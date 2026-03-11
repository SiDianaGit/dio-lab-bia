import streamlit as st
import PyPDF2
from PIL import Image
from agente import analisar_com_rag
from vector_store import criar_base_conhecimento
import docx

@st.cache_resource
def inicializar_banco_vetorial():
    """Executa a criação da base de conhecimento apenas uma vez."""
    print("Iniciando o processamento dos documentos regulatórios...")
    criar_base_conhecimento()
    print("Base de conhecimento 'Regulatory' criada com sucesso!")
    return True

# O Streamlit vai rodar isso, guardar o resultado no cache e 
# pular a execução nas próximas vezes.
base_pronta = inicializar_banco_vetorial()


# 1. Configuração da página da interface
st.set_page_config(page_title="Bússola De Crédito", page_icon="🧭", layout="centered")
st.title("🧭 Bússola De Crédito")
st.markdown("Seu amigo experiente para traduzir contratos e te ajudar a sair das dívidas.")


if __name__ == "__main__":
    # 2. Área lateral para upload de documentos
    with st.sidebar:
        st.header("Análise de Contrato e Faturas")
        st.write("Faça o upload do seu contrato bancário ou faturas em PDF, TXT ou Word.")
        
        uploaded_files = st.file_uploader(
            "Envie seus arquivos", 
            type=["pdf", "txt", "doc", "docx"], 
            accept_multiple_files=True
        )
        
        texto_contrato = ""
        
        if uploaded_files:
            for file in uploaded_files:
                nome_arquivo = file.name.lower()
                try:
                    # 2. Lógica para PDF
                    if nome_arquivo.endswith('.pdf'):
                        reader = PyPDF2.PdfReader(file)
                        for page in reader.pages:
                            texto_extraid = page.extract_text()
                            if texto_extraid:
                                texto_contrato += texto_extraid + "\n"
                    
                    # 3. Lógica para TXT
                    elif nome_arquivo.endswith('.txt'):
                        # Decodifica o binário para string
                        texto_contrato += file.read().decode("utf-8") + "\n"
                    
                    # 4. Lógica para DOCX
                    elif nome_arquivo.endswith('.docx'):
                        doc = docx.Document(file)
                        for para in doc.paragraphs:
                            texto_contrato += para.text + "\n"
                    
                    # Para arquivos .doc (antigos), a leitura é complexa em Python puro.
                    # Avisar o usuário para converter para .docx. 
                    elif nome_arquivo.endswith('.doc'):
                        st.warning(f"O arquivo {file.name} está em formato .doc antigo. Tente salvar como .docx para melhor leitura.")

                except Exception as e:
                    st.error(f"Erro ao ler o arquivo {file.name}: {e}")
                    
            if texto_contrato:
                st.success("Documentos lidos com sucesso!")

    # 3. Gerenciamento de estado do chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        saudacao_inicial = (
            "Olá! Sou o Bússola. Estou aqui para te ajudar a traduzir esses contratos complicados "
            "e encontrar o melhor caminho para sair das dívidas. Se tiver um contrato ou print, "
            "suba na barra lateral que eu leio para você agora!"
        )
        st.session_state.messages.append({"role": "assistant", "content": saudacao_inicial})

    # Exibe o histórico
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 4. Caixa de entrada e Processamento
    if prompt := st.chat_input("Pergunte sobre sua dívida ou juros..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("O Bússola está analisando..."):
                # A lógica de decidir se aceita imagem ou texto está dentro do agente.py
                resposta = analisar_com_rag(texto_contrato, [], prompt)
                st.markdown(resposta)
                
        st.session_state.messages.append({"role": "assistant", "content": resposta})