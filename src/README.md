# Código da Aplicação

Esta pasta contém o código do seu agente financeiro.

## Estrutura

```
src/
├── app.py              # Aplicação principal (Streamlit/Gradio)
├── agente.py           # Lógica do agente
├── config.py           # Configurações (API keys, etc.)
└── vector_store.py     # Lógica para carregamento da base de conhecimento "in memory"
data/
├── Regulatory/
    ├── DesenrolaBrasil.pdf
    ├── L14181-LeiDoSuperendividamento2021.pdf
    └── ResoluçãoCMN_5265de28-11-2025.pdf
└── produtos_credito.json


└── requirements.txt    # Dependências
```

## Exemplo de requirements.txt

```
streamlit
openai
python-dotenv
```

## Como Rodar

```bash
# Instalar dependências
# Execute estes passos na ordem:

# Criar o ambiente:
python -m venv venv

#Ativar o ambiente:
.\venv\Scripts\activate

#Instalar as dependências agora no ambiente limpo:
pip install -r requirements.txt


#python -m pip install --upgrade google-generativeai
#python -m pip install -U langchain-google-genai
#python -m pip uninstall langchain-huggingface sentence-transformers torch -y
#python -m pip cache purge


#Verifique se a instalação funcionou
#Para ter certeza de que você está na versão correta (deve ser 0.3.0 ou superior), digite:

#pip show google-generativeai

# Rodar a aplicação
streamlit run src/app.py

python -m streamlit run src/app.py


#Para encerrar a sessão e limpar a memória

deactivate

Remove-Item -Recurse -Force venv

pip uninstall torch torchvision torchaudio
pip uninstall sentence-transformers
