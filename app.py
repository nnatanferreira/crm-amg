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

# --- 1. CONFIGURAÇÕES CLOUDINARY ---
cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

st.set_page_config(page_title="CRM AMG Multimarcas", page_icon="🚗", layout="wide")

# --- 2. SEGURANÇA E SESSÃO (1 HORA) ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "login_time" not in st.session_state:
    st.session_state["login_time"] = 0

if st.session_state["autenticado"]:
    if time.time() - st.session_state["login_time"] > 3600:
        st.session_state["autenticado"] = False
        st.rerun()

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🚗 CRM AMG MULTIMARCAS</h1>", unsafe_allow_html=True)
    with st.container():
        st.info("Acesso restrito. Entre com suas credenciais.")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Acessar Painel"):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.session_state["login_time"] = time.time()
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    st.stop()

# --- 3. CONEXÃO E FUNÇÕES ---
conn = st.connection("gsheets", type=GSheetsConnection)

def obter_data_extensa():
    meses = {1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL", 5: "MAIO", 6: "JUNHO", 
             7: "JULHO", 8: "AGOSTO", 9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"}
    hoje = datetime.now()
    return f"{hoje.day} DE {meses[hoje.month]} DE {hoje.year}"

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

# --- 4. INTERFACE ---
menu = st.sidebar.radio("Navegação", ["➕ Novo Cadastro", "📑 Estoque", "👥 Procuradores"])
if st.sidebar.button("Sair (Logoff)"):
    st.session_state["autenticado"] = False
    st.rerun()

# --- ABA: NOVO CADASTRO ---
if menu == "➕ Novo Cadastro":
    st.subheader("📝 Novo Cadastro (FIPE + CRM)")
    try:
        marcas = requests.get("https://fipe.parallelum.com.br/api/v2/cars/brands").json()
        dict_marcas = {m['name']: m['code'] for m in marcas}
        marca_n = st.selectbox("1. Marca", options=[""] + sorted(list(dict_marcas.keys())))
        
        if marca_n:
            modelos = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{dict_marcas[marca_n]}/models").json()
            dict_modelos = {m['name']: m['code'] for m in modelos}
            modelo_n = st.selectbox("2. Modelo", options=[""] + sorted(list(dict_modelos.keys())))

            if modelo_n:
                anos = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{dict_marcas[marca_n]}/models/{dict_modelos[modelo_n]}/years").json()
                dict_anos = {a['name']: a['code'] for a in anos}
                ano_sel = st.selectbox("3. Ano", options=[""] + list(dict_anos.keys()))

                if ano_sel:
                    fipe = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{dict_marcas[marca_n]}/models/{dict_modelos[modelo_n]}/years/{dict_anos[ano_sel]}").json()
                    with st.form("f_cadastro"):
                        st.subheader("🚗 Dados do Veículo")
                        c1, c2 = st.columns(2)
                        v_marca = c1.text_input("Marca", value=fipe.get('brand'))
                        v_modelo = c1.text_input("Modelo", value=fipe.get('model'))
                        v_placa = c1.text_input("Placa").upper().strip()
                        v_valor = c1.text_input("Valor de Venda", value=fipe.get('price')) # VALOR RESTAURADO
                        v_foto = c1.file_uploader("Foto Principal", type=['jpg','png','jpeg'])
                        
                        v_renavam = c2.text_input("Renavam")
                        v_chassi = c2.text_input("Chassi").strip()
                        v_cor = c2.text_input("Cor")
                        v_ano = c2.text_input("Ano Modelo", value=ano_sel)
                        
                        st.markdown("---")
                        st.write("👤 **Dados do Proprietário**")
                        cc1, cc2 = st.columns(2)
                        t_nome, t_cpf = cc1.text_input("Nome Completo"), cc1.text_input("CPF").strip()
                        t_rg, t_rua = cc2.text_input("RG"), cc2.text_input("Rua/Logradouro")
                        cc3, cc4, cc5 = st.columns([1, 2, 1])
                        t_num, t_bairro, t_est = cc3.text_input("Nº"), cc4.text_input("Bairro"), cc5.selectbox("UF", ["RS", "SC", "PR", "SP"])

                        if st.form_submit_button("🚀 SALVAR E PUBLICAR"):
                            url = cloudinary.uploader.upload(v_foto)['secure_url'] if v_foto else ""
                            try: df_e = conn.read(worksheet="Estoque", ttl=0).astype(str)
                            except: df_e = pd.DataFrame()
                            
                            novo = pd.DataFrame([{
                                "marca": v_marca, "modelo": v_modelo, "placa": v_placa, "valor": v_valor, "foto": url, 
                                "renavam": v_renavam, "chassi": v_chassi, "cor": v_cor, "ano": v_ano, 
                                "nome_titular": t_nome, "cpf_titular": t_cpf, "rg_titular": t_rg, 
                                "endereco_titular": t_rua, "tit_num": t_num, "tit_bairro": t_bairro, 
                                "tit_cid": "GRAVATAÍ", "tit_est": t_est
                            }])
                            conn.update(worksheet="Estoque", data=pd.concat([df_e, novo], ignore_index=True))
                            st.success("✅ Salvo com sucesso!"); time.sleep(1); st.rerun()
    except: st.error("Erro ao carregar dados da FIPE.")

# --- ABA: ESTOQUE ---
elif menu == "📑 Estoque":
    st.header("📑 Gerenciar Estoque")
    try:
        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all').astype(str)
        df_p = conn.read(worksheet="Procuradores", ttl=0).astype(str)
        procs = df_p['nome'].tolist() if not df_p.empty else []
        
        if df.empty: st.info("Estoque vazio.")
        else:
            for i, r in df.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 2])
                    if r.get('foto') and "http" in str(r['foto']): c1.image(r['foto'], use_container_width=True)
                    
                    c2.subheader(f"{r['marca']} {r['modelo']} | {r['placa']}")
                    c2.write(f"**Valor:** {r.get('valor', 'R$ 0,00')} | **Titular:** {r['nome_titular']}")
                    
                    if procs:
                        cs, cb = c2.columns([2, 1])
                        p_sel = cs.selectbox("Procurador:", procs, key=f"s{i}")
                        dados_p = df_p[df_p['nome'] == p_sel].iloc[0].to_dict()
                        doc = preencher_procuracao(r, dados_p)
                        if doc: cb.download_button("📥 Procuração", doc, f"Procuracao_{r['placa']}.docx", key=f"d{i}")
                    
                    if c2.button("🗑️ Excluir", key=f"del{i}"):
                        conn.update(worksheet="Estoque", data=df.drop(i).astype(str))
                        st.rerun()
    except: st.error("Erro na planilha.")

# --- ABA: PROCURADORES ---
elif menu == "👥 Procuradores":
    st.subheader("👥 Cadastro de Procuradores")
    with st.form("f_p_add"):
        n, c, r = st.text_input("Nome Completo"), st.text_input("CPF"), st.text_input("RG")
        if st.form_submit_button("Salvar"):
            try: df_p = conn.read(worksheet="Procuradores", ttl=0).astype(str)
            except: df_p = pd.DataFrame(columns=["nome", "cpf", "rg"])
            conn.update(worksheet="Procuradores", data=pd.concat([df_p, pd.DataFrame([{"nome":n,"cpf":c,"rg":r}])], ignore_index=True))
            st.success("✅ Salvo!"); st.rerun()
