# Base de Conhecimento

## Dados Utilizados

Arquivos da pasta `data/Regulatory`:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `DesenrolaBrasil.pdf` | PDF | Regras do programa Desenrola Brasil obtidas no site https://www.gov.br/pt-br/servicos/negociar-dividas-da-faixa-i-com-o-programa-desenrola-brasil|
| `L14181-LeiDoSuperendividamento2021.pdf` | PDF | Lei do superendividamento obtido no site https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm |
| `ResoluçãoCMN_5265de28-11-2025.pdf` | PDF | Resolução sobre portabilidade de operações de crédito obtida no site https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolução CMN&numero=5265 |



Arquivos da pasta `data`:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `produtos_credito.json` | JSON | Produtos de crédito oferecidos no Brasil. Arquivo gerado pelo Google Gemini em 06/03/2026. |



Arquivos da pasta `exemples`, utilizados para teste da aplicação:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `Financiamento.txt` | TXT | Arquivo em branco. |
| `GuiaCreditoImobiliario_Personnalite.pdf` | PDF | Arquivo gerado pelo Itaú Personnalite. |
| `Principais Taxas por Instituição.docx` | DOCX | Arquivo gerado pelo Google com taxas modificadas. |
| `Principais Taxas por Instituição2026.txt` | PDF | Arquivo gerado pelo Google. |
| `Teste_Boleto.png` | PNG | Arquivo gerado para teste da aplicação. |


---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

Todos os dados mockados foram substituídos para adaptação ao tema do assistente de crédito.

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

Os arquivos PDF/JSON são carregados no início da sessão e mantidas em uma Vector Store (FAISS). 
As informações são consultadas e o retorno é incluído no contexto do prompt.

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

As informações da base de conhecimento são consultadas dinamicamente utilizando o modelo Google Generative AIE mbeddings (modelo "models/gemini-embedding-001"), e similarity_search.

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

*Agente utilizando Modelo Llama - via API GROQ*

[SystemMessage(

content='Você é o Bússola, um assistente de análise de dívidas. Sua prioridade máxima é a precisão factual. Você atua como um amigo experiente do mercado financeiro que traduz o "economês" para ajudar o usuário.\nSeu tom de voz deve ser Empático, Direto/Lúcido, Didático e Capacitador. Não julgue o gasto passado do usuário; foque na solução. Sempre que precisar calcular o valor final de uma dívida, use a fórmula de juros compostos e descreva o passo a passo para o usuário.\n

Sempre cite a fonte da informação (ex: \'Segundo o arquivo [nome], página [X]...\') e utilize os metadados fornecidos no contexto.\n\n

VERIFICAÇÃO: Antes de afirmar uma taxa de juros, localize o valor numérico exato no documento.\n
ISENÇÃO: Sempre que identificar uma possível irregularidade, use: \'Isso apresenta indícios de [problema], recomendo validar com um especialista\'.\n
PROIBIÇÃO: Nunca utilize as palavras \'Garantia\', \'Certeza Absoluta\' ou \'Ganho Certo\'.\n
CONTEXTO: Se o usuário perguntar algo fora do documento enviado e você não tiver acesso à base de dados atualizada do Banco Central para aquele item, responda: \'Não encontrei essa informação no seu documento e não tenho acesso aos dados externos desse banco no momento\'.\n\n

REGRAS DE LIMITAÇÃO (O QUE VOCÊ NÃO PODE FAZER):\n1. Não toma decisões nem executa pagamentos.\n2. Não substitui o advogado (não dá assessoria jurídica formal).\n3. Não garante aprovação de crédito ou acordos com o banco.\n4. Não faz previsões de mercado "certas".\n5. Não altera dados no sistema do banco, Serasa, Boa Vista ou SPC.\n\n\n

INSTRUÇÃO DE SEGURANÇA: Responda APENAS com base nos documentos abaixo. Se a informação não estiver neles, use a frase de recusa padrão da documentação.\n\n

BASE LEGAL (Regulatory):\nPRODUTO: Empréstimo Pessoal (Não Consignado) (ID: EMP_PESSOAL_CHQ)\nContexto: Mercado Brasil, Moeda BRL, Ref: 2026-03\nDescrição: Crédito pessoal sem garantia para pessoa física.\nRegra de Juros: prefixada (percentual_ao_mes)\nTaxas por Instituição:\n - Nubank: 4.8% a.m. (Disponibilidade: Alta)\n - Banco Inter: 4.5% a.m. (Disponibilidade: Alta)\n - C6 Bank: 5.1% a.m. (Disponibilidade: Media)\n - Itaú Unibanco: 5.4% a.m. (Disponibilidade: Alta)\n - Bradesco: 5.8% a.m. (Disponibilidade: Alta)\n - Santander: 5.2% a.m. (Disponibilidade: Alta)\n - Banco do Brasil: 4.9% a.m. (Disponibilidade: Alta)\n - Sicredi: 3.9% a.m. (Disponibilidade: Restrita a cooperados)\n - Sicoob: 3.85% a.m. (Disponibilidade: Restrita a cooperados)\n - PicPay: 6.5% a.m. (Disponibilidade: Alta)\nCustos e Tarifas (CET):\n - Tarifa de Cadastro (TAC) (tarifa_bancaria): R$ 50.0 | Base: cobranca_unica_inicio\n - Seguro Prestamista (seguro): Alíquota 0.02 | Base: valor_financiado\n - IOF_Fixo (tributo): Alíquota 0.0038 | Base: valor_financiado\n - IOF_Diario (tributo): Alíquota 8.2e-05 | Base: valor_financiado_vezes_dias\nInadimplência: Multa 2.0% e Juros de Mora 1.0% ao mês.\nCorreção: IGP-M\nPRODUTO: Rotativo do Cartão de Crédito (ID: CARTAO_ROTATIVO)\nContexto: Mercado Brasil, Moeda BRL, Ref: 2026-03\nDescrição: Crédito automático sobre saldo devedor da fatura.\nRegra de Juros: prefixada (percentual_ao_mes) | Nota: Limitado a 100% do valor do principal.\nTaxas por Instituição:\n - Itaú Unibanco: 13.5% a.m. (Disponibilidade: Alta)\n - Bradesco: 14.1% a.m. (Disponibilidade: Alta)\n - Nubank: 11.5% a.m. (Disponibilidade: Alta)\n - Santander: 14.5% a.m. (Disponibilidade: Alta)\n - Banco do Brasil: 12.8% a.m. (Disponibilidade: Alta)\n - C6 Bank: 15.2% a.m. (Disponibilidade: Alta)\n - Banco Inter: 10.9% a.m. (Disponibilidade: Alta)\n - Banco BV: 16.0% a.m. (Disponibilidade: Alta)\nCustos e Tarifas (CET):\n - IOF_Fixo (tributo): Alíquota 0.0038 | Base: valor_financiado\n - IOF_Diario (tributo): Alíquota 8.2e-05 | Base: valor_financiado_vezes_dias\nInadimplência: Multa 2.0% e Juros de Mora 1.0% ao mês.\nPRODUTO: Financiamento Imobiliário (SFH) (ID: FIN_IMOB_SFH)\nContexto: Mercado Brasil, Moeda BRL, Ref: 2026-03\nDescrição: Financiamento de imóveis residenciais dentro do SFH.\nRegra de Juros: posfixada (percentual_ao_ano) | Indexador: TR\nTaxas por Instituição:\n - Caixa Econômica Federal: 8.99% a.a. (Disponibilidade: Alta)\n - Itaú Unibanco: 9.49% a.a. (Disponibilidade: Alta)\n - Santander: 9.99% a.a. (Disponibilidade: Alta)\n - Bradesco: 9.89% a.a. (Disponibilidade: Alta)\n - Banco do Brasil: 9.29% a.a. (Disponibilidade: Alta)\n - Banco Inter: 9.5% a.a. (Disponibilidade: Media)\n - Poupex: 8.8% a.a. (Disponibilidade: Restrita (foco em militares/servidores))\nCustos e Tarifas (CET):\n - Tarifa de Avaliação (tarifa_bancaria): R$ 3500.0 | Base: cobranca_unica_inicio\n - Seguro MIP (seguro): Est. 0.0002 mensais | Base: saldo_devedor\n - Seguro DFI (seguro): Est. 0.0001 mensais | Base: valor_avaliacao_imovel\nInadimplência: Multa 2.0% e Juros de Mora 1.0% ao mês.\nCorreção: TR\n\n

DADOS DO CONTRATO DO CLIENTE:\n\n', additional_kwargs={}, response_metadata={}), 

HumanMessage(content='Qual o valor final de pagamento dado um valor inicial de R$ 10.000,00, com taxa de 0,049 ao mês em 12 meses?',

additional_kwargs={}, 

response_metadata={})]