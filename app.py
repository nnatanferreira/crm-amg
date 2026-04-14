import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests
from datetime import datetime

# --- 1. CONFIGURAÇÕES ---
API_FIPE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI0ZDk3YTE4NC1kOGIzLTQwOTEtOWVhOC1kNWQ0ZGUzYWZiNWQiLCJlbWFpbCI6Im5uYXRhbmZlcnJlaXJhQGdtYWlsLmNvbSIsImlhdCI6MTc3NjIwMTM4NH0.v_0pe0vEEuLCIMenEsLWZXSl_hdkXVq4oTzfhT4kdXM"

cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

# Configuração da Página
st.set_page_config(
    page_title="CRM AMG Multimarcas", 
    page_icon="🚗", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. FUNÇÃO DE CONSULTA API ---
def consultar_dados_veiculo(placa):
    try:
        placa_limpa = placa.replace("-", "").strip().upper()
        url = f"https://api.fipe.online/v1/veiculos/{placa_limpa}"
        headers = {
            "Authorization": f"Bearer {API_FIPE_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=12)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Erro 401: Token da API Inválido.")
        elif response.status_code == 404:
            st.error("Placa não encontrada na base nacional.")
        else:
            st.error(f"Erro na API: {response.status_code}")
        return None
    except Exception as e:
        st.error(f"Erro de conexão: {str(e)}")
        return None

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #f8f9fa !important; }
    h1 { font-size: 3rem !important; font-weight: 800 !important; color: #1a1a1a; }
    h2 { font-size: 2.2rem !important; font-weight: 700 !important; color: #1e7e34; }
    [data-testid="stSidebar"] { min-width: 320px !important; background-color: #ffffff !important; }
    [data-testid="stWidgetLabel"] p { font-size: 1.2rem !important; font-weight: 600 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 1.2rem !important; height: 60px !important; border-radius: 10px !important;
    }
    .stButton button {
        font-size: 1.6rem !important; font-weight: 800 !important; height: 75px !important;
        border-radius: 15px !important; background-color: #1e7e34 !important; color: white !important;
    }
    .car-card { 
        border: 2px solid #eee; border-radius: 20px; padding: 25px; 
        background-color: #ffffff; box-shadow: 0px 6px 15px rgba(0,0,0,0.05);
    }
    .preco-destaque { color: #1e7e34 !important; font-size: 2rem !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CONEXÃO GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Erro de conexão com a planilha.")

# --- 5. SISTEMA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🚗 AMG Multimarcas</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA", use_container_width=True):
                if u == "amgmultimarcas" and p == "amg0031":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")
else:
    menu = st.sidebar.radio("Navegar:", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR VEÍCULO ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Cadastro de Veículo")
        
        # BUSCA POR PLACA
        col_p1, col_p2 = st.columns([3, 1])
        placa_input = col_p1.text_input("🔍 Digite a Placa para buscar dados:", placeholder="ABC1D23").upper()
        
        if "dados_fipe" not in st.session_state:
            st.session_state.dados_fipe = {}

        if col_p2.button("BUSCAR DADOS"):
            if placa_input:
                with st.spinner("Consultando base de dados nacional..."):
                    res_api = consultar_dados_veiculo(placa_input)
                    if res_api:
                        st.session_state.dados_fipe = res_api.get("data", res_api)
                        st.success("Dados preenchidos automaticamente!")
            else:
                st.warning("Informe a placa.")

        # FORMULÁRIO DE CADASTRO
        with st.form("form_veiculo", clear_on_submit=True):
            f = st.session_state.dados_fipe
            
            st.subheader("🚗 Dados do Veículo")
            c1, c2, c3 = st.columns([1, 1.5, 1])
            with c1:
                marca = st.text_input("Marca", value=f.get("marca", ""))
            with c2:
                modelo = st.text_input("Modelo/Versão", value=f.get("modelo", ""))
            with c3:
                placa_final = st.text_input("Placa", value=placa_input if not f else f.get("placa", placa_input))

            d1, d2, d3 = st.columns(3)
            with d1:
                ano_fab = st.text_input("Ano Fabricação", value=str(f.get("ano_fabricacao", "")))
                renavam = st.text_input("Renavam", value=f.get("renavam", ""))
            with d2:
                ano_mod = st.text_input("Ano Modelo", value=str(f.get("ano_modelo", "")))
                chassi = st.text_input("Chassi", value=f.get("chassi", ""))
            with d3:
                cor = st.text_input("Cor", value=f.get("cor", ""))
                combustivel = st.text_input("Combustível", value=f.get("combustivel", ""))

            st.markdown("---")
            v1, v2 = st.columns(2)
            with v1:
                preco_fipe_sugerido = f.get("preco_fipe", 0.0)
                # Converte para float se vier string da API
                try: preco_val = float(preco_fipe_sugerido)
                except: preco_val = 0.0
                
                preco = st.number_input("Preço de Venda (R$)", value=preco_val, step=500.0)
                km = st.number_input("Quilometragem", min_value=0)
            with v2:
                foto_v_file = st.file_uploader("📷 Foto Principal do Veículo", type=['jpg', 'jpeg', 'png'])

            st.markdown("---")
            st.subheader("👤 Proprietário / Titular (Opcional)")
            t1, t2 = st.columns(2)
            with t1:
                nome_titular = st.text_input("Nome do Titular")
                cpf_titular = st.text_input("CPF")
                rg_titular = st.text_input("RG")
            with t2:
                endereco_titular = st.text_input("Endereço Completo")
                doc_titular_file = st.file_uploader("📂 Foto do Documento do Titular", type=['jpg', 'jpeg', 'png'])

            if st.form_submit_button("🚀 SALVAR NO ESTOQUE", use_container_width=True):
                if modelo and placa_final and foto_v_file:
                    with st.spinner('Salvando no banco de dados...'):
                        # Upload Foto Carro
                        res_car = cloudinary.uploader.upload(foto_v_file)
                        
                        # Upload Doc Titular
                        url_doc = ""
                        if doc_titular_file:
                            res_doc = cloudinary.uploader.upload(doc_titular_file)
                            url_doc = res_doc['secure_url']

                        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                        
                        novo = pd.DataFrame([{
                            "marca": marca, "modelo": modelo, "placa": placa_final.upper(),
                            "ano_fab": str(ano_fab), "ano_mod": str(ano_mod),
                            "renavam": renavam, "chassi": chassi.upper(),
                            "cor": cor, "combustivel": combustivel,
                            "preco": preco, "km": km, "foto": res_car['secure_url'],
                            "nome_titular": nome_titular, "cpf_titular": cpf_titular,
                            "rg_titular": rg_titular, "endereco_titular": endereco_titular,
                            "doc_titular": url_doc
                        }])
                        
                        conn.update(worksheet="Estoque", data=pd.concat([df, novo], ignore_index=True))
                        st.session_state.dados_fipe = {}
                        st.success("Veículo cadastrado com sucesso!")
                        st.rerun()
                else:
                    st.warning("Obrigatório: Modelo, Placa e Foto do Veículo.")

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        if df.empty:
            st.info("Estoque vazio.")
        else:
            st.markdown(f"## 🚘 Estoque AMG ({len(df)} veículos)")
            cols = st.columns(3)
            for i, r in df.iterrows():
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="car-card">
                            <img src="{r['foto']}" style="width:100%; border-radius:15px; margin-bottom:15px; height:200px; object-fit:cover;">
                            <h3>{r['modelo']}</h3>
                            <p class="preco-destaque">R$ {r['preco']:,.2f}</p>
                            <p style='font-size:1.1rem'>
                                <b>Placa:</b> {r['placa']}<br>
                                <b>Ano:</b> {str(r['ano_fab']).replace('.0','')}/{str(r['ano_mod']).replace('.0','')}<br>
                                {"<b>Titular:</b> " + str(r['nome_titular']) if r['nome_titular'] else ""}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if 'doc_titular' in r and r['doc_titular']:
                        st.link_button("📂 Ver Doc Titular", r['doc_titular'], use_container_width=True)
                    
                    if st.button(f"🗑️ Excluir", key=f"del_{i}", use_container_width=True):
                        conn.update(worksheet="Estoque", data=df.drop(i))
                        st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)
