# Chat com Grafo de Conhecimento usando LLM Local

Grupo: Hyuri Fragoso, Pedro Ulisses, Iago Jacob, Welberson Franklin, Matheus Militão.

Disciplina: Técnicas de Banco de Dados (CSI-30)

Este projeto demonstra como utilizar a biblioteca LangChain para conectar um Modelo de Linguagem Grande (LLM), rodando localmente através do LM Studio, a um banco de dados de grafo Neo4j. O sistema é capaz de responder a perguntas em linguagem natural, convertendo-as em queries Cypher, executando-as no grafo e formulando uma resposta final com base nos resultados.

## Arquivos do Projeto

- **`main.py`**: Script principal que executa a lógica de consulta.
- **`config.py` / `config_pedro.py`**: Arquivos para armazenar todas as configurações, como credenciais, perguntas e parâmetros do modelo.
- **`requirements.txt`**: Lista as bibliotecas Python necessárias para o projeto.
- **`log_*.txt`**: Arquivos de log gerados após a execução, contendo os resultados e métricas.
- **`README.md`**: Documentação do projeto.
- **`enunciado_exame.pdf`**: Documento que descreve os objetivos do projeto (Forma 2).
- **`scripts_geração_bd.pdf`**: Documento que contém um exemplo de script de criação e população de um grafo de conhecimento, assim como algumas perguntas, em liguagem natural, mas com um tratamento de queries no cypher.

## Funcionalidades

- **Geração de Query Cypher:** Converte perguntas em português para queries Cypher.
- **Integração com LLM Local:** Utiliza um servidor local do LM Studio, permitindo o uso de diversos modelos de código aberto sem custo de API.
- **Consulta ao Grafo:** Conecta-se a um banco de dados Neo4j para extrair informações.
- **Geração de Resposta:** Formula uma resposta em linguagem natural com base no contexto retornado pelo grafo.
- **Logging Detalhado:** Gera um arquivo de log completo com especificações da máquina, configurações, perguntas, queries geradas, contexto, respostas e tempos de execução.
- **Configuração Flexível:** Permite a fácil troca de configurações (credenciais, modelo, perguntas) através de arquivos de configuração dedicados.

## Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:

- **Python 3.9+**
- **Neo4j Desktop:** Com um banco de dados criado e em execução.
- **LM Studio:** Com um modelo de LLM compatível baixado (ex: `qwen/qwen2-7b-instruct-gguf`).

---

## Guia de Instalação e Execução

Siga os passos abaixo para configurar e rodar o projeto.

### 1. Crie um Ambiente Virtual (venv)

É uma boa prática isolar as dependências do projeto. No diretório do projeto, execute:

**No Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**No macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instale as Dependências

Com o ambiente virtual ativado, instale todas as bibliotecas necessárias a partir do arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Configure o Ambiente

**Neo4j Desktop:**
1.  Abra o Neo4j Desktop e inicie seu banco de dados.
2.  **Instale o Plugin APOC:** Vá em `Plugins` no seu banco de dados e instale o plugin `APOC`. Isso é crucial para que o LangChain possa inspecionar o esquema do grafo.
3.  **Popule o Banco de Dados:** Certifique-se de que seu banco de dados contenha os dados (nós e relacionamentos) que serão consultados.

**LM Studio:**
1.  Abra o LM Studio.
2.  Baixe um modelo de sua preferência (o `qwen/qwen2-7b-instruct-gguf` é uma boa opção).
3.  Vá para a aba **Local Server** (`<->`), selecione o modelo que você baixou e clique em **Start Server**.

### 4. Crie seu Arquivo de Configuração

Você pode criar seus próprios arquivos de configuração sem alterar o código principal.

1.  **Copie o arquivo `config_pedro.py`** e renomeie-o para algo como `meu_config.py`.

2.  **Edite o `meu_config.py`** com suas próprias informações:
    ```python
    # Em meu_config.py

    # Altere a senha do seu banco de dados Neo4j
    NEO4J_PASSWORD = "sua-senha-super-secreta"

    # Nome do arquivo de log que será gerado
    LOG_FILENAME = "log_meu_teste.txt"

    # Especifique o modelo que você está usando no LM Studio
    LLM_MODEL_NAME = "qwen/qwen2-7b-instruct-gguf"

    # Adicione ou altere as perguntas que deseja fazer
    QUESTIONS = [
        "Qual o nome de todos os funcionários?",
        "Quais livros foram escritos por Martin?"
    ]
    
    # ... ajuste outras configurações se necessário.
    ```

### 5. Execute o Programa

1.  Abra o arquivo `main.py`.
2.  No topo do arquivo, altere a variável `CONFIG_MODULE_NAME` para o nome do seu novo arquivo de configuração (sem o `.py`).

    ```python
    # Em main.py
    CONFIG_MODULE_NAME = "meu_config"
    ```

3.  Execute o script principal no seu terminal:
    ```bash
    python main.py
    ```

### 6. Verifique a Saída

O programa irá imprimir as perguntas e respostas no console.

Ao final da execução, um arquivo de log (ex: `log_meu_teste.txt`) será criado no diretório. Este arquivo contém um registro detalhado de toda a execução, incluindo:
- Especificações da máquina.
- Configurações do modelo.
- Cada pergunta feita.
- A query Cypher gerada pela IA e o tempo que levou.
- O contexto retornado pelo banco de dados.
- A resposta final da IA e o tempo que levou.
- O tempo total de processamento.

---

