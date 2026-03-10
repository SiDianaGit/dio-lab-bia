from langchain_core.messages import HumanMessage, SystemMessage
from config import get_groq_llm
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# O prompt baseia-se estritamente nas regras de segurança e persona da documentação.
SYSTEM_PROMPT = """Você é o Bússola, um assistente de análise de dívidas. Sua prioridade máxima é a precisão factual. Você atua como um amigo experiente do mercado financeiro que traduz o "economês" para ajudar o usuário.
Seu tom de voz deve ser Empático, Direto/Lúcido, Didático e Capacitador. Não julgue o gasto passado do usuário; foque na solução. Sempre que precisar calcular o valor final de uma dívida, use a fórmula de juros compostos e descreva o passo a passo para o usuário.

VERIFICAÇÃO: Antes de afirmar uma taxa de juros, localize o valor numérico exato no documento.
ISENÇÃO: Sempre que identificar uma possível irregularidade, use: 'Isso apresenta indícios de [problema], recomendo validar com um especialista'.
PROIBIÇÃO: Nunca utilize as palavras 'Garantia', 'Certeza Absoluta' ou 'Ganho Certo'.
CONTEXTO: Se o usuário perguntar algo fora do documento enviado e você não tiver acesso à base de dados atualizada do Banco Central para aquele item, responda: 'Não encontrei essa informação no seu documento e não tenho acesso aos dados externos desse banco no momento'.

REGRAS DE LIMITAÇÃO (O QUE VOCÊ NÃO PODE FAZER):
1. Não toma decisões nem executa pagamentos.
2. Não substitui o advogado (não dá assessoria jurídica formal).
3. Não garante aprovação de crédito ou acordos com o banco.
4. Não faz previsões de mercado "certas".
5. Não altera dados no sistema do banco, Serasa, Boa Vista ou SPC.
"""

def get_bussola_model():
    """Recupera o modelo Groq configurado no config.py."""
    return get_groq_llm()

def calcular_juros_compostos(principal, taxa_mensal, meses):
    """
    Ferramenta de validação para garantir que o Bússola não alucine 
    em cálculos de dívida acumulada.
    """
    # Fórmula: M = P * (1 + i)^n
    montante = principal * (1 + taxa_mensal)**meses
    return round(montante, 2)

def buscar_legislacao_relevante(pergunta):
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    db = FAISS.load_local("faiss_regulatory_index", embeddings, allow_dangerous_deserialization=True)
    # Busca os 3 trechos mais importantes (ex: sobre INSS ou Desenrola)
    docs = db.similarity_search(pergunta, k=3)
    return "\n".join([d.page_content for d in docs])

def analisar_com_rag(texto_documento, imagens_documento, mensagem_usuario):
    """
    Função de análise utilizando LangChain e Groq.
    Nota: Modelos Llama via Groq focam em texto. Se imagens forem enviadas,
    o sistema avisará sobre a necessidade de OCR ou PDF.
    """
    # 1. Recuperamos o LLM configurado no Groq
    llm = get_bussola_model()
    
    # 2. BUSCA NO VECTOR_DB: Onde a mágica acontece
    # Buscamos nas leis (Regulatory) o que faz sentido para a dúvida atual
    contexto_lei = buscar_legislacao_relevante(mensagem_usuario)
    
    # 3. MONTAGEM DO CONTEXTO PARA O LLM
    # Passamos o texto da lei + o contrato do cliente para o modelo
    prompt_completo = (
        f"BASE LEGAL (Regulatory):\n{contexto_lei}\n\n"
        f"DADOS DO CONTRATO DO CLIENTE:\n{texto_documento}\n\n"
        f"PERGUNTA: {mensagem_usuario}"
    )
    
    # 4. ENVIO PARA O MODELO
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt_completo)
    ]

    # Chamada do modelo
    try:
        resposta = llm.invoke(messages)
        return resposta.content
    except Exception as e:
        return f"Erro na análise: {str(e)}"