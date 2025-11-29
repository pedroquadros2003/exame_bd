# ===== 1. Configuração do Banco de Dados Neo4j =====
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"

# ===== 2. Configuração de Log e Ambiente =====
LOG_FILENAME = "log_pedro3.txt"

# Versão do LM Studio utilizada na execução. Atualize se necessário.
LM_STUDIO_VERSION = "0.3.32"

# Especificações da máquina onde foram realizados os testes.
pc_specs = {
    "brand": "Lenovo",
    "model": "LOQ 83EU0000BR",
    "cpu": {
        "model": "Intel Core i5-12450H",
        "generation": 12,
        "cores_threads": None,
        "base_clock": None,
        "turbo_clock": None
    },
    "ram_gb": 8,
    "storage": {
        "type": "SSD",
        "size_gb": 512
    },
    "gpu": {
        "model": "NVIDIA GeForce RTX 2050",
        "vram_gb": 4
    },
    "os": "Windows 11 Home"
}

# ===== 3. Configuração do LLM (Language Model) =====
LLM_MODEL_NAME = "qwen/qwen3-8b"
LLM_API_BASE = "http://127.0.0.1:1234/v1"
LLM_API_KEY = "not-required"
LLM_TEMPERATURE = 0

# ===== 4. Perguntas para Execução =====
QUESTIONS = [
    "Quem são os funcionários da BigCo?",
    "Quais são os livros que os funcionários da BigCo gostam?",
    "Quem são os autores dos livros que os funcionários da BigCo gostam?",
    "Quem gosta de livro da categoria Databases?"
]
