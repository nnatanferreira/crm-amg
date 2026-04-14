import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests # Biblioteca para chamar a API da FIPE

# --- 1. CONFIGURAÇÕES ---
API_FIPE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI0ZDk3YTE4NC1kOGIzLTQwOTEtOWVhOC1kNWQ0ZGUzYWZiNWQiLCJlbWFpbCI6Im5uYXRhbmZlcnJlaXJhQGdtYWlsLmNvbSIsImlhdCI6MTc3NjIwMTM4NH0.v_0pe0vEEuLCIMenEsLWZXSl_hdkXVq4oTzfhT4kdXM"

cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

st.set_page_config(page_title="CRM AMG Multimarcas", page_icon="🚗", layout="wide")

# --- 2. FUNÇÃO DE CONSULTA API ---
def consultar_dados_veiculo(placa):
    try:
        url = f"https://api.fipe.online/v1/veiculos/{placa}"
        headers = {"Authorization": f"Bearer {API_FIPE_KEY}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #f8f9fa !important; }
    [data-testid="stWidgetLabel"] p { font-size: 1.2rem !important; font-weight: 600; }
    .stButton button { font-size: 1.5rem !important; font-weight: 800 !important; height: 70px !important; border-radius: 12px !important; }
    .car-card { border: 2px solid #eee; border-radius: 20px; padding: 20px; background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.markdown("<h1 style='text-align: center;'>🚗 AMG Multimarcas</h1>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR"):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
else:
    menu = st.sidebar.radio("Navegar:", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])

    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Cadastro Automático por Placa")
        
        # Busca inicial por placa
        col_p1, col_p2 = st.columns([2,1])
        placa_para_busca = col_p1.text_input("Digite a Placa:", placeholder="ABC1D23").upper()
        
        # Estado para armazenar dados da consulta
        if "dados_fipe" not in st.session_state:
            st.session_state.dados_fipe = {}

        if col_p2.button("🔍 Puxar Dados"):
            if placa_para_busca:
                with st.spinner("Consultando base da FIPE..."):
                    resultado = consultar_dados_veiculo(placa_para_busca)
                    if resultado:
                        st.session_state.dados_fipe = resultado
                        st.success("Dados encontrados!")
                    else:
                        st.error("Placa não encontrada ou erro na API.")
            else:
                st.warning("Digite uma placa.")

        # FORMULÁRIO (Preenchido com dados da API ou manual)
        with st.form("form_veiculo", clear_on_submit=True):
            d = st.session_state.dados_fipe
            
            st.subheader("🚗 Informações do Veículo")
            c1, c2, c3 = st.columns([1, 1.5, 1])
            with c1:
                marca_auto = d.get("marca", "")
                marca = st.text_input("Marca", value=marca_auto)
            with c2:
                modelo_auto = d.get("modelo", "")
                modelo = st.text_input("Modelo e Versão", value=modelo_auto)
            with c3:
                placa = st.text_input("Placa Final", value=placa_para_busca)

            d1, d2, d3 = st.columns(3)
            with d1:
                ano_f = d.get("ano_fabricacao", "")
                ano_fab = st.text_input("Ano Fabricação", value=str(ano_f))
                renavam = st.text_input("Renavam", value=d.get("renavam", ""))
            with d2:
                ano_m = d.get("ano_modelo", "")
                ano_mod = st.text_input("Ano Modelo", value=str(ano_m))
                chassi = st.text_input("Chassi", value=d.get("chassi", ""))
            with d3:
                cor = st.text_input("Cor", value=d.get("cor", ""))
                combustivel = st.text_input("Combustível", value=d.get("combustivel", ""))

            st.markdown("---")
            v1, v2 = st.columns(2)
            with v1:
                preco_fipe = d.get("preco_fipe", 0.0)
                preco = st.number_input("Preço de Venda (R$)", value=float(preco_fipe), step=500.0)
                km = st.number_input("Quilometragem", min_value=0)
            with v2:
                foto_v_file = st.file_uploader("📷 Foto Principal", type=['jpg', 'jpeg', 'png'])

            st.markdown("---")
            st.subheader("👤 Proprietário / Titular (Opcional)")
            t1, t2 = st.columns(2)
            with t1:
                nome_titular = st.text_input("Nome Completo do Titular")
                cpf_titular = st.text_input("CPF do Titular")
                rg_titular = st.text_input("RG do Titular")
            with t2:
                endereco_titular = st.text_input("Endereço Completo")
                doc_titular_file = st.file_uploader("📂 Foto do Documento", type=['jpg', 'jpeg', 'png'])

            if st.form_submit_button("🚀 SALVAR NO ESTOQUE"):
                if modelo and placa and foto_v_file:
                    with st.spinner('Salvando...'):
                        res_carro = cloudinary.uploader.upload(foto_v_file)
                        url_doc = ""
                        if doc_titular_file:
                            res_doc = cloudinary.uploader.upload(doc_titular_file)
                            url_doc = res_doc['secure_url']

                        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                        novo = pd.DataFrame([{
                            "marca": marca, "modelo": modelo, "placa": placa.upper(),
                            "ano_fab": str(ano_fab), "ano_mod": str(ano_mod),
                            "renavam": renavam, "chassi": chassi.upper(),
                            "cor": cor, "combustivel": combustivel,
                            "preco": preco, "km": km, "foto": res_carro['secure_url'],
                            "nome_titular": nome_titular, "cpf_titular": cpf_titular,
                            "rg_titular": rg_titular, "endereco_titular": endereco_titular,
                            "doc_titular": url_doc
                        }])
                        conn.update(worksheet="Estoque", data=pd.concat([df, novo], ignore_index=True))
                        st.session_state.dados_fipe = {} # Limpa após salvar
                        st.success("Veículo cadastrado!")
                        st.rerun()
                else:
                    st.warning("Preencha Modelo, Placa e Foto.")

    elif menu == "📑 Gerenciar Estoque":
        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        if df.empty: st.info("Estoque vazio.")
        else:
            cols = st.columns(3)
            for i, r in df.iterrows():
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="car-card">
                            <img src="{r['foto']}" style="width:100%; border-radius:15px; margin-bottom:15px;">
                            <h3>{r['modelo']}</h3>
                            <p style='color:green; font-size:1.5rem; font-weight:bold;'>R$ {r['preco']:,.2f}</p>
                            <p><b>Placa:</b> {r['placa']}<br>
                               <b>Ano:</b> {str(r['ano_fab']).replace('.0','')}/{str(r['ano_mod']).replace('.0','')}<br>
                               {f"<b>Titular:</b> {r['nome_titular']}" if r['nome_titular'] else ""}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"🗑️ Excluir", key=f"del_{i}"):
                        conn.update(worksheet="Estoque", data=df.drop(i))
                        st.rerun()
