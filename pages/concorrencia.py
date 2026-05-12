import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn2,venn3

st.title('🔗Análise de concorrência 2000')

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

c1,c2 = st.columns(2)

if 'data' not in st.session_state:
    with c1:
        up_file = st.sidebar.file_uploader('Suba o arquivo CSV do seu cliente', type=['csv','xlsx'], accept_multiple_files=False)
    if up_file:
        extensao=str(up_file.name).split('.')[-1]
        if extensao =='csv':
            df=pd.read_csv(up_file)
        else:
            df=pd.read_excel(up_file)
        st.write(f'Arquivo .{extensao} lido com sucesso!')
        st.session_state['data'] = df 
        df_up= st.session_state['data']

if 'data' in st.session_state:
    df_up= st.session_state['data']
    x=set(df_up['Keyword'])
    st.write(df_up)
    dados_confronto = {"TIM": x}
    with c2:
        conc_file = st.file_uploader('Suba os arquivos da concorrência', type=['csv','xlsx'], accept_multiple_files=True)
    if conc_file:
        #lista para os CSVs
        dict_concorrentes = {}
        
        st.write('Arquivos lidos com sucesso!')
        #juntando os CSVs
        for conc_file in conc_file:
            df = pd.read_csv(conc_file)
            dict_concorrentes[conc_file.name] = df
            st.write(conc_file.name)
            tratar_df(dict_concorrentes[conc_file.name])
            dados_confronto[conc_file.name] = set(dict_concorrentes[conc_file.name]['Keyword'])
        venn2([dados_confronto[conc_file.name]])


        # Cria o diagrama
        fig = plt.figure(figsize=(10, 6))
        plot(mapa_intersecao, fig=fig, element_size=None)
        st.pyplot(fig)
