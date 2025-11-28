import os
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate

# ===== 1. Configuração =====
# Preencher com suas credenciais
OPENAI_API_KEY = "VaiBotarAChaveDaOpenAiAqui"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "AquiEhASenhaDoNeo4j"

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
    api_key=OPENAI_API_KEY,
)

# Conecta ao Neo4j
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USER,
    password=NEO4J_PASSWORD,
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
Use SOMENTE a informação do contexto para responder à pergunta.
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

# ===== 3. Cria a cadeia GraphCypherQAChain =====
chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    cypher_prompt=CYPHER_GENERATION_PROMPT,
    qa_prompt=QA_PROMPT,
    validate_cypher=True,
    verbose=True,
    return_intermediate_steps=True,
)

print("Cadeia GraphCypherQAChain criada.")

# ===== 4. Perguntas do Exame =====
questions = [
    "Quem são os funcionários da BigCo?",
    "Quais são os livros que os funcionários da BigCo gostam?",
    "Quem são os autores dos livros que os funcionários da BigCo gostam?",
    "Quem gosta de livro da categoria Databases?"
]

for q in questions:
    print("\n\nPergunta:", q)
    result = chain.invoke({"query": q})

    # Mostrar query Cypher gerada, contexto e resposta final
    print("\n> Query Cypher gerada:")
    if result.get("intermediate_steps"):
        step0 = result["intermediate_steps"][0]
        print(step0.get("query", "Query não encontrada."))
        print("\n> Contexto retornado do grafo:")
        print(step0.get("context", "Contexto não encontrado."))
    else:
        print("Sem passos intermediários.")

    print("\n> Resposta final:")
    print(result["result"])
