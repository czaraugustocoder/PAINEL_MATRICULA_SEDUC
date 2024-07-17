import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from streamlit_gsheets import GSheetsConnection

current_working_directory = os.getcwd()

path_logo = os.path.join(current_working_directory, "cets_logo.jpeg")

import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="MATRÍCULAS - REDE ESTADUAL - SEDUC",
                   layout="wide"
)

conn = st.connection("gsheets", type=GSheetsConnection)

dados_dash = conn.read()

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #F5F5F4;
#   }
</style>
""", unsafe_allow_html=True)

st.title('SEDUC')

st.sidebar.image(path_logo)

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

dados_dash_turno = dados_dash.groupby('TURNO')['QTDE-MAT'].sum().reset_index()

fig_ensino = go.Figure(data=[go.Bar(x=dados_dash_ensino['QTDE-MAT'], y=dados_dash_ensino['ENSINO_REDUZIDO'], orientation='h', text=dados_dash_ensino['QTDE-MAT'], textposition='auto')])

fig_turno = go.Figure(data=[go.Pie(labels=dados_dash_turno['TURNO'], values=dados_dash_turno['QTDE-MAT'], hole=.3)])

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_ensino)

with col2:
    st.plotly_chart(fig_turno)

st.write("TABELA DE MATRÍCULAS")
st.dataframe(dados_dash)
st.write("TABELA DE TURMAS COM MATRÍCULA ZERADA")
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
