import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go

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


st.title("DASHBOARD DE VENDAS :shopping_trolley:")

#url = "https://labdados.com/produtos"
#response = requests.get(url)
#dados = pd.DataFrame.from_dict(url.json())

url = "/home/jardelsewo.seed/Documentos/Alura/streamlit/produtos.json"
df = pd.read_json(url)

regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Regiao', regioes)

if regiao == 'Brasil':
    regia = ''

todos_anos = st.sidebar.checkbox('Dados de todo o periodo', value = True)

if todos_anos:
    ano = ' '
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

df['Data da Compra'] = pd.to_datetime(df['Data da Compra'], format = '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', df['Vendedor'].unique())
if filtro_vendedores:
    df = df[df['Vendedor'].isin(filtro_vendedores)]

#receita_mensal = df.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preco'].sum().reset_index()
receita_mensal = df.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = df.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

##Tabelas

### Tabelas de receita

receitas_estados = df.groupby('Local da compra')[['Preço']].sum()
#receitas_estados = df.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(
#    receitas_estados, left_on = 'Local da compra', right_index=True ).sort_values('Preço', ascending=True)

Local_da_compra_agrupado = df.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']]

receita_estados = Local_da_compra_agrupado\
    .merge(receitas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

### Tabelas de quantidade de vendas

## Tabelas de quantidade de vendas por estado
qtdade_vendas_por_estado = df.groupby('Local da compra')[['Local da compra']].count()
qtdade_vendas_por_estado = qtdade_vendas_por_estado._rename(columns= {"Local da compra" : "Total de vendas"}).reset_index()

imagem_vendas_por_estado = pd.merge(Local_da_compra_agrupado,qtdade_vendas_por_estado,how='left', on='Local da compra')


## Tabelas de quantidade de vendas por mensal
qtdade_vendas_mensal = df.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Local da compra'].count().reset_index()
qtdade_vendas_mensal = qtdade_vendas_mensal._rename(columns= {"Local da compra" : "Total de vendas"})
qtdade_vendas_mensal['Ano'] = qtdade_vendas_mensal['Data da Compra'].dt.year
qtdade_vendas_mensal['Mes'] = qtdade_vendas_mensal['Data da Compra'].dt.month_name()

qtdade_vendas_mensal = qtdade_vendas_mensal[['Total de vendas', 'Ano', 'Mes']]

## Tabelas de top 5 maior qtdade de vendas
## Tabelas de quantidade de vendas por categoria de produtos
qtdade_vendas_por_produto = df.groupby("Produto").size().sort_values(ascending=False).reset_index(name="Total por Produto")

#qtdade_vendas_por_produto = qtdade_vendas_por_produto.set_index('Produto').groupby('Produto').count()

print(qtdade_vendas_por_produto)


#print(meses)

### Tabela vendedores
vendedores = pd.DataFrame(df.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

#print(qtdade_vendas_mensal[['Total de vendas']].sort_values('Ano', ascending=False).head(qtdade_vendas_mensal))

##Graficos
fig_mapa_receita = px.scatter_geo(receita_estados,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Preço',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat':False,'lon':False},
                                   title = 'Receita por Estado')

fig_mapa_vendas_por_estado = px.scatter_geo(imagem_vendas_por_estado,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Total de vendas',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat':False,'lon':False},
                                   title = 'Vendas por Estado')


fig_receita_mensal = px.line(receita_mensal,
                            x = 'Mes',
                            y = 'Preço',
                            markers = True,
                            range_y = (0, receita_mensal.max()),
                            color='Ano',
                            line_dash = 'Ano',
                            title = 'Receita mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')


fig_receita_estados = px.bar(receita_estados.head(),
                            x = 'Local da compra',
                            y = 'Preço',
                            text_auto = True,
                            title = 'Top estados')
fig_receita_estados.update_layout(yaxis_title = 'Receita')


fig_receita_categorias = px.bar(receita_categorias,
                                text_auto= True,
                                title = 'Receita por Categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

## Visualizacao do streamlit

aba_receita, aba_qtdade_vendas, aba_vendedores = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba_receita:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        #st.metric('Receita', '2')
        st.metric('Receita', formata_numero(df['Preço'].sum()), 'R$')
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(df.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)
with aba_qtdade_vendas:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        #st.metric('Receita', '2')
        st.metric('Receita', formata_numero(df['Preço'].sum()), 'R$')
        st.plotly_chart(fig_mapa_vendas_por_estado, use_container_width=True)

        # Criar a figura de barras
        fig_vendas_por_produto = go.Figure(data=[go.Bar(x=qtdade_vendas_por_produto['Produto'], y=qtdade_vendas_por_produto['Total por Produto'])])

        # Configurar o layout
        fig_vendas_por_produto.update_layout(title='Total Vendas por Produto',
                          xaxis_title='Produto',
                          yaxis_title='Total Vendas por Produto')

        st.plotly_chart(fig_vendas_por_produto)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(df.shape[0]))

        x1 = qtdade_vendas_mensal.query("Ano == 2020")
        x2 = qtdade_vendas_mensal.query("Ano == 2021")
        x3 = qtdade_vendas_mensal.query("Ano == 2022")
        x4 = qtdade_vendas_mensal.query("Ano == 2023")

        meses = []

        for i in x1['Mes']:
            meses.append(i)

        #print(hist_data)

        fig = go.Figure(data=[
            go.Scatter(name='2020', x=x1['Mes'], y=x1['Total de vendas']),
            go.Scatter(name='2021', x=x2['Mes'], y=x2['Total de vendas']),
            go.Scatter(name='2022', x=x3['Mes'], y=x3['Total de vendas']),
            go.Scatter(name='2023', x=x4['Mes'], y=x4['Total de vendas'])
        ])
        # Change the bar mode
        fig.update_layout(barmode='group',
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)'
                          )

        # Remova as linhas de grade e linhas dos eixos
        fig.update_xaxes(showgrid=False, showline=False)
        fig.update_yaxes(showgrid=False, showline=False)

        st.plotly_chart(fig)

with aba_vendedores:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        #st.metric('Receita', '2')
        st.metric('Receita', formata_numero(df['Preço'].sum()), 'R$')

        fig_receita_vendedores = px.bar(
            vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
            x='sum',
            y=vendedores[['sum']].sort_values(['sum'], ascending=False).head(qtd_vendedores).index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendedores (receita)'
        )

        st.plotly_chart(fig_receita_vendedores)



    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(df.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x='count',
                                        y=vendedores[['count']].sort_values('count', ascending=False).head(
                                            qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)')

        st.plotly_chart(fig_vendas_vendedores)
#Tabela Geral do Dataframe
st.dataframe(df)
