import os
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_groq import ChatGroq


# Carrega as variáveis do arquivo .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
def configure_api():
    """Configura a chave da API do Gemini."""
    if not GEMINI_API_KEY:
        raise ValueError("A chave GEMINI_API_KEY não foi encontrada no arquivo .env")
    genai.configure(api_key=GEMINI_API_KEY)


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
def get_groq_llm():
    """
    Configura e retorna o modelo ChatGroq com os parâmetros de segurança
    definidos na documentação do Bússola de Crédito.
    """
    if not GROQ_API_KEY:
        raise ValueError("A chave GROQ_API_KEY não foi encontrada.")
    
    llm = ChatGroq(
        model='llama-3.3-70b-versatile', # Modelo com alta capacidade de raciocínio e ferramentas
        temperature=0.0,  # Baixa temperatura para evitar alucinações. Temperatura zero para máxima precisão em chamadas de função
        groq_api_key=GROQ_API_KEY, 
        max_retries=2
    )
    return llm
