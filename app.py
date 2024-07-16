import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

current_working_directory = os.getcwd()

path_token = os.path.join(current_working_directory, "turmas-gepes-planilha-f3e630cb4bec.json")

path_logo = os.path.join(current_working_directory, "cets_logo.jpeg")


import warnings
warnings.filterwarnings("ignore")

scope = ['https://spreadsheets.google.com/feeds']

credentials = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\03206881277\Desktop\CODE\STREAMLIT_PAINEL_MATRICULA\turmas-gepes-planilha-f3e630cb4bec.json', scope)

gc = gspread.authorize(credentials)

wks = gc.open_by_key('1BiEpIPjLaAGjfgdN4qjmH3bbKD8zno9Py3nwiktUTQE').worksheet('BASE')

dados = wks.get_all_values()

data = []

colunas = dados[0]

# Imprimir os dados
for linha in dados[1:]:
    data.append(linha)

dados_dash = pd.DataFrame(data, columns=colunas)

st.set_page_config(page_title="MATRÍCULAS - REDE ESTADUAL - SEDUC",
                   layout="wide"
)

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #F5F5F4;
    }
</style>
""", unsafe_allow_html=True)

st.title('SEDUC')

st.sidebar.image(r"C:\Users\03206881277\Desktop\CODE\STREAMLIT_PAINEL_MATRICULA\cets_logo.jpeg")

st.sidebar.header("Filtre as opções que deseja:")

local = st.sidebar.multiselect(
    "Selecione a Localização",
    options= dados_dash["LOCALIZACAO"].unique()
)

mun = st.sidebar.multiselect(
    "Selecione o Município",
    options= dados_dash["MUNICIPIO"].unique()
)

escola = st.sidebar.multiselect(
    "Selecione a Escola",
    options= dados_dash["ESCOLA"].unique()
)

ensino = st.sidebar.multiselect(
    "Selecione o Ensino",
    options= dados_dash["ENSINO"].unique()
)

projeto = st.sidebar.multiselect(
    "Selecione o Projeto",
    options= dados_dash["PROJETO"].unique()
)

turno = st.sidebar.multiselect(
    "Selecione o Turno",
    options= dados_dash["TURNO"].unique()
)

fase = st.sidebar.multiselect(
    "Selecione o fase",
    options= dados_dash["FASE"].unique()
)

if ((len(local) != 0)):
    print(local)
    dados_dash = dados_dash.query(
        "LOCALIZACAO == @local")
if ((len(mun) != 0)):
    print(mun)
    dados_dash = dados_dash.query(
        "MUNICIPIO == @mun")
if ((len(escola) != 0)):
    print(escola)
    dados_dash = dados_dash.query(
        "ESCOLA == @escola")
if ((len(ensino) != 0)):
    print(ensino)
    dados_dash = dados_dash.query(
        "ENSINO == @ensino")
if ((len(projeto) != 0)):
    print(projeto)
    dados_dash = dados_dash.query(
        "PROJETO == @projeto")
if ((len(turno) != 0)):
    print(turno)
    dados_dash = dados_dash.query(
        "TURNO == @turno")
if ((len(fase) != 0)):
    print(fase)
    dados_dash = dados_dash.query(
        "FASE == @fase")
    
dados_dash['QTDE-MAT'] = dados_dash['QTDE-MAT'].astype('int64') 
    
QTD_MAT = dados_dash['QTDE-MAT'].sum()
print(QTD_MAT)

TURMAS = dados_dash['COD-TURMA'].count()
print(TURMAS)

TURMAS_ZERO = dados_dash.loc[dados_dash['QTDE-MAT'] == 0]
TURMAS_ZERADAS = TURMAS_ZERO['COD-TURMA'].count()

ESCOLAS = dados_dash['ESCOLA'].nunique()
print(ESCOLAS)

a1, a2, a3, a4 = st.columns(4)
a1.metric("QTD-MATRICULA ", f"{QTD_MAT}")
a2.metric("TURMAS ",f"{TURMAS}")
a3.metric("TURMAS ZERADAS ",f"{TURMAS_ZERADAS}")
a4.metric("ESCOLAS ",f"{ESCOLAS}")

dados_dash_ensino = dados_dash.groupby('ENSINO_REDUZIDO')['QTDE-MAT'].sum().reset_index()

fig_ensino = go.Figure(data=[go.Bar(x=dados_dash_ensino['ENSINO_REDUZIDO'], y=dados_dash_ensino['QTDE-MAT'], textposition='outside')])

#st.plotly_chart(fig_ensino)

st.write("TABELAS DE MATRÍCULAS")
st.dataframe(dados_dash)

st.write("TABELAS DE TURMAS COM MATRÍCULA ZERADA")
st.dataframe(TURMAS_ZERO)

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

csv = convert_df(dados_dash)

st.download_button(
    label="Download",
    data=csv,
    file_name="large_df.csv",
    mime="text/csv",
)
