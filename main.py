import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


st.set_page_config(layout="wide", page_title='Analisador de Páginas - SEMRush', page_icon="🤖")



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

st.title('Analisador de termos 2.000')
#up file
up_file = st.file_uploader('Escolha um arquivo', type=['csv','xlsx'])

#--------------------SIDEBAR--------------------#
arquivo_carregado = up_file is None
placeholder_texto= st.sidebar.write('Selecione os filtros')
resumo= st.sidebar.toggle("Resumo dos dados",disabled=arquivo_carregado, value=True)
marca= st.sidebar.toggle("Pesquisa por marca",disabled=arquivo_carregado)
intencao= st.sidebar.toggle("Detalhamento de intenção de busca",disabled=arquivo_carregado)
ia= st.sidebar.toggle("Detalhamento de IA",disabled=arquivo_carregado)
detalhamento= st.sidebar.toggle("Visão detalhada de coluna",disabled=arquivo_carregado)
clusters= st.sidebar.toggle("Agrupamento por clusters",disabled=arquivo_carregado)


#Leitura de arquivo upload
if up_file is not None:
    extensao=str(up_file.name).split('.')[-1]
    if extensao =='csv':
        df=pd.read_csv(up_file)
    else:
        df=pd.read_excel(up_file)
    st.write(f'Arquivo .{extensao} lido com sucesso!')
    if 'data' not in st.session_state:
       st.session_state['data'] = df
       df_mestre=st.session_state['data'] 
    
    #--------------------TRATAMENTO DE TABELA--------------------#
    df['Google']=f'https://www.google.com/search?q='+df['Keyword'].str.replace(' ','+')+'&oq='+df['Keyword'].str.replace(' ','+')
    lista_detalhe=[ 'URL','Position','Keyword Intents','ai']
    #ajuste de url
    df['URL'] = df['URL']+' '
    #Filtro por AI
    df['ai']=(df['Position Type'].str.contains('AI overview')).astype(str)
    df['marca']='-'
    options = st.sidebar.multiselect("Selecione quais colunas você quer ver",list(st.session_state['data'].columns), default=['Keyword', 'Position','Search Volume','URL','Traffic (%)', 'Google' ])
    
    #--------------------BIG NUMBERS E VISÃO INICIAL--------------------#
    if resumo:    
        st.subheader('Resumo dos dados')
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
        #options = st.multiselect("Selecione quais colunas você quer ver",list(st.session_state['data'].columns), default=['Keyword', 'Position','Search Volume','URL','Traffic (%)', 'Google' ])
        tratar_df(st.session_state['data'][options])
        st.divider()
    
    #--------------------ANÁLISE DE MARCA--------------------#
    if marca:       
        st.sidebar.divider()
        text_input = st.sidebar.text_input("Coloque o regex de marca que você utiliza normalmente (opcional)")    
        if text_input:
            st.subheader('Análise de :green[marca]')
            st.write("Marca: ", text_input)
            st.session_state['data']['marca'] = (st.session_state['data']['Keyword'].str.contains(text_input)).astype(str)
            tratar_df(st.session_state['data'].groupby('marca').agg({'Keyword':['count',lambda x:round((x.count()/df['Keyword'].count())*100,2)]}).rename(columns={'<lambda_0>': 'Porcentagem'}))
            lista_detalhe.append('marca')
            tratar_df(st.session_state['data'].groupby('marca').agg({'Traffic (%)':'sum', 'Keyword':['count',lambda x: round((x.count()/df['Keyword'].count())*100,2)], 'Position':'mean' }).round({('Position','mean'):2}).rename(columns={'<lambda_0>': 'Porcentagem'}))
        if not text_input:
            st.session_state['data']['marca'] = '-'
        st.divider()
        
    #--------------------INTENÇÃO DE BUSCA--------------------#
    if intencao:
        st.subheader('Agrupamento por :green[intenção de busca]')
        x=df.groupby('Keyword Intents').agg({'Keyword':['count',lambda x:round((x.count()/df['Keyword'].count())*100,2)]}).rename(columns={'<lambda_0>': 'Porcentagem'})
        tratar_df(x)

        st.divider()
        
    #--------------------IA--------------------#
    if ia:
        st.subheader('Termos com :green[IA]')
        tratar_df(df.groupby('ai').agg({'Keyword':['count',lambda x:round((x.count()/df['Keyword'].count())*100,2)]}).rename(columns={'<lambda_0>': 'Porcentagem'}))
        df['Possibilidade de AI']=(df['SERP Features by Keyword'].str.contains('AI', na=False)).astype(str)
        tratar_df(df.groupby(['Possibilidade de AI','ai']).agg({'Keyword':['count',lambda x:round((x.count()/df['Keyword'].count())*100,2)]}).rename(columns={'<lambda_0>': 'Porcentagem'}))
        st.divider()
        
    #--------------------VISÃO DETALHADA--------------------#
    if detalhamento:
        st.subheader('Visão detalhada por colunas')
        x=st.selectbox('Filtros de colunas', lista_detalhe)
        df_select = df.groupby(x).agg({'Keyword':'count','Traffic (%)':'sum'})
        tratar_df(df_select)
        y=st.selectbox('Filtros de valores', df[x].unique())
        dff=st.session_state['data'][st.session_state['data'][x]==y][options]
        tratar_df(dff)   
        st.divider()
    
    #--------------------AGRUPAMENTO POR CLUSTERS--------------------#
    if clusters:
        st.subheader('Agrupamento por :green[Clusters]')
        c1,c2=st.columns(2)
        with c1:
            y=st.selectbox('Filtros de valores', ['Keyword', 'URL'])

        with c2:
            if y == 'URL':
                sug=df[y].str.split('https://internet.tim.com.br').str[1].value_counts(ascending=False).head(5)
            else:
                sug=df[y].str.split(' ').str[0].value_counts(ascending=False).head(5)
            categoria=st.multiselect("Selecione quais colunas você quer ver",sug.index,accept_new_options=True)

        lista_df=[]
        if categoria:
            for i in list(categoria):
                df[i]=df[y].str.contains(i, na=False).astype(str)
                if df[df[i] == 'True'].empty ==True:
                    cols = pd.MultiIndex.from_tuples([('Keyword','count'),('Keyword','Porcentagem'),('Traffic (%)','sum'),('Position','mean')])
                    x = pd.DataFrame(np.nan, index=['True'], columns=cols)   
                else:                
                    x=df[df[i]=='True'].groupby(i).agg({'Keyword':['count',lambda x: round((x.count()/df['Keyword'].count())*100,2)], 'Traffic (%)':'sum','Position':'mean' }).round({('Position','mean'):2}).rename(columns={'<lambda_0>': 'Porcentagem'})
                lista_df.append(x)
                st.write()
            df_final = pd.concat(lista_df)
            df_final.index = categoria
            tratar_df(df_final)
            selec_detail=st.selectbox('Filtros de valores', categoria)
            c1,c2,c3,c4,c5,c6 = st.columns(6)
            with c1:
                st.metric(label="1-3",border=True, value=df[(df[y].str.contains(selec_detail))&(df['Position']<=3)&(df['Position Type']=='Organic')]['Keyword'].count())
            with c2:
                st.metric(label="4-10",border=True, value=df[(df[y].str.contains(selec_detail))&(df['Position']>=4)&(df['Position Type']=='Organic')&(df['Position']<=10)]['Keyword'].count())
            with c3:
                st.metric(label="11-20",border=True, value=df[(df[y].str.contains(selec_detail))&(df['Position']>=11)&(df['Position Type']=='Organic')&(df['Position']<=20)]['Keyword'].count())
            with c4:
                st.metric(label="21-50",border=True, value=df[(df[y].str.contains(selec_detail))&(df['Position']>=21)&(df['Position Type']=='Organic')&(df['Position']<=50)]['Keyword'].count())
            with c5:
                st.metric(label="51-100",border=True, value=df[(df[y].str.contains(selec_detail))&(df['Position']>=51)&(df['Position Type']=='Organic')&(df['Position']<=100)]['Keyword'].count())
            with c6:
                st.metric(label="Recursos de SERP",border=True, value=df[(df[y].str.contains(selec_detail))&(df['Position Type']!='Organic')]['Keyword'].count())
            listasem=len(categoria)*-1
            
            tratar_df(df[df[y].str.contains(selec_detail)][options])
