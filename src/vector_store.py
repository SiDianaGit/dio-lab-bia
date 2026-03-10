
import json
import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def criar_base_conhecimento():
    # 1. Carregar PDFs (Informações Regulatórias)
    # Tenta carregar os PDFs; se a pasta não existir, inicia lista vazia
    docs_pdf = []
    if os.path.exists("data/Regulatory/"):
        loader = PyPDFDirectoryLoader("data/Regulatory/")
        docs_pdf = loader.load()
    
    # Divide os PDFs em pedaços menores
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    final_docs = text_splitter.split_documents(docs_pdf)

    # 2. Carregar e Processar o JSON (Produtos de Crédito)
    with open("data/produtos_credito.json", "r", encoding="utf-8") as f:
        dados_json = json.load(f)
        
    mercado = dados_json.get("mercado", "Brasil")
    data_ref = dados_json.get("data_referencia", "N/A")
    moeda = dados_json.get("moeda", "BRL")

    for item in dados_json.get("produtos_credito", []):
        # Construímos uma "Ficha Técnica" detalhada para cada produto
        linhas = [
            f"PRODUTO: {item.get('nome')} (ID: {item.get('id')})",
            f"Contexto: Mercado {mercado}, Moeda {moeda}, Ref: {data_ref}",
            f"Descrição: {item.get('descricao')}"
        ]

        # Info de Taxas Gerais
        taxa_g = item.get("taxa_juros_remuneratorios_geral", {})
        detalhe_taxa = f"Regra de Juros: {taxa_g.get('tipo', '')} ({taxa_g.get('unidade', '')})"
        if "teto_regulatorio" in taxa_g: detalhe_taxa += f" | Teto: {taxa_g['teto_regulatorio']}%"
        if "indexador" in taxa_g: detalhe_taxa += f" | Indexador: {taxa_g['indexador']}"
        if "observacao" in taxa_g: detalhe_taxa += f" | Nota: {taxa_g['observacao']}"
        linhas.append(detalhe_taxa)

        # Instituições Financeiras
        insts = item.get("instituicoes_financeiras", [])
        if insts:
            linhas.append("Taxas por Instituição:")
            for inst in insts:
                # Trata campos de taxa mensal ou anual dinamicamente
                valor_taxa = inst.get("taxa_juros_mensal_media") or inst.get("taxa_juros_anual_media")
                periodo = "a.m." if "taxa_juros_mensal_media" in inst else "a.a."
                linhas.append(f" - {inst['nome']}: {valor_taxa}% {periodo} (Disponibilidade: {inst['disponibilidade']})")

        # Tarifas e CET
        tarifas = item.get("tarifas_cet", [])
        if tarifas:
            linhas.append("Custos e Tarifas (CET):")
            for t in tarifas:
                desc_t = f" - {t['nome']} ({t['tipo']}): "
                if "aliquota" in t: desc_t += f"Alíquota {t['aliquota']}"
                elif "valor_fixo_medio" in t: desc_t += f"R$ {t['valor_fixo_medio']}"
                elif "aliquota_mensal_estimada" in t: desc_t += f"Est. {t['aliquota_mensal_estimada']} mensais"
                desc_t += f" | Base: {t.get('base_calculo')}"
                linhas.append(desc_t)

        # Inadimplência
        inad = item.get("encargos_inadimplencia", {})
        linhas.append(f"Inadimplência: Multa {inad.get('multa_atraso_percentual')}% e Juros de Mora {inad.get('juros_mora_percentual_ao_mes')}% ao mês.")
        if inad.get("correcao_monetaria"): linhas.append(f"Correção: {inad['correcao_monetaria']}")

        # Unifica tudo em um único conteúdo textual para este produto
        conteudo_completo = "\n".join(linhas)
        
        # Adiciona como um Documento individual (evita que o splitter corte o produto no meio)
        final_docs.append(Document(
            page_content=conteudo_completo,
            metadata={"source": "produtos_credito.json", "product_id": item.get("id")}
        ))

    # 3. Gerar Embeddings e Salvar Base Vetorial
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    vector_db = FAISS.from_documents(final_docs, embeddings)
    vector_db.save_local("faiss_regulatory_index")
    
    return vector_db