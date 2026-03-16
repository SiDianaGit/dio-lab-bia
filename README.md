# 🧭 Bússola de Crédito

O **Bússola de Crédito** é um agente de Inteligência Artificial com base em RAG (Retrieval-Augmented Generation) criado para auxiliar os brasileiros na análise de dívidas financeiras. Ele atua como um assistente empático e didático, capaz de traduzir o jargão financeiro ("economês") de contratos bancários, ajudando o usuário a entender suas opções e encontrar o melhor caminho para sair das dívidas.

> **Aviso Legal:** O Bússola atua como um assistente informativo. Ele não executa pagamentos, não substitui assessoria jurídica formal e não garante aprovação de acordos de crédito.

## ✨ Funcionalidades

* **Análise de Documentos:** Suporte para upload e leitura de contratos e faturas nos formatos `PDF`, `TXT`, `DOC` e `DOCX`.
* **Chat Conversacional:** Interface intuitiva em formato de chat para interagir com os documentos enviados e tirar dúvidas sobre taxas e juros.
* **Busca em Base Regulatória:** Utiliza um banco de dados vetorial (FAISS) para consultar leis e regulamentações financeiras aplicáveis ao contexto do usuário.
* **Cálculo Transparente:** Capacidade de calcular juros compostos de forma educativa, explicando o passo a passo da evolução da dívida.

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando as seguintes ferramentas e bibliotecas:

* **[Streamlit](https://streamlit.io/):** Framework para a construção da interface web interativa.
* **[LangChain](https://python.langchain.com/):** Orquestração dos fluxos de LLM e integração com a base de conhecimento.
* **Google Generative AI Embeddings:** Geração de embeddings (`models/gemini-embedding-001`) para a base de documentos.
* **Groq:** Provedor do LLM principal responsável por interpretar e responder às dúvidas.
* **[FAISS](https://github.com/facebookresearch/faiss):** Banco de dados vetorial otimizado para busca de similaridade local.
* **LLM Google gemini-2.5-flash** Modelo para extração de texto estruturado dos arquivos PDF e imagens (OCR) enviados pelo usuário.

## 📁 Estrutura do Projeto

```text
├── data/
│   ├── Regulatory/             # Arquivos PDF com regulamentações (ex: Leis, Resoluções do BC)
│   └── produtos_credito.json   # Dados estruturados de produtos financeiros e taxas de mercado
├── docs/                       # Documentação do projeto e roteiro do Pitch
├── faiss_regulatory_index/     # Pasta gerada automaticamente contendo o banco vetorial FAISS
├── src/
│   ├── app.py                  # Ponto de entrada da aplicação e interface Streamlit
│   ├── agente.py               # Lógica do agente Bússola, prompt de sistema e integração LLM
│   ├── config.py               # Configurações globais e instâncias de modelos
│   └── vector_store.py         # Scripts de ingestão de dados e criação dos embeddings
├── requirements.txt            # Dependências do projeto
└── README.md                   # Esta documentação
```
# Assets
Esta pasta é destinada a recursos visuais do projeto:

* Diagramas de arquitetura 
    - diagrama_arquitetura_solução.xml e (.pdf)
* Screenshots da aplicação
    - Testes da aplicação
    - Métricas



## 🚀 Como Executar Localmente

### Pré-requisitos
* Python 3.9+ instalado.
* Chaves de API do **Google** (para embeddings) e do **Groq** (para o LLM).

### Passos para Instalação

1. **Clone o repositório:**
   ```bash
   git clone <url-do-seu-repositorio>
   cd dio-lab-bia
    ```

2. **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    # No Windows:
    venv\Scripts\activate
    # No Linux/Mac:
    source venv/bin/activate
    ```

3. **Instale as dependências:**
    ```bash
    pip install -r requirements.txt  
    ``` 

4. **Configure as Variáveis de Ambiente:**
   Crie um arquivo `.env` na raiz do projeto e adicione suas chaves: 
    ```
    GEMINI_API_KEY=sua_chave_do_google_aqui
    GROQ_API_KEY=sua_chave_do_groq_aqui
    ```

5. **Inicie a aplicação:**
    ```bash
    streamlit run src/app.py
    ```

    *A interface abrirá automaticamente no seu navegador padrão (geralmente em http://localhost:8501).*

## 🧠 Como o RAG Funciona no Projeto

1. **Ingestão:** Ao iniciar o sistema, a função `criar_base_conhecimento` lê os PDFs regulatórios na pasta `data/Regulatory/` e o catálogo `produtos_credito.json`, gerando chunks de texto.

2. **Vetorização:** Esses textos são transformados em *embeddings* pela API do Google e armazenados localmente no FAISS.

3. **Recuperação e Geração:** Quando o usuário faz uma pergunta, o app busca o contexto mais relevante nas leis (recuperação) e injeta essa informação no *prompt* junto com o texto do contrato enviado pelo usuário. O LLM (Groq) usa essa combinação para elaborar uma resposta altamente embasada.


## 🔮 Melhorias Futuras

O Bússola de Crédito é um projeto em contínua evolução. Para tornar as análises ainda mais precisas e conectadas com a realidade econômica do momento, as seguintes implementações estão planejadas para o futuro:

* **Busca Ampla na Internet:** Integração de ferramentas de pesquisa web (Web Search Agents) para permitir que o assistente busque contextos adicionais, notícias financeiras e orientações gerais que vão além da sua base de dados local.
* **Integração com APIs Oficiais:** Conexão direta com APIs abertas do **Banco Central do Brasil (BCB)** (como a API do Sistema Gerenciador de Séries Temporais - SGS) e de outras **instituições financeiras** (Open Finance). Isso permitirá que o agente consulte taxas de juros atualizadas em tempo real, novos tetos regulatórios e condições de mercado atuais para fundamentar ainda mais os seus cálculos e conselhos.
* **Busca de Dívidas no Mercado:** Conexão direta com APIs fechadas (sob concentimento) do **Banco Central do Brasil (BCB/BACEN)**, **Serasa** e outros para composição de cálculos personalizados de endividamento por cliente atualizados, atentando-se a Lei Geral de Proteção de Dados (**LGPD**) para tratamento de  **dados pessoais sensíveis**. Implementar mascaramento dados pessoais sensíveis e anonimizar as informações em bases de dados mesmo que temporárias em memória, prompts de LLM's, e traces de observabilidade.

