from langchain_core.messages import HumanMessage, SystemMessage
from config import get_groq_llm
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import re

# O prompt baseia-se estritamente nas regras de segurança e persona da documentação.
SYSTEM_PROMPT = """Você é o Bússola, um assistente de análise de dívidas. Sua prioridade máxima é a precisão factual. Você atua como um amigo experiente do mercado financeiro que traduz o "economês" para ajudar o usuário.
Seu tom de voz deve ser Empático, Direto/Lúcido, Didático e Capacitador. Não julgue o gasto passado do usuário; foque na solução. Sempre que precisar calcular o valor final de uma dívida, use a fórmula de juros compostos e descreva o passo a passo para o usuário.
Sempre cite a fonte da informação (ex: 'Segundo o arquivo [nome], página [X]...') e utilize os metadados fornecidos no contexto.

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

LIMITAÇÃO DE ESCOPO:
Você é estritamente um assistente de análise financeira e de contratos de crédito.
Se o usuário perguntar sobre assuntos não relacionados (como culinária, esportes, política, ou códigos de programação não relacionados ao projeto), recuse-se a responder.
Use EXATAMENTE esta frase para recusar: "Desculpe, meu foco é te ajudar a encontrar o melhor caminho para suas dívidas e contratos de crédito. Não consigo navegar por outros assuntos.
"""

def get_bussola_model():
    """Recupera o modelo Groq configurado no config.py."""
    return get_groq_llm()


def buscar_legislacao_relevante(pergunta):
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    db = FAISS.load_local("faiss_regulatory_index", embeddings, allow_dangerous_deserialization=True)
    # Busca os 3 trechos mais importantes (ex: sobre INSS ou Desenrola)
    docs = db.similarity_search(pergunta, k=3)
    return "\n".join([d.page_content for d in docs])


def aplicar_guardrails(resposta_llm: str) -> str:
    """
    Camada de segurança (Guardrails) que intercepta a resposta do LLM 
    para garantir formatação correta e isenção de responsabilidade.
    """
    resposta_segura = resposta_llm

    # 1. REGEX: Padronização de Valores Monetários
    # Corrige casos em que o LLM gera "BRL 1500", "$ 1500" ou "US$ 1500" para "R$ 1500"
    padrao_moeda = r'(?i)(?:BRL\s+|US\$\s*|(?<![Rr])\$\s*)(\d+[.,\d]*)'
    resposta_segura = re.sub(padrao_moeda, r'R$ \1', resposta_segura)

    # 2. FILTRO DE CONSELHOS JURÍDICOS E DISCRICIONÁRIOS
    # Se o LLM identificar problemas no contrato, precisamos adicionar o disclaimer legal
    termos_risco_juridico = [
        "abusivo", "ilegal", "irregular", "fraude", "procon", 
        "processo", "advogado", "justiça", "crime", "inconstitucional"
    ]
    
    # Verifica se alguma palavra de risco está na resposta (ignorando maiúsculas/minúsculas)
    contem_risco = any(termo in resposta_segura.lower() for termo in termos_risco_juridico)
    
    # Texto do Disclaimer Obrigatório (conforme diretrizes de agentes financeiros)
    disclaimer = (
        "\n\n⚠️ **Aviso Legal:** O Bússola atua como uma ferramenta de educação financeira. "
        "Esta análise não substitui o aconselhamento oficial de um advogado ou a orientação "
        "de órgãos de defesa do consumidor, como o Procon."
    )
    
    # Adiciona o disclaimer apenas se o contexto exigir e se já não foi adicionado
    if contem_risco and "Aviso Legal" not in resposta_segura:
        resposta_segura += disclaimer

    return resposta_segura


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
    prompt_instrucao = (
        f"{SYSTEM_PROMPT}\n\n"
        "INSTRUÇÃO DE SEGURANÇA: Responda APENAS com base nos documentos abaixo. "
        "Se a informação não estiver neles, use a frase de recusa padrão da documentação.\n\n"
        f"BASE LEGAL (Regulatory):\n{contexto_lei}\n\n"
        f"DADOS DO CONTRATO DO CLIENTE:\n{texto_documento}\n"
    )
    
    # 4. ENVIO PARA O MODELO
    messages = [
        SystemMessage(content=prompt_instrucao),
        HumanMessage(content=mensagem_usuario)
    ]

    # Chamada do modelo
    try:
        #resposta = llm.invoke(messages)
        # - O modelo agora decide se chama a função ou responde diretamente
        resposta = llm.invoke(messages)

        # ---> APLICA A CAMADA DE SEGURANÇA (GUARDRAILS) <---
        texto_verificado = aplicar_guardrails(resposta.content)

        return texto_verificado
    
    except Exception as e:
        return f"Erro na análise: {str(e)}"
    
