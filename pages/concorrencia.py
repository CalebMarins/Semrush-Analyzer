import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn2,venn3
import plotly.express as px
import tldextract

st.set_page_config(layout="wide", page_title='Analisador de Concorrência - SEMRush', page_icon="🤼")

#--------------------TÍTULO--------------------#
st.title('🤼Análise de concorrência')
clcf = {
        'Trends': st.column_config.BarChartColumn(
            y_min=0,
            y_max=100,
        ),
        'Google':st.column_config.LinkColumn(display_text="Abrir no Google"),
        'URL':st.column_config.LinkColumn(),
    }

#--------------------TRATAMENTO DE DATAFRAME ST--------------------#
def tratar_df(x):
    df_tratado=st.dataframe(
    x,
    column_config=clcf,
    hide_index=True
    
    )
    return df_tratado

#--------------------SUBINDO ARQUIVO--------------------#
up_file = st.sidebar.file_uploader('Suba o arquivo CSV do seu cliente', type=['csv','xlsx'], accept_multiple_files=False)
if up_file:
    extensao=str(up_file.name).split('.')[-1]
    if extensao =='csv':
        df=pd.read_csv(up_file)
    else:
        df=pd.read_excel(up_file)
    st.write(f'Arquivo .{extensao} lido com sucesso!')
    
    #--------------------TRATAMENTO DE TABELA--------------------#
    df['Google']=f'https://www.google.com/search?q='+df['Keyword'].str.replace(' ','+')+'&oq='+df['Keyword'].str.replace(' ','+')
    #ajuste de url
    df['URL'] = df['URL']+' '
    #Filtro por AI
    df['Posiciona para AI']=(df['Position Type'].str.contains('AI overview')).astype(str)
    st.session_state['data'] = df

#--------------------COM SESSION STATE--------------------#
if 'data' in st.session_state:
    df_up= st.session_state['data']
    keywords_cliente = set(df_up['Keyword'])
    dados_confronto = {"TIM": keywords_cliente}

    #--------------------FUNÇÃO PARA DETALHAR KW--------------------#
    def kw_detail(item):
        termo_selecionado=iinter[iinter['Keyword']==item['Keyword'].iloc[0]]
        c1,c2 = st.columns(2, vertical_alignment="center")

        with c1:
            c1_1,c1_2,c1_3=st.columns(3)
            with c1_1:
                st.metric(label=f'Posição', value=termo_selecionado['Position'].min(), delta_color="inverse", border=True, height='stretch')
            with c1_2:
                if selec =='Todos':
                    xx=list(iinter['Conc'].unique())
                    for i in xx:
                        st.metric(label=f'Posição {i}', value=termo_selecionado[f'Posição {i}'].min(),format='plain', delta_color="inverse", border=True,)
                else:
                    st.metric(label=f'Posição {selec}', value=termo_selecionado[f'Posição {selec}'].min(),format='plain', delta_color="inverse", border=True,)

                

            with c1_3:
                st.metric(label='Volume de busca', value=termo_selecionado['Search Volume'].min(), border=True, format='localized', height='stretch')
        st.divider()
    def df_trato_detail(x):
        df_tratado=st.dataframe(
            x,
            on_select="rerun",
            column_config=clcf,
            hide_index=True,
            selection_mode="single-row",
        )
        kw = df_tratado.selection.rows
        if kw:
            filtered_df = x.iloc[kw]
            kw_detail(filtered_df)
        return df_tratado

    #--------------------UPLOAD CONCORRÊNCIA--------------------#
    conc_file = st.sidebar.file_uploader('Suba os arquivos da concorrência', type=['csv','xlsx'], accept_multiple_files=True)

   
    if conc_file:
        #lista para os CSVs
        dict_concorrentes = {}
        lista_conc= []
        resultados = []
        inter = pd.DataFrame()
        exclusivo = pd.DataFrame()
        brand_l=[]


           
        #--------------------SEPARANDO UPLOADS--------------------#
        for conc_file in conc_file:
            extensao=str(conc_file.name).split('.')[-1]
            if extensao =='csv':
                df=pd.read_csv(conc_file)
            else:
                df=pd.read_excel(conc_file)

            #--------------------NOMEANDO --------------------#
            brand=tldextract.extract(str(df['URL'][0])).domain
            brand_l.append(brand)
            sub=tldextract.extract(str(df['URL'][0])).subdomain
            fi=tldextract.extract(str(df['URL'][0])).suffix
            dominio=brand+'.'+fi
            if len(sub)>1:
                dominio=sub+'.'+brand+'.'+fi
            lista_conc.append(dominio)

            dict_concorrentes[dominio] = df

            dados_confronto[dominio] = set(dict_concorrentes[dominio]['Keyword'])
            #--------------------INTERSEÇÃO--------------------#
            intersecao = keywords_cliente.intersection(
                dados_confronto[dominio]
            )
            #--------------------EXCLUSIVOS--------------------#
            exclusivos_concorrente = (
                dados_confronto[dominio] - keywords_cliente
            )
            exclusivos_cliente = (
                keywords_cliente - dados_confronto[dominio]
            )
            resultados.append({
                'Concorrente': dominio,
                'Keywords em comum': len(intersecao),
                'Exclusivas concorrente': len(exclusivos_concorrente),
                'Exclusivas cliente': len(exclusivos_cliente)
            })
            #--------------------COMPILANDO RESULTADOS--------------------#
            df_resultados = pd.DataFrame(resultados)
            df_melt = df_resultados.melt(
            id_vars='Concorrente',
            var_name='Tipo',
            value_name='Quantidade'
            )

            #--------------------ANÁLISE DE INTERSEÇÃO--------------------#
            analise_inter= pd.DataFrame(intersecao)
            analise_inter=analise_inter.merge(df_up, left_on=0,right_on='Keyword',how='left')
            # dados do concorrente
            analise_inter = analise_inter.merge(
                dict_concorrentes[dominio][['Keyword', 'Position', 'URL']].rename(columns={
                    'Position': f'Posição {dominio}',
                    'URL': f'URL {dominio}'
                }),
                on='Keyword',
                how='left'
            )
            analise_inter['Conc'] = dominio
            inter = pd.concat([inter, analise_inter], ignore_index=True)
        

            #--------------------ANÁLISE DE EXCLUSIVOS--------------------#
            if len(exclusivos_concorrente)>0:
                analise_exclusivos = pd.DataFrame(exclusivos_concorrente)
                
                analise_exclusivos = analise_exclusivos.merge(
                    dict_concorrentes[dominio][['Keyword', 'Position', 'URL', 'Traffic (%)']].rename(columns={
                        'Position': f'Posição {dominio}',
                        'URL': f'URL {dominio}'
                    }),
                    left_on=0,
                    right_on='Keyword',
                    how='left'
                )
                analise_exclusivos['Conc'] = dominio
                exclusivo = pd.concat([exclusivo, analise_exclusivos], ignore_index=True)
                exclusivo=exclusivo.sort_values(by=['Keyword',f'Posição {dominio}']).drop_duplicates(subset=['Keyword'], keep='first')
                exclusivo=exclusivo.sort_values(by=['Traffic (%)'],ascending=False)

        inter=inter.sort_values(by=['Keyword','Position']).drop_duplicates(subset=['Keyword','Conc'], keep='first')
        
        inter=inter.sort_values(by=['Traffic (%)'],ascending=False)

        #--------------------SIDEBAR--------------------#
        if len(dict_concorrentes.keys())>1:
            st.sidebar.divider()
            lista_conc.append('Todos')
            selec=st.sidebar.selectbox('Selecione o concorrente para ver no detalhe',lista_conc)
            st.sidebar.divider()
        resumo=st.sidebar.toggle('Resumo dos dados')
        detail=st.sidebar.toggle('Correlação de termos')
        insights=st.sidebar.toggle('Análise de termos ausentes')

        #--------------------RESUMO DOS DADOS--------------------#
        if resumo:
            if len(dict_concorrentes.keys())>1:
                if selec=='Todos':
                    for i in df_melt['Concorrente'].unique():
                        st.subheader(i)
                        c1,c2,c3 = st.columns(3)
                        x=df_melt[(df_melt['Concorrente']==i)&(df_melt['Tipo']=='Keywords em comum')]['Quantidade']
                        c1.metric(f'Keywords em comum - {i}',x, border=True)
                        x=df_melt[(df_melt['Concorrente']==i)&(df_melt['Tipo']=='Exclusivas concorrente')]['Quantidade']
                        c2.metric(f'Exclusivas concorrente - {i}',x, border=True)
                        x=df_melt[(df_melt['Concorrente']==i)&(df_melt['Tipo']=='Exclusivas cliente')]['Quantidade']
                        c3.metric(f'Exclusivas cliente',x, border=True)
                        plot_sel=df_melt 
                else:
                    st.subheader(selec)
                    plot_sel=df_melt[df_melt['Concorrente']==selec]
                    c1,c2,c3 = st.columns(3)
                    x=df_melt[(df_melt['Concorrente']==selec)&(df_melt['Tipo']=='Keywords em comum')]['Quantidade']
                    c1.metric(f'Keywords em comum - {selec}',x, border=True)
                    x=df_melt[(df_melt['Concorrente']==selec)&(df_melt['Tipo']=='Exclusivas concorrente')]['Quantidade']
                    c2.metric(f'Exclusivas concorrente - {selec}',x, border=True)
                    x=df_melt[(df_melt['Concorrente']==selec)&(df_melt['Tipo']=='Exclusivas cliente')]['Quantidade']
                    c3.metric(f'Exclusivas cliente',x, border=True)
            else:
                selec = dominio
                st.subheader(dominio)
                c1,c2,c3 = st.columns(3)
                x=df_melt[(df_melt['Concorrente']==dominio)&(df_melt['Tipo']=='Keywords em comum')]['Quantidade']
                c1.metric(f'Keywords em comum - {dominio}',x, border=True)
                x=df_melt[(df_melt['Concorrente']==dominio)&(df_melt['Tipo']=='Exclusivas concorrente')]['Quantidade']
                c2.metric(f'Exclusivas concorrente - {dominio}',x, border=True)
                x=df_melt[(df_melt['Concorrente']==dominio)&(df_melt['Tipo']=='Exclusivas cliente')]['Quantidade']
                c3.metric(f'Exclusivas cliente',x, border=True)
                plot_sel=df_melt

            fog = px.sunburst(
            plot_sel,
            path=['Concorrente','Tipo'],
            values='Quantidade',
            title=f'Comparação de keywords {selec}'
            )

            st.plotly_chart(fog)


        #--------------------CORRELAÇÃO DE TERMOS--------------------#
        if detail:
            opt=list(range(1, 101))

            i_pos, f_pos = st.select_slider(
                "Filtre por posição",
                options=opt,
                value=(1, 100)
            )
            st.session_state['inter'] = inter
            iinter=st.session_state['inter']
            filtro_pos_inter= (iinter['Position']>=i_pos)&(iinter['Position']<=f_pos)
            campos = ['Keyword','Search Volume','Position', 'URL']
            if len(dict_concorrentes.keys())>1:                  
                if selec != 'Todos':
                    campos = ['Keyword','Search Volume','Position', f'Posição {selec}','URL', f'URL {selec}', 'Google']
                    df_trato_detail(iinter[(filtro_pos_inter)&(iinter['Conc']==selec)][campos])
                    
                else:
                    for i in iinter['Conc'].unique():
                        campos.append(f'Posição {i}')
                        campos.append(f'URL {i}')
                        campos.append('Google')
                    df_trato_detail(iinter[(iinter['Position']>=i_pos)&(iinter['Position']<=f_pos)][campos])
                    

            else:
                selec = dominio
                campos = ['Keyword','Search Volume','Position', f'Posição {selec}','URL', f'URL {selec}', 'Google']
                df_trato_detail(iinter[filtro_pos_inter][campos])
            if selec == 'Todos':
                for i in list(dict_concorrentes.keys()):
                    x=len(iinter[(iinter['Conc']==i)&(filtro_pos_inter)]['Keyword'].unique())
                    st.metric(f'Keywords em comum - {i}',x, border=True)
            else:
                x=len(iinter[(iinter['Conc']==selec)&(filtro_pos_inter)]['Keyword'].unique())
                st.metric(f'Keywords em comum - {selec}',x, border=True)

        #--------------------ANÁLISE DE TERMOS AUSENTES--------------------#               
        if insights:
            brand_filter=st.multiselect('Filtre pelo regex de marca dos seus concorrentes:',options=brand_l,default=brand_l, accept_new_options=True)
            regex_pattern = '|'.join(brand_filter)
            filter = exclusivo[~exclusivo['Keyword'].str.contains(regex_pattern)]
            campos = ['Keyword']
            if len(dict_concorrentes.keys())>1:
                if selec != 'Todos':
                    tratar_df(filter[(filter['Conc']==selec)])
                else:
                    for i in dict_concorrentes.keys():
                        campos.append(f'Posição {i}')
                        campos.append(f'URL {i}')
                    tratar_df(filter[campos])
            else:
                    tratar_df(filter)
