import streamlit as st
import PyPDF2
from PIL import Image
# Importamos apenas o necessário do config e do agente
from agente import analisar_com_rag

# 1. Configuração da página da interface
st.set_page_config(page_title="Bússola De Crédito", page_icon="🧭", layout="centered")

st.title("🧭 Bússola De Crédito")
st.markdown("Seu amigo experiente para traduzir contratos e te ajudar a sair das dívidas.")


if __name__ == "__main__":
    print("Iniciando o processamento dos documentos regulatórios...")


from vector_store import criar_base_conhecimento
criar_base_conhecimento()
print("Base de conhecimento 'Regulatory' criada com sucesso!")


# 2. Área lateral para upload de documentos
with st.sidebar:
    st.header("Análise de Contrato e Faturas")
    st.write("Faça o upload do seu contrato bancário em PDF ou envie fotos das faturas.")
    
    uploaded_files = st.file_uploader(
        "Envie seus arquivos (PDF, PNG, JPG)", 
        type=["pdf", "png", "jpg", "jpeg"], 
        accept_multiple_files=True
    )
    
    texto_contrato = ""
    imagens_contrato = []
    
    if uploaded_files:
        for file in uploaded_files:
            try:
                if file.name.lower().endswith('.pdf'):
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        texto_extraid = page.extract_text()
                        if texto_extraid:
                            texto_contrato += texto_extraid + "\n"
                
                elif file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img = Image.open(file)
                    imagens_contrato.append(img)
                    st.image(img, caption=f"Imagem: {file.name}", use_column_width=True)
                    
            except Exception as e:
                st.error(f"Erro ao ler o arquivo {file.name}: {e}")
                
        if texto_contrato or imagens_contrato:
            st.success("Documentos prontos para análise!")

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
            resposta = analisar_com_rag(texto_contrato, imagens_contrato, prompt)
            st.markdown(resposta)
            
    st.session_state.messages.append({"role": "assistant", "content": resposta})