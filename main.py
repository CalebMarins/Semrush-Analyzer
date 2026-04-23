import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title('Analisador de termos 2000')

up_file = st.file_uploader('Escolha um arquivo CSV', type='csv')

#tratamento de Dataframe no streamlit
def tratar_df(x):
    df_tratado=st.dataframe(
    x,
    column_config={
        'Trends': st.column_config.BarChartColumn(
            y_min=0,
            y_max=100,
        ),
        'Google':st.column_config.LinkColumn(display_text="Abrir no Google"),
        'URL':st.column_config.LinkColumn()
    },
    
    )
    return df_tratado
st.set_page_config(layout="wide")

if up_file is not None:
    st.write('Arquivo lido com sucesso!')
    text_input = st.text_input("Coloque o regex de marca que você utiliza normalmente (opcional)")
    #--------------------TRATAMENTO DE TABELA--------------------#
    df=pd.read_csv(up_file)
    df['Google']=f'https://www.google.com/search?q='+df['Keyword'].str.replace(' ','+')+'&oq='+df['Keyword'].str.replace(' ','+')
    lista_detalhe=[ 'URL','Position','Keyword Intents','ai']
    #filtros de marca
    if text_input:
        st.write("Marca: ", text_input)
        df['marca'] = (df['Keyword'].str.contains(text_input)).astype(str)
        tratar_df(df.groupby('marca').agg({'Keyword':['count',lambda x:round((x.count()/df['Keyword'].count())*100,2)]}).rename(columns={'<lambda_0>': 'Porcentagem'}))
        lista_detalhe.append('marca')
        tratar_df(df.groupby('marca').agg({'Traffic (%)':'sum', 'Keyword':['count',lambda x: round((x.count()/df['Keyword'].count())*100,2)], 'Position':'mean' }).round({('Position','mean'):2}).rename(columns={'<lambda_0>': 'Porcentagem'}))
    #Filtro por AI
    df['ai']=(df['Position Type'].str.contains('AI overview')).astype(str)
    st.subheader('Resumo dos dados')
    options = st.multiselect("Selecione quais colunas você quer ver",list(df.columns), default=['Keyword', 'Position','Search Volume','URL','Traffic (%)', 'Google' ])
    c1,c2,c3,c4,c5,c6=st.columns(6)
    with c1:
        st.metric(label="1-3",border=True, value=df[(df['Position']<=3)&(df['Position Type']=='Organic')]['Keyword'].count())
    with c2:
        st.metric(label="4-10",border=True, value=df[(df['Position']>=4)&(df['Position Type']=='Organic')&(df['Position']<=10)]['Keyword'].count())
    with c3:
        st.metric(label="11-20",border=True, value=df[(df['Position']>=11)&(df['Position Type']=='Organic')&(df['Position']<=20)]['Keyword'].count())
    with c4:
        st.metric(label="21-50",border=True, value=df[(df['Position']>=21)&(df['Position Type']=='Organic')&(df['Position']<=50)]['Keyword'].count())
    with c5:
        st.metric(label="51-100",border=True, value=df[(df['Position']>=51)&(df['Position Type']=='Organic')&(df['Position']<=100)]['Keyword'].count())
    with c6:
        st.metric(label="Recursos de SERP",border=True, value=df[(df['Position Type']!='Organic')]['Keyword'].count())
    tratar_df(df[options])
    
    st.divider()
    #--------------------Intenção de busca--------------------#
    st.subheader('Agrupamento por :green[intenção de busca]')
    x=df.groupby('Keyword Intents').agg({'Keyword':['count',lambda x:round((x.count()/df['Keyword'].count())*100,2)]}).rename(columns={'<lambda_0>': 'Porcentagem'})
    tratar_df(x)
    
    st.divider()
    #--------------------IA--------------------#
    st.subheader('Termos com :green[IA]')
    tratar_df(df.groupby('ai').agg({'Keyword':['count',lambda x:round((x.count()/df['Keyword'].count())*100,2)]}).rename(columns={'<lambda_0>': 'Porcentagem'}))
    df['Possibilidade de AI']=(df['SERP Features by Keyword'].str.contains('AI', na=False)).astype(str)
    tratar_df(df.groupby(['Possibilidade de AI','ai']).agg({'Keyword':['count',lambda x:round((x.count()/df['Keyword'].count())*100,2)]}).rename(columns={'<lambda_0>': 'Porcentagem'}))
    st.divider()
    #--------------------Visão detalhada--------------------#
    st.subheader('Visão detalhada por colunas')
    x=st.selectbox('Filtros de colunas', lista_detalhe)
    df_select = df[x].value_counts()
    tratar_df(df_select)
    y=st.selectbox('Filtros de valores', df[x].unique())
    dff=df[df[x]==y]
    tratar_df(dff)   