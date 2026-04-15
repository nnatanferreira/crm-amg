import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import os
import locale
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

# --- FUNÇÃO PARA FORMATAR DATA EXTENSA ---
def obter_data_extensa():
    meses = {
        1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL",
        5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO",
        9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
    }
    hoje = datetime.now()
    return f"{hoje.day} DE {meses[hoje.month]} DE {hoje.year}"

# --- FUNÇÃO DE PREENCHIMENTO (PRESERVA FORMATAÇÃO) ---
def preencher_procuracao(dados_carro, dados_procurador):
    caminho = "modelo_procuracao.docx"
    if not os.path.exists(caminho):
        return None
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

        # Substituição preservando estilos (Runs)
        for p in doc.paragraphs:
            for k, v in subs.items():
                if k in p.text:
                    # Isso garante que a formatação original do Word seja mantida
                    for run in p.runs:
                        if k in run.text:
                            run.text = run.text.replace(k, v)

        for t in doc.tables:
            for r in t.rows:
                for c in r.cells:
                    for p in c.paragraphs:
                        for k, v in subs.items():
                            if k in p.text:
                                for run in p.runs:
                                    if k in run.text:
                                        run.text = run.text.replace(k, v)
        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf
    except: return None

# --- CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- INTERFACE ---
menu = st.sidebar.radio("Navegação", ["➕ Novo Cadastro", "📑 Estoque", "👥 Procuradores"])

# --- ABA: PROCURADORES ---
if menu == "👥 Procuradores":
    st.subheader("Cadastrar Novo Procurador")
    with st.form("f_p"):
        n, c, r = st.text_input("Nome"), st.text_input("CPF"), st.text_input("RG")
        if st.form_submit_button("Salvar"):
            try: df_p = conn.read(worksheet="Procuradores", ttl=0).astype(str)
            except: df_p = pd.DataFrame(columns=["nome","cpf","rg"])
            conn.update(worksheet="Procuradores", data=pd.concat([df_p, pd.DataFrame([{"nome":n,"cpf":c,"rg":r}])]))
            st.success("Salvo!"); st.rerun()

# --- ABA: NOVO CADASTRO ---
elif menu == "➕ Novo Cadastro":
    st.header("Novo Veículo")
    with st.form("f_v"):
        c1, c2 = st.columns(2)
        marca = c1.text_input("Marca")
        modelo = c1.text_input("Modelo")
        placa = c1.text_input("Placa").upper()
        renavam = c1.text_input("Renavam")
        chassi = c1.text_input("Chassi")
        foto = c1.file_uploader("Foto Principal", type=['jpg','png','jpeg'])
        
        nome_t = c2.text_input("Nome Titular")
        cpf_t = c2.text_input("CPF Titular")
        rg_t = c2.text_input("RG Titular")
        rua_t = c2.text_input("Endereço (Rua)")
        bairro_t = c2.text_input("Bairro")
        num_t = c2.text_input("Número")
        ano_v = c2.text_input("Ano Modelo")
        
        if st.form_submit_button("Cadastrar no Sistema"):
            url = cloudinary.uploader.upload(foto)['secure_url'] if foto else ""
            try: df = conn.read(worksheet="Estoque", ttl=0).astype(str)
            except: df = pd.DataFrame()
            novo = pd.DataFrame([{"marca":marca,"modelo":modelo,"placa":placa,"renavam":renavam,"chassi":chassi,"foto":url,"nome_titular":nome_t,"cpf_titular":cpf_t,"rg_titular":rg_t,"endereco_titular":rua_t,"tit_bairro":bairro_t,"tit_num":num_t,"ano":ano_v}])
            conn.update(worksheet="Estoque", data=pd.concat([df, novo]))
            st.success("Veículo Cadastrado!"); st.rerun()

# --- ABA: ESTOQUE ---
elif menu == "📑 Estoque":
    st.header("Estoque e Documentos")
    try:
        df = conn.read(worksheet="Estoque", ttl=0).astype(str)
        df_p = conn.read(worksheet="Procuradores", ttl=0).astype(str)
        procs = df_p['nome'].tolist()
    except:
        st.error("Erro ao ler planilhas. Verifique as abas 'Estoque' e 'Procuradores'.")
        st.stop()

    for i, row in df.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([1, 2])
            if row.get('foto') and "http" in str(row['foto']):
                c1.image(str(row['foto']), use_container_width=True)
            else: c1.info("Sem foto")

            c2.subheader(f"{row.get('marca','')} {row.get('modelo','')} - {row.get('placa','')}")
            
            if procs:
                col_sel, col_btn = c2.columns([2,1])
                p_sel = col_sel.selectbox("Assinar como:", procs, key=f"s{i}")
                dados_p = df_p[df_p['nome'] == p_sel].iloc[0].to_dict()
                doc = preencher_procuracao(row, dados_p)
                if doc:
                    col_btn.download_button("📜 Baixar Procuração", doc, f"Procuracao_{row['placa']}.docx", key=f"d{i}")
            else: c2.warning("Cadastre um procurador no menu ao lado.")
            
            if c2.button("🗑️ Excluir", key=f"del{i}"):
                conn.update(worksheet="Estoque", data=df.drop(i))
                st.rerun()
