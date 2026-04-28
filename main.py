import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import tldextract
import numpy as np
import ast
import calendar

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
            'URL':st.column_config.LinkColumn(),
            'Teste':st.column_config.LinkColumn(),
            'Keyword Intents': st.column_config.MultiselectColumn(
                options=['informational', 'navigational', 'commercial', 'transactional'],
                color=['#ffa421', '#803df5', '#00c0f2', "#17f748"]
            )
        },    
    )
    return df_tratado





#--------------------TÍTULO--------------------#
st.title('Analisador de termos 2.000')
#up file
up_file = st.file_uploader('Escolha um arquivo', type=['csv','xlsx'])

#--------------------SIDEBAR--------------------#
arquivo_carregado = up_file is None
placeholder_texto= st.sidebar.write('Selecione os filtros')
resumo= st.sidebar.toggle("Resumo dos dados",disabled=arquivo_carregado, value=True)
marca= st.sidebar.toggle("Pesquisa por marca",disabled=arquivo_carregado)
intencao= st.sidebar.toggle("Intenção de busca",disabled=arquivo_carregado)
ia= st.sidebar.toggle("Detalhamento de IA",disabled=arquivo_carregado)
detalhamento= st.sidebar.toggle("Visão detalhada de coluna",disabled=arquivo_carregado)
clusters= st.sidebar.toggle("Agrupamento por clusters",disabled=arquivo_carregado)
st.sidebar.divider()

def meses_a_partir_de(mes_inicio):
    # calendar.month_name[1:] pega [Janeiro, ..., Dezembro]
    meses = list(calendar.month_name)[1:]
    
    # Reorganiza a lista: pega do mês de início até o final, 
    # e coloca os anteriores no final
    index = mes_inicio - 1
    return meses[index + 1:] + meses[:index + 1]

#Leitura de arquivo upload
if up_file is not None:
    extensao=str(up_file.name).split('.')[-1]
    if extensao =='csv':
        df=pd.read_csv(up_file)
    else:
        df=pd.read_excel(up_file)
    st.write(f'Arquivo .{extensao} lido com sucesso!')
    
    st.session_state['data'] = df
    
    #--------------------TRATAMENTO DE TABELA--------------------#
    df['Google']=f'https://www.google.com/search?q='+df['Keyword'].str.replace(' ','+')+'&oq='+df['Keyword'].str.replace(' ','+')
    lista_detalhe=[ 'URL','Position','Keyword Intents','ai']
    #ajuste de url
    df['URL'] = df['URL']+' '
    #Filtro por AI
    df['ai']=(df['Position Type'].str.contains('AI overview')).astype(str)

    
    #buscando o domínio e predefenindo como marca
    dominio=tldextract.extract(str(df['URL'][0])).domain
    brand_input = st.sidebar.text_input("Coloque o regex de marca que você utiliza normalmente (opcional)", value=dominio)
    st.sidebar.divider()
    
    if brand_input:
        st.session_state['data']['marca'] = (st.session_state['data']['Keyword'].str.contains(brand_input)).astype(str)
        lista_detalhe.append('marca')
    if not brand_input:
        st.session_state['data']['marca'] = '-' 
    
    #campos escolhidos em tabela
    options = st.sidebar.multiselect("Selecione quais colunas você quer ver",list(st.session_state['data'].columns), default=['Keyword', 'Position','Search Volume','URL','Traffic (%)', 'Google' ])
    
    #função para detalhamento de palavra chave
    def kw_detail(item):
        termo_selecionado=df[df.index.values==item.index.values]
        termos_iguais = df[df['Keyword']==item['Keyword'].iloc[0]]
        st.subheader(f'Detalhamento de palava chave: :green[{termo_selecionado['Keyword'].iloc[0]}]')
        
        c1,c2,c3,c4=st.columns([1.5,1.5,1,1])
        with c1:
            st.markdown(f'**Palavra chave:** :green-badge[{termo_selecionado['Keyword'].iloc[0]}]')
        with c2:
            st.markdown(f'**URL:** :green-badge[{termo_selecionado['URL'].iloc[0]}]')
        with c3:
            posiciona = 'AI overview' in termo_selecionado['SERP Features by Keyword'].iloc[0]
            if posiciona:
                bgg='green-badge'
            else:
                bgg='red-badge'
            st.markdown(f'**Tem AI Overview na SERP?:** :{bgg}[{posiciona}]')
            
        with c4:
            posiciona = (termos_iguais['ai']=='True').any()
            if posiciona:
                bgg='green-badge'
            else:
                bgg='red-badge'
            st.markdown(f'**Site posiciona para IA:** :{bgg}[{posiciona}]')
        delta = termo_selecionado['Position'].iloc[0] - termo_selecionado['Previous position'].iloc[0]
        c1,c2 = st.columns(2, vertical_alignment="center")
        with c1:
            c1_1,c1_2,c1_3=st.columns(3)
            with c1_1:
                st.metric(label='Posição', value=termo_selecionado['Position'], delta=delta, delta_color="inverse", border=True,)
            with c1_2:
                st.metric(label='Volume de busca', value=termo_selecionado['Search Volume'], border=True, format='localized', height='stretch')
            with c1_3:
                st.metric(label='Tráfego (%)', value=termos_iguais['Traffic (%)'].sum(), border=True, format='localized', height='stretch')
            
                     
              
            c1_1,c1_2= st.columns(2)
            with c1_1:
                valor_unico = ", ".join(termos_iguais['Position Type'].unique())
                df_display = pd.DataFrame({"Tipo de posição": [valor_unico]})
                st.dataframe(df_display, hide_index=True,
                             column_config={'Tipo de posição':st.column_config.MultiselectColumn(
                                 options=["Organic","People also ask","AI overview",'Image pack'],
                                 color=["#ffa421", "#ffa421", "#803df5", '#ffa421'],
                             )})
                
            with c1_2:
                st.dataframe(termo_selecionado['Keyword Intents'], hide_index=True,
                            column_config={'Keyword Intents': st.column_config.MultiselectColumn(
                            "Intenção de busca",
                            options=['informational', 'navigational', 'commercial', 'transactional'],
                            color=['#ffa421', '#803df5', '#00c0f2', "#17f748"])
                            }
                )
            opcoes = termo_selecionado['SERP Features by Keyword'].iloc[0].split(',')
            lm=[]
            for i in opcoes:
                if i ==' AI overview': 
                    lm.append('#803df5')
                else:
                    lm.append('#ffa421')
                
            st.dataframe(termo_selecionado['SERP Features by Keyword'], hide_index=True,
                        column_config={
                            'SERP Features by Keyword': st.column_config.MultiselectColumn(
                                "SERP Features da palavra chave",
                                options=opcoes,
                                color=lm
                                )
                            }
                        )
            c11,c12 = st.columns(2)
            with c11:
                st.link_button("Abrir URL", type='primary', url=termo_selecionado['URL'].iloc[0], width='stretch')
            with c12:
                st.link_button("Abrir no Google", type='secondary', url=termo_selecionado['Google'].iloc[0], width='stretch')  
                
        with c2:
            tt = termo_selecionado['Trends'].apply(ast.literal_eval).iloc[0]
            termo_selecionado['Timestamp']= pd.to_datetime(termo_selecionado['Timestamp'])
            m=termo_selecionado['Timestamp'].dt.month.iloc[0]
            ala=meses_a_partir_de(m)
            fig = px.bar(x=ala, y=tt, text=tt)
            fig.update_traces(hoverinfo='none', hovertemplate=None, marker_cornerradius=15)
            fig.update_xaxes(showgrid=False, zeroline=False, dtick=1)
            fig.update_yaxes(showgrid=False, zeroline=False)
            fig.update_layout(yaxis_title=" ", xaxis_title=" ")
            st.plotly_chart(fig, config = {'scrollZoom': False},height=500)
            
        
    def df_trato_detail(x):
        df_tratado=st.dataframe(
            x,
            on_select="rerun",
            column_config={
                'Trends': st.column_config.BarChartColumn(
                    y_min=0,
                    y_max=100,
                ),      
                'Google':st.column_config.LinkColumn(display_text="Abrir no Google"),
                'URL':st.column_config.LinkColumn(),
                'Teste':st.column_config.LinkColumn(),
                'Keyword Intents': st.column_config.MultiselectColumn(
                    options=['informational', 'navigational', 'commercial', 'transactional'],
                    color=['#ffa421', '#803df5', '#00c0f2', "#17f748"]
                )
            },
            hide_index=True,
            selection_mode="single-row",
        )

        kw = df_tratado.selection.rows
        filtered_df = x.iloc[kw]
        if kw:
            kw_detail(filtered_df)

        return df_tratado
    

    #--------------------BIG NUMBERS E VISÃO INICIAL--------------------#
    if resumo:    
        st.subheader('Resumo dos dados')
        c1,c2,c3,c4,c5,c6,c7=st.columns(7)
        with c1:
            st.metric(label="1-3",border=True, value=df[(df['Position']<=3)&(df['Position Type']=='Organic')]['Keyword'].count(), format='localized')
        with c2:
            st.metric(label="4-10",border=True, value=df[(df['Position']>=4)&(df['Position Type']=='Organic')&(df['Position']<=10)]['Keyword'].count(), format='localized')
        with c3:
            st.metric(label="11-20",border=True, value=df[(df['Position']>=11)&(df['Position Type']=='Organic')&(df['Position']<=20)]['Keyword'].count(), format='localized')
        with c4:
            st.metric(label="21-50",border=True, value=df[(df['Position']>=21)&(df['Position Type']=='Organic')&(df['Position']<=50)]['Keyword'].count(), format='localized')
        with c5:
            st.metric(label="51-100",border=True, value=df[(df['Position']>=51)&(df['Position Type']=='Organic')&(df['Position']<=100)]['Keyword'].count(), format='localized')
        with c6:
            st.metric(label="Recursos de SERP",border=True, value=df[(df['Position Type']!='Organic')]['Keyword'].count(), format='localized')
        with c7:
            st.metric(label="Total",border=True, value=df['Keyword'].count(), format='localized')

        df_trato_detail(st.session_state['data'][options])
        st.divider()
    
    #--------------------ANÁLISE DE MARCA--------------------#
    if marca:       
        st.sidebar.divider()
        st.subheader('Análise de :green[marca]')   
        if brand_input:
            
            st.markdown(f'Marca: :green-badge[{brand_input}]')
            
            st.session_state['data']['marca'] = (st.session_state['data']['Keyword'].str.contains(brand_input)).astype(str)
            tratar_df(st.session_state['data'].groupby('marca').agg({'Keyword':['count',lambda x:round((x.count()/df['Keyword'].count())*100,2)]}).rename(columns={'<lambda_0>': 'Porcentagem'}))
            lista_detalhe.append('marca')
            tratar_df(st.session_state['data'].groupby('marca').agg({'Traffic (%)':'sum', 'Keyword':['count',lambda x: round((x.count()/df['Keyword'].count())*100,2)], 'Position':'mean' }).round({('Position','mean'):2}).rename(columns={'<lambda_0>': 'Porcentagem'}))
        if not brand_input:
            st.session_state['data']['marca'] = '-'
            st.markdown(':red[**Preencha o campo na sidebar para que os filtros de marca sejam aplicados**]')
        st.divider()
        
    #--------------------INTENÇÃO DE BUSCA--------------------#
    if intencao:
        st.subheader('Agrupamento por :green[intenção de busca]')
        x=df.groupby('Keyword Intents').agg({'Keyword':['count',lambda x:round((x.count()/df['Keyword'].count())*100,2)]}).rename(columns={'<lambda_0>': 'Porcentagem'}).sort_values(by=('Keyword','count'),ascending=False)
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
        df_select = st.session_state['data'].groupby(x).agg({'Keyword':'count','Traffic (%)':'sum'})
        tratar_df(df_select)
        y=st.selectbox('Filtros de valores', st.session_state['data'][x].unique())
        dff=st.session_state['data'][st.session_state['data'][x]==y][options]
        if resumo:
            tratar_df(dff)
        else:
            df_trato_detail(dff)   
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
            df_final = pd.concat(lista_df)
            df_final.index = categoria
            tratar_df(df_final)
            selec_detail=st.selectbox('Filtros de valores', categoria)
            c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
            with c1:
                st.metric(label="1-3",border=True, value=df[(df[y].str.contains(selec_detail))&(df['Position']<=3)&(df['Position Type']=='Organic')]['Keyword'].count())
            with c2:
                st.metric(label="4-10",border=True, value=df[(df[y].str.contains(selec_detail))&(df['Position']>=4)&(df['Position Type']=='Organic')&(df['Position']<=10)]['Keyword'].count(), format='localized')
            with c3:
                st.metric(label="11-20",border=True, value=df[(df[y].str.contains(selec_detail))&(df['Position']>=11)&(df['Position Type']=='Organic')&(df['Position']<=20)]['Keyword'].count(), format='localized')
            with c4:
                st.metric(label="21-50",border=True, value=df[(df[y].str.contains(selec_detail))&(df['Position']>=21)&(df['Position Type']=='Organic')&(df['Position']<=50)]['Keyword'].count(), format='localized')
            with c5:
                st.metric(label="51-100",border=True, value=df[(df[y].str.contains(selec_detail))&(df['Position']>=51)&(df['Position Type']=='Organic')&(df['Position']<=100)]['Keyword'].count(), format='localized')
            with c6:
                st.metric(label="Recursos de SERP",border=True, value=df[(df[y].str.contains(selec_detail))&(df['Position Type']!='Organic')]['Keyword'].count())
            with c7:
                st.metric(label="Total",border=True, value=df[df[y].str.contains(selec_detail)]['Keyword'].count(), format='localized')
            if resumo or detalhamento:
                tratar_df(st.session_state['data'][st.session_state['data'][y].str.contains(selec_detail)][options])
            else:
                df_trato_detail(st.session_state['data'][st.session_state['data'][y].str.contains(selec_detail)][options])
