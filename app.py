import streamlit as st
import pandas as pd
from PIL import Image

# 1. Configuração de Página
st.set_page_config(page_title="CRM Amg Multimarcas", page_icon="🚗", layout="wide")

# 2. CSS "Blindado" contra Modo Escuro de Celulares
st.markdown("""
    <style>
    /* Força Fundo Branco e Texto Preto em TODO o app e menus */
    html, body, [data-testid="stAppViewContainer"], .main, .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Blindagem do Menu Lateral (Sidebar) */
    [data-testid="stSidebar"], [data-testid="stSidebar"] div, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Garante que o ícone do menu (hambúrguer) seja visível no mobile */
    [data-testid="stHeader"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #000000 !important;
    }

    /* Forçar cores de Títulos e Textos */
    h1, h2, h3, h4, p, span, label {
        color: #000000 !important;
    }

    /* Estilo dos Cards de Veículos */
    .car-card {
        background-color: #ffffff !important;
        border: 1px solid #dddddd !important;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
    }
    
    .price-tag {
        color: #28a745 !important;
        font-size: 24px;
        font-weight: 800;
        margin: 5px 0;
    }

    .spec-tag {
        background-color: #f0f2f6 !important;
        color: #31333f !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 5px;
        display: inline-block;
        border: 1px solid #cccccc;
    }

    /* Estilização dos campos de input para não sumirem no mobile */
    .stTextInput input, .stNumberInput input, .stSelectbox div {
        background-color: #f9f9f9 !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }

    /* Otimização para Mobile (Empilhamento) */
    @media (max-width: 640px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ACESSO ---
if "autenticado" not in st.session_state:
    st.markdown("<h2 style='text-align: center; margin-top: 30px; color: black;'>🔐 CRM AMG MULTIMARCAS</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("Acessar Painel", use_container_width=True):
                if u == "amgmultimarcas" and p == "amg0031":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Credenciais inválidas")
else:
    if 'estoque_dados' not in st.session_state:
        st.session_state.estoque_dados = []

    # LOGO
    st.markdown("<h1 style='text-align: center; color: black; font-weight: 900;'>AMG MULTIMARCAS</h1>", unsafe_allow_html=True)
    
    # Menu Lateral
    menu = st.sidebar.radio("MENU PRINCIPAL", ["➕ Cadastrar", "📑 Estoque", "📊 Leads"])

    if menu == "➕ Cadastrar":
        st.subheader("📝 Novo Cadastro")
        with st.form("cadastro", clear_on_submit=True):
            marca = st.selectbox("Marca", ["Ford", "Chevrolet", "Volkswagen", "Fiat", "Toyota", "Hyundai", "Honda", "Nissan", "Mitsubishi", "Outra"])
            modelo = st.text_input("Modelo e Versão")
            ano = st.text_input("Ano/Modelo")
            preco = st.number_input("Preço", min_value=0, step=500)
            km = st.number_input("KM", min_value=0, step=1000)
            cambio = st.selectbox("Câmbio", ["Automático", "Manual"])
            foto_input = st.file_uploader("📷 Foto Principal", type=['jpg', 'png', 'jpeg'])
            
            if st.form_submit_button("🚀 PUBLICAR NO SISTEMA", use_container_width=True):
                if modelo and foto_input:
                    img = Image.open(foto_input)
                    st.session_state.estoque_dados.append({
                        "marca": marca, "modelo": modelo, "ano": ano, 
                        "preco": preco, "km": km, "cambio": cambio, "foto": img
                    })
                    st.success(f"{modelo} publicado!")

    elif menu == "📑 Estoque":
        st.subheader(f"🚘 Pátio ({len(st.session_state.estoque_dados)} veículos)")
        
        for idx, carro in enumerate(st.session_state.estoque_dados):
            km_f = f"{carro['km']:,.0f}".replace(",", ".")
            pr_f = f"R$ {carro['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            with st.container():
                st.markdown('<div class="car-card">', unsafe_allow_html=True)
                # No mobile, essas colunas vão se empilhar automaticamente
                c_img, c_info = st.columns([1, 1.5])
                with c_img:
                    st.image(carro["foto"], use_container_width=True)
                with c_info:
                    st.markdown(f"<h3 style='margin-bottom:0;'>{carro['marca']} {carro['modelo']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p class='price-tag'>{pr_f}</p>", unsafe_allow_html=True)
                    st.markdown(f"""
                        <span class="spec-tag">📅 {carro['ano']}</span>
                        <span class="spec-tag">🛣️ {km_f} KM</span>
                        <span class="spec-tag">⚙️ {carro['cambio']}</span>
                    """, unsafe_allow_html=True)
                    if st.button(f"🗑️ Remover", key=f"del_{idx}", use_container_width=True):
                        st.session_state.estoque_dados.pop(idx)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.divider()
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()
