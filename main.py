import os
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from importlib import import_module
import time


# --- PONTO DE CONFIGURAÇÃO PRINCIPAL ---
# Para usar um arquivo de configuração diferente (ex: 'config_pessoal.py'),
# altere o nome do módulo na linha abaixo (sem o '.py').
CONFIG_MODULE_NAME = "config_pedro"
# -----------------------------------------

try:
    config = import_module(CONFIG_MODULE_NAME)
except ImportError:
    print(f"ERRO: O arquivo de configuração '{CONFIG_MODULE_NAME}.py' não foi encontrado. Verifique o nome e o local do arquivo.")
    exit()

llm = ChatOpenAI(
    # Modelo carregado via LM Studio. O nome do modelo aqui é apenas informativo.
    model=config.LLM_MODEL_NAME,
    openai_api_base=config.LLM_API_BASE,
    openai_api_key=config.LLM_API_KEY,
    temperature=config.LLM_TEMPERATURE,
)

# Conecta ao Neo4j
graph = Neo4jGraph(
    url=config.NEO4J_URI,
    username=config.NEO4J_USER,
    password=config.NEO4J_PASSWORD,
)

print("Conectado ao Neo4j com sucesso!")

# ===== 2. Prompts personalizados =====
CYPHER_GENERATION_TEMPLATE = """
Você é um expert em Neo4j e Cypher. Dada uma pergunta em linguagem natural em português e
um esquema de grafo, gere uma query Cypher para responder à pergunta.

Regras importantes:
- NÃO responda à pergunta, apenas gere a query.
- NÃO use exemplos, apenas o que é necessário para a pergunta.
- NÃO coloque a query dentro de blocos de markdown.
- Retorne apenas a query Cypher final.
- As relações são arestas direcionadas, CUIDADO para não errar o sentido delas.

Esquema do grafo:
{schema}

Pergunta: {question}
Query Cypher:
"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE,
)

QA_TEMPLATE = """
Você é um assistente que responde perguntas com base em um contexto fornecido.
O contexto é o resultado de uma query Cypher em um grafo de conhecimento.
Use SOMENTE a informação do contexto para responder à pergunta, mas observe que 
o contexto não vem com todas as informações, você precisa interpretá-las a partir da pergunta.
Se a informação não estiver no contexto, diga que não encontrou a resposta no grafo.

Contexto:
{context}

Pergunta: {question}
Resposta útil (em português):
"""

QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=QA_TEMPLATE,
)

# Função para extrair apenas a query Cypher da saída do LLM
def extract_cypher(text: str) -> str:
    """Extrai a query Cypher de uma string que pode conter tags <think>."""
    # Encontra a última ocorrência de "MATCH" para pegar a query real
    match_pos = text.rfind("MATCH")
    if match_pos != -1:
        return text[match_pos:]
    return text # Retorna o texto original se "MATCH" não for encontrado

# ===== 3. Cria a cadeia GraphCypherQAChain =====
chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=llm | StrOutputParser() | extract_cypher, # Adiciona o parser e a função de extração
    qa_llm=llm,
    cypher_prompt=CYPHER_GENERATION_PROMPT,
    qa_prompt=QA_PROMPT,
    validate_cypher=True,
    verbose=True,
    return_intermediate_steps=True,
    allow_dangerous_requests=True,
)

print("Cadeia GraphCypherQAChain criada.")

with open(config.LOG_FILENAME, "w", encoding="utf-8") as log_file:
    # Função auxiliar para printar e salvar no log
    def log_and_print(message):
        print(message)
        log_file.write(message + "\n")

    # Log das informações da máquina e ambiente
    log_and_print("===== Informações da Máquina e Ambiente =====")
    log_and_print(f"Marca: {config.pc_specs['brand']}")
    log_and_print(f"Modelo: {config.pc_specs['model']}")
    log_and_print(f"OS: {config.pc_specs['os']}")
    log_and_print(f"CPU: {config.pc_specs['cpu']['model']}")
    log_and_print(f"RAM: {config.pc_specs['ram_gb']} GB")
    log_and_print(f"Armazenamento: {config.pc_specs['storage']['size_gb']} GB {config.pc_specs['storage']['type']}")
    log_and_print(f"GPU: {config.pc_specs['gpu']['model']} com {config.pc_specs['gpu']['vram_gb']} GB VRAM")
    log_and_print(f"Versão do LM Studio: {config.LM_STUDIO_VERSION}")
    log_and_print("="*40)

    # Log das configurações do modelo
    log_and_print("===== Configurações da Execução =====")
    model_info = f"Modelo LLM: {llm.model_name}\nTemperatura: {llm.temperature}"
    if hasattr(llm, 'openai_api_base') and llm.openai_api_base and 'localhost' in llm.openai_api_base:
        model_info += f"\nEndpoint: {llm.openai_api_base} (Modelo Local)"
    else:
        model_info += "\nEndpoint: OpenAI API"
    log_and_print(model_info)
    log_and_print("="*40)

    total_execution_time = 0.0

    # Itera sobre as perguntas
    for q in config.QUESTIONS:
        log_and_print(f"\n\nPergunta: {q}")

        # Etapa 1: Geração da Query Cypher (com medição de tempo)
        start_time_cypher = time.perf_counter()
        generated_query = chain.cypher_generation_chain.invoke({"question": q, "schema": graph.schema})
        end_time_cypher = time.perf_counter()
        cypher_gen_time = end_time_cypher - start_time_cypher
        total_execution_time += cypher_gen_time
        log_and_print(f"\n> Query Cypher gerada (em {cypher_gen_time:.2f}s):\n{generated_query}")
        
        # Etapa 2: Execução da Query no Grafo
        raw_context = graph.query(generated_query)
        context_for_log = str(raw_context)
        
        if context_for_log == "[]":
            context_for_log = "[] (A query retornou uma lista vazia)"
        log_and_print(f"\n> Contexto retornado do grafo:\n{context_for_log}")

        # Etapa 3: Geração da Resposta Final (com medição de tempo)
        start_time_qa = time.perf_counter()
        final_answer = chain.qa_chain.invoke({"question": q, "context": raw_context})
        end_time_qa = time.perf_counter()
        qa_gen_time = end_time_qa - start_time_qa
        total_execution_time += qa_gen_time
        log_and_print(f"\n> Resposta final (gerada em {qa_gen_time:.2f}s):\n{final_answer}")

    # Log do tempo total de execução
    log_and_print("\n" + "="*40)
    log_and_print(f"Tempo total de processamento da IA: {total_execution_time:.2f}s")
    log_and_print("="*40)

print(f"\nExecução finalizada. Log completo salvo em '{config.LOG_FILENAME}'.")
