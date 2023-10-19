import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(
    #page_title="Ex-stream-ly Cool App",
    #page_icon="🧊",
    layout="wide",
    #initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso', icon = "✅")
    time.sleep(5)
    sucesso.empty()


st.title("Dados Brutos :shopping_trolley:")

#url = "https://labdados.com/produtos"
#response = requests.get(url)
#dados = pd.DataFrame.from_dict(url.json())

url = "/home/jardelsewo.seed/Documentos/Alura/streamlit/produtos.json"
df = pd.read_json(url)

df['Data da Compra'] = pd.to_datetime(df['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(df.columns), list(df.columns))

### ------------------------- BLOCO DE NOMES ---------------------------------

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do Produto'):
    produtos = st.multiselect('Seleciona os produtos', df['Produto'].unique(), df['Produto'].unique())
with st.sidebar.expander('Categoria do Produto'):
    categoria_produtos = st.multiselect('Categoria do Produto', df['Categoria do Produto'].unique(), df['Categoria do Produto'].unique())
with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Vendedor', df['Vendedor'].unique(), df['Vendedor'].unique())
with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Tipo de pagamento', df['Tipo de pagamento'].unique(), df['Tipo de pagamento'].unique())


### ------------------------- BLOCO DE VALORES ---------------------------------
with st.sidebar.expander('Preco do Produto'):
    preco = st.slider('Seleciona o preçe', 0, 5000, (0,5000))
with st.sidebar.expander('Frete'):
    frete = st.slider('Seleciona o frete', 0, 300, (0, 300))
with st.sidebar.expander('Avaliaçao da compra'):
    avaliacao_compra = st.slider('Avaliação da compra', 1, 10, (1,10))
with st.sidebar.expander('Quantidade de parcelas'):
    qtdade_parcelas = st.slider('Quantidade de parcelas', 0, 10, (0,10))


### ------------------------- BLOCO DE DATAS ---------------------------------
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (df['Data da Compra'].min(), df['Data da Compra'].max()))

#Primeiro xxxx = referente a coluna do df in @xxxx = referente ao filtro feito pelo streamlit
query = '''
Produto in @produtos and \
`Categoria do Produto` in @categoria_produtos and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedor and \
@avaliacao_compra[0]<= `Avaliação da compra` <= @avaliacao_compra[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtdade_parcelas[0] <= `Quantidade de parcelas` <= @qtdade_parcelas[1]
'''
dados_filtrados = df.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)


st.markdown(f'A tabela possui :green[{dados_filtrados.shape[0]}] linhas e :red[{dados_filtrados.shape[1]}] colunas')
st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em csv', data = converte_csv(dados_filtrados), file_name= nome_arquivo, mime = 'text/csv', on_click= mensagem_sucesso())

#print(df['Frete'].max())
