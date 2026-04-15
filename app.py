import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests
import time
import os
from docx import Document
from io import BytesIO
from datetime import datetime

# --- CONFIGURAÇÕES CLOUDINARY ---
cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

st.set_page_config(page_title="CRM AMG Multimarcas", page_icon="🚗", layout="wide")

# --- FUNÇÃO DATA EXTENSA ---
def obter_data_extensa():
    meses = {1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL", 5: "MAIO", 6: "JUNHO", 
             7: "JULHO", 8: "AGOSTO", 9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"}
    hoje = datetime.now()
    return f"{hoje.day} DE {meses[hoje.month]} DE {hoje.year}"

# --- FUNÇÃO DOCX ---
def preencher_procuracao(dados_carro, dados_procurador):
    caminho = "modelo_procuracao.docx"
    if not os.path.exists(caminho): return None
    try:
        doc = Document(caminho)
        subs = {
            "{{NOME_TITULAR}}": str(dados_carro.get('nome_titular', '')).upper(),
            "{{CPF}}": str(dados_carro.get('cpf_titular', '')),
            "{{RG}}": str(dados_carro.get('rg_titular', '')),
            "{{RUA}}": str(dados_carro.get('endereco_titular', '')).upper(),
            "{{NRUA}}": str(dados_carro.get('tit_num', '')),
            "{{BAIRRO}}": str(dados_carro.get('tit_bairro', '')).upper(),
            "{{CIDADE}}": "GRAVATAÍ",
            "{{UF}}": str(dados_carro.get('tit_est', 'RS')).upper(),
            "{{PLACA}}": str(dados_carro.get('placa', '')).upper(),
            "{{CHASSI}}": str(dados_carro.get('chassi', '')).upper(),
            "{{RENAVAM}}": str(dados_carro.get('renavam', '')),
            "{{MARCAMODELO}}": f"{dados_carro.get('marca', '')} {dados_carro.get('modelo', '')}".upper(),
            "{{COR}}": str(dados_carro.get('cor', '')).upper(),
            "{{ANO}}": str(dados_carro.get('ano', '')),
            "{{DATA}}": obter_data_extensa(),
            "{{NNOME}}": str(dados_procurador.get('nome', '')).upper(), 
            "{{NCPF}}": str(dados_procurador.get('cpf', '')),
            "{{NRG}}": str(dados_procurador.get('rg', ''))
        }
        for p in doc.paragraphs:
            for k, v in subs.items():
                if k in p.text:
                    for run in p.runs:
                        if k in run.text: run.text = run.text.replace(k, v)
        for t in doc.tables:
            for r in t.rows:
                for c in r.cells:
                    for p in c.paragraphs:
                        for k, v in subs.items():
                            if k in p.text:
                                for run in p.runs:
                                    if k in run.text: run.text = run.text.replace(k, v)
        buf = BytesIO(); doc.save(buf); buf.seek(0)
        return buf
    except: return None

# --- CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

menu = st.sidebar.radio("Navegação", ["➕ Novo Cadastro", "📑 Estoque", "👥 Procuradores"])

# --- ABA: NOVO CADASTRO (IGUAL ANTES) ---
if menu == "➕ Novo Cadastro":
    st.markdown("## 📝 Novo Cadastro de Veículo")
    try:
        marcas = requests.get("https://fipe.parallelum.com.br/api/v2/cars/brands").json()
        dict_marcas = {m['name']: m['code'] for m in marcas}
        marca_n = st.selectbox("1. Selecione a Marca", options=[""] + sorted(list(dict_marcas.keys())))
    except: marca_n = None

    if marca_n:
        modelos = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{dict_marcas[marca_n]}/models").json()
        dict_modelos = {m['name']: m['code'] for m in modelos}
        modelo_n = st.selectbox("2. Selecione o Modelo", options=[""] + sorted(list(dict_modelos.keys())))

        if modelo_n:
            anos = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{dict_marcas[marca_n]}/models/{dict_modelos[modelo_n]}/years").json()
            dict_anos = {a['name']: a['code'] for a in anos}
            ano_sel = st.selectbox("3. Selecione o Ano", options=[""] + list(dict_anos.keys()))

            if ano_sel:
                fipe = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{dict_marcas[marca_n]}/models/{dict_modelos[modelo_n]}/years/{dict_anos[ano_sel]}").json()
                
                with st.form("form_completo"):
                    st.subheader("🚗 Dados do Veículo")
                    c1, c2 = st.columns(2)
                    v_marca = c1.text_input("Marca", value=fipe.get('brand'))
                    v_modelo = c1.text_input("Modelo", value=fipe.get('model'))
                    v_placa = c1.text_input("Placa").upper()
                    v_foto = c1.file_uploader("Foto Principal", type=['jpg','png','jpeg'])
                    
                    v_renavam = c2.text_input("Renavam")
                    v_chassi = c2.text_input("Chassi")
                    v_cor = c2.text_input("Cor")
                    v_ano = c2.text_input("Ano Modelo", value=ano_sel)

                    st.markdown("---")
                    st.subheader("📑 Dados do Proprietário")
                    cc1, cc2 = st.columns(2)
                    t_nome = cc1.text_input("Nome Completo")
                    t_cpf = cc1.text_input("CPF")
                    t_rg = cc2.text_input("RG")
                    t_rua = cc2.text_input("Rua / Logradouro")
                    
                    cc3, cc4, cc5 = st.columns([1, 2, 1])
                    t_num = cc3.text_input("Nº")
                    t_bairro = cc4.text_input("Bairro")
                    t_est = cc5.selectbox("UF", ["RS", "SC", "PR", "SP"])

                    if st.form_submit_button("🚀 SALVAR NO ESTOQUE"):
                        img_url = cloudinary.uploader.upload(v_foto)['secure_url'] if v_foto else ""
                        df_atual = conn.read(worksheet="Estoque", ttl=0).astype(str)
                        novo_veic = pd.DataFrame([{
                            "marca": v_marca, "modelo": v_modelo, "placa": v_placa, "foto": img_url,
                            "renavam": v_renavam, "chassi": v_chassi, "cor": v_cor, "ano": v_ano,
                            "nome_titular": t_nome, "cpf_titular": t_cpf, "rg_titular": t_rg,
                            "endereco_titular": t_rua, "tit_num": t_num, "tit_bairro": t_bairro,
                            "tit_cid": "GRAVATAÍ", "tit_est": t_est
                        }])
                        conn.update(worksheet="Estoque", data=pd.concat([df_atual, novo_veic], ignore_index=True))
                        st.success("✅ Veículo Cadastrado!"); time.sleep(1); st.rerun()

# --- OUTRAS ABAS (ESTOQUE E PROCURADORES) ---
elif menu == "📑 Estoque":
    st.header("Gerenciar Estoque")
    try:
        df = conn.read(worksheet="Estoque", ttl=0).astype(str)
        df_p = conn.read(worksheet="Procuradores", ttl=0).astype(str)
        procs = df_p['nome'].tolist()
        for i, r in df.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                if r.get('foto'): c1.image(r['foto'], use_container_width=True)
                c2.subheader(f"{r['marca']} {r['modelo']} ({r['placa']})")
                if procs:
                    p_sel = c2.selectbox("Procurador:", procs, key=f"s{i}")
                    dados_p = df_p[df_p['nome'] == p_sel].iloc[0].to_dict()
                    doc = preencher_procuracao(r, dados_p)
                    if doc: c2.download_button("📜 Baixar Procuração", doc, f"Procuracao_{r['placa']}.docx", key=f"d{i}")
                if c2.button("🗑️ Excluir", key=f"del{i}"):
                    conn.update(worksheet="Estoque", data=df.drop(i)); st.rerun()
    except: st.error("Erro ao carregar dados.")

elif menu == "👥 Procuradores":
    st.subheader("Cadastrar Procurador")
    with st.form("f_p"):
        n, c, r = st.text_input("Nome"), st.text_input("CPF"), st.text_input("RG")
        if st.form_submit_button("Salvar"):
            df_p = conn.read(worksheet="Procuradores", ttl=0).astype(str)
            conn.update(worksheet="Procuradores", data=pd.concat([df_p, pd.DataFrame([{"nome":n,"cpf":c,"rg":r}])]))
            st.success("Salvo!"); st.rerun()
