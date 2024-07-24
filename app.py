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

dados_dash = conn.read(
    worksheet="TXTTURMA",
    ttl="60m"
)

data_atualizacao = dados_dash['DATA DE ATUALIZAÇÃO'][0]

dados_dash = dados_dash.iloc[:,:-1]

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #F5F5F4;
#   }
</style>
""", unsafe_allow_html=True)

title = str(f"TXTTURMA ({data_atualizacao}) - GEPES/DEPLAN/SEDUC")

st.title(title)

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

ensino_2 = st.sidebar.multiselect(
    "Selecione a Modalidade",
    options= dados_dash["ENSINO_REDUZIDO"].unique()
)

ensino_1 = st.sidebar.multiselect(
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
if ((len(ensino_1) != 0)):
    print(ensino_1)
    dados_dash = dados_dash.query(
        "ENSINO == @ensino_1")
if ((len(ensino_2) != 0)):
    print(ensino_2)
    dados_dash = dados_dash.query(
        "ENSINO_REDUZIDO == @ensino_2")
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
QTD_TURMAS_ZERADAS = len(TURMAS_ZERO['MUNICIPIO'])
TURMAS_ZERADAS_MUN = TURMAS_ZERO.groupby('MUNICIPIO')['COD-TURMA'].count().reset_index()
TURMAS_ZERADAS_MUN.rename(columns={'COD-TURMA': 'QTDE-ABS'}, inplace=True)
TURMAS_ZERADAS_MUN['QTDE-REL(%)'] = (TURMAS_ZERADAS_MUN['QTDE-ABS'] / QTD_TURMAS_ZERADAS) * 100

ESCOLAS = dados_dash.loc[dados_dash['ESCOLA-ANEXA'] == "-"]['ESCOLA'].nunique()
print(ESCOLAS)

ESCOLAS_ANEXAS = dados_dash.loc[dados_dash['ESCOLA-ANEXA'] != "-"]['ESCOLA'].nunique()
print(ESCOLAS_ANEXAS)

a1, a2, a3, a4, a5 = st.columns(5)
a1.metric("QTD-MATRICULA ", f"{QTD_MAT}")
a2.metric("TURMAS ",f"{TURMAS}")
a3.metric("TURMAS ZERADAS ",f"{TURMAS_ZERADAS}")
a4.metric("ESCOLAS ",f"{ESCOLAS}")
a5.metric("ANEXOS ",f"{ESCOLAS_ANEXAS}")

dados_dash_ensino = dados_dash.groupby('ENSINO_REDUZIDO')['QTDE-MAT'].sum().reset_index()

dados_dash_ensino = dados_dash_ensino.sort_values(by='QTDE-MAT')

dados_dash_turno = dados_dash.groupby('TURNO')['QTDE-MAT'].sum().reset_index()

dados_dash_sala = dados_dash.groupby('TIPO-SALA')['QTDE-MAT'].sum().reset_index()

fig_ensino = go.Figure(data=[go.Bar(x=dados_dash_ensino['QTDE-MAT'], y=dados_dash_ensino['ENSINO_REDUZIDO'], orientation='h', text=dados_dash_ensino['QTDE-MAT'], textposition='auto')])

fig_ensino.update_layout(
    title='QTDE-MAT POR MODALIDADE'
)

fig_turno = go.Figure(data=[go.Pie(labels=dados_dash_turno['TURNO'], values=dados_dash_turno['QTDE-MAT'], hole=.3)])

fig_turno.update_layout(
    title='QTDE-MAT POR TURNO'
)

fig_sala = go.Figure(data=[go.Bar(x=dados_dash_sala['TIPO-SALA'], y=dados_dash_sala['QTDE-MAT'], orientation='v', text=dados_dash_sala['QTDE-MAT'], textposition='auto')])

fig_sala.update_layout(
    title='QTDE-MAT POR TIPO DE SALA'
)

col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(fig_ensino)
with col2:
    st.plotly_chart(fig_turno)
with col3:
    st.plotly_chart(fig_sala)

st.write("TABELA DE MATRÍCULAS")
st.dataframe(dados_dash)
st.write("TABELA DE TURMAS COM MATRÍCULA ZERADA")
col1, col2 = st.columns(2)
with col1:
    st.dataframe(TURMAS_ZERO)
with col2:
  st.dataframe(TURMAS_ZERADAS_MUN)

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
