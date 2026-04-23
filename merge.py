import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title('🔗Junta planilha 2000')

up_file = st.file_uploader('Escolha um arquivo CSV', type='csv', accept_multiple_files=True)

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
    #lista para os CSVs
    lista_dfs = []
    st.write('Arquivos lidos com sucesso!')
    #juntando os CSVs
    for up_file in up_file:
        df = pd.read_csv(up_file)
        lista_dfs.append(df)
    df_final = pd.concat(lista_dfs, ignore_index=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar CSV", shortcut="Ctrl+S", type="primary", width="stretch"):
            df_final.to_csv('juntas.csv')
    with col2:
        if st.button("Salvar Excel", shortcut="Ctrl+S", type="primary", width="stretch"):
            df_final.to_excel('juntas.xlsx')
    tratar_df(df_final)