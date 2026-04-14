import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd

# --- 1. CONFIGURAÇÃO DO CLOUDINARY ---
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

# --- 2. ESTILO VISUAL ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #f8f9fa !important; color: #1a1a1a !important; }
    h1 { font-size: 3.5rem !important; font-weight: 800 !important; }
    h2 { font-size: 2.5rem !important; font-weight: 700 !important; }
    
    [data-testid="stSidebar"] { min-width: 350px !important; background-color: #ffffff !important; border-right: 1px solid #ddd; }
    
    [data-testid="stWidgetLabel"] p { font-size: 1.4rem !important; font-weight: 600 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 1.4rem !important; height: 65px !important; border-radius: 12px !important;
    }

    .stButton button {
        font-size: 1.8rem !important; font-weight: 800 !important; height: 80px !important;
        border-radius: 15px !important; background-color: #1e7e34 !important; color: white !important;
    }

    .car-card { 
        border: 2px solid #eee; border-radius: 20px; padding: 25px; 
        background-color: #ffffff; box-shadow: 0px 6px 20px rgba(0,0,0,0.1);
    }
    .preco-destaque { color: #1e7e34 !important; font-size: 2.3rem !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. SISTEMA DE LOGIN ---
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
                else: st.error("Dados incorretos.")
else:
    menu = st.sidebar.radio("Navegar:", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR VEÍCULO ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Novo Cadastro Completo")
        
        with st.form("form_veiculo", clear_on_submit=True):
            # LINHA PRINCIPAL
            c1, c2, c3 = st.columns([1, 1.5, 1])
            with c1:
                marca = st.selectbox("Marca", ["Nissan", "Ford", "Chevrolet", "VW", "Fiat", "Toyota", "Honda", "Mitsubishi", "Renault", "Hyundai", "Jeep", "BMW", "Mercedes", "Outra"])
            with c2:
                modelo = st.text_input("Modelo e Versão")
            with c3:
                placa = st.text_input("Placa (Ex: ABC1D23)")

            # DADOS TÉCNICOS PARA DOCUMENTOS
            st.markdown("---")
            st.subheader("🏁 Informações para Documentos (Arras/Procuração/ATPV)")
            
            d1, d2, d3 = st.columns(3)
            with d1:
                ano_fab = st.text_input("Ano de Fabricação")
                renavam = st.text_input("Renavam")
            with d2:
                ano_mod = st.text_input("Ano do Modelo")
                chassi = st.text_input("Chassi")
            with d3:
                cor = st.text_input("Cor (conforme documento)")
                combustivel = st.selectbox("Combustível", ["Flex", "Diesel", "Gasolina", "Híbrido", "Elétrico"])

            # VALORES E FOTO
            st.markdown("---")
            v1, v2 = st.columns(2)
            with v1:
                preco = st.number_input("Preço de Venda (R$)", min_value=0.0, step=500.0)
                km = st.number_input("Quilometragem", min_value=0)
            with v2:
                foto_v = st.file_uploader("📷 Foto Principal do Veículo", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("🚀 SALVAR VEÍCULO COMPLETO", use_container_width=True):
                if modelo and placa and foto_v:
                    with st.spinner('Gravando veículo...'):
                        res = cloudinary.uploader.upload(foto_v)
                        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                        
                        novo = pd.DataFrame([{
                            "marca": marca, "modelo": modelo, "placa": placa.upper(),
                            "ano_fab": str(ano_fab), "ano_mod": str(ano_mod),
                            "renavam": renavam, "chassi": chassi.upper(),
                            "cor": cor, "combustivel": combustivel,
                            "preco": preco, "km": km, "foto": res['secure_url']
                        }])
                        
                        conn.update(worksheet="Estoque", data=pd.concat([df, novo], ignore_index=True))
                        st.success(f"Veículo {modelo} (Placa: {placa.upper()}) cadastrado!")
                else:
                    st.warning("Preencha Modelo, Placa e Foto.")

    # ---
