import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from upsetplot import from_contents, plot

st.title('🔗Análise de concorrência 2000')
c1,c2 = st.columns(2)
with c1:
    up_file = st.file_uploader('Suba o arquivo CSV do seu cliente', type='csv', accept_multiple_files=False)


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

if up_file:
    df=pd.read_csv(up_file)
    x=set(df['Keyword'])
    dados_confronto = {"TIM": x}
    with c2:
        conc_file = st.file_uploader('Suba os arquivos da concorrência', type='csv', accept_multiple_files=True)
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
        mapa_intersecao = from_contents(dados_confronto)


        # Cria o diagrama
        fig = plt.figure(figsize=(10, 6))
        plot(mapa_intersecao, fig=fig, element_size=None)
        st.pyplot(fig)
