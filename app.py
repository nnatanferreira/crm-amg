import streamlit as st
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="CRM Amg Multimarcas", page_icon="🚗", layout="wide")

# 2. Estilização para Máxima Legibilidade (Tema Claro)
st.markdown("""
    <style>
    /* Fundo geral mais limpo */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Forçar todos os textos principais para preto para não sumirem */
    h1, h2, h3, p, span, label {
        color: #1a1a1a !important;
    }

    /* Estilo dos Cards de Carros */
    .car-card {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }

    /* Tags de detalhes (Ano, KM, etc) */
    .tag {
        background-color: #e9ecef;
        color: #495057 !important;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 13px;
        margin-right: 5px;
        font-weight: 500;
    }

    /* Preço em destaque */
    .price-tag {
        color: #28a745 !important;
        font-size: 22px;
        font-weight: bold;
    }
    
    /* Ajuste da barra lateral */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
def check_password():
    def password_guessed():
        if st.session_state["username"] == "amgmultimarcas" and st.session_state["password"] == "amg0031":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔐 Acesso AMG Multimarcas</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            st.button("Entrar", on_click=password_guessed, use_container_width=True)
        return False
    return st.session_state["password_correct"]

if check_password():
    if 'meu_estoque' not in st.session_state: st.session_state.meu_estoque = []
    if 'leads' not in st.session_state: st.session_state.leads = []

    # --- LOGO NO TOPO ---
    st.markdown("<h1 style='text-align: center; color: #000; margin-bottom: 0;'>AMG <span style='font-weight: lighter;'>MULTIMARCAS</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; margin-top: 0;'>Gravataí - Rio Grande do Sul</p>", unsafe_allow_html=True)
    st.divider()

    # Menu Lateral
    aba = st.sidebar.radio("Navegação", ["Estoque / Cadastro", "Leads Site", "Anúncios Meta"])
    if st.sidebar.button("Sair"):
        st.session_state["password_correct"] = False
        st.rerun()

    # --- ABA: ESTOQUE ---
    if aba == "Estoque / Cadastro":
        st.subheader("📋 Cadastrar Veículo")
        with st.form("novo_carro", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                modelo = st.text_input("Modelo do Carro")
                marca = st.selectbox("Marca", ["Chevrolet", "Volkswagen", "Fiat", "Ford", "Hyundai", "Toyota", "Honda", "Nissan", "Renault", "Outros"])
            with c2:
                ano = st.text_input("Ano (Ex: 2015/2016)")
                km = st.number_input("Quilometragem", min_value=0)
            with c3:
                valor = st.number_input("Preço de Venda (R$)", min_value=0)
                foto = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
            
            if st.form_submit_button("Salvar no Sistema", use_container_width=True):
                st.session_state.meu_estoque.append({
                    "Modelo": modelo, "Marca": marca, "Ano": ano, 
                    "KM": km, "Preço": valor, "Foto": foto
                })
                st.success("Veículo adicionado!")

        # Exibição do Estoque
        for idx, carro in enumerate(st.session_state.meu_estoque):
            st.markdown(f"""
            <div class="car-card">
                <h3 style="margin-top:0;">{carro['Marca']} {carro['Modelo']}</h3>
                <p class="price-tag">R$ {carro['Preço']:,.2f}</p>
                <div>
                    <span class="tag">📅 {carro['Ano']}</span>
                    <span class="tag">🛣️ {carro['KM']:,} KM</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if carro["Foto"]:
                st.image(carro["Foto"], width=300)
            st.divider()

    elif aba == "Leads Site":
        st.subheader("👤 Leads Recebidos")
        st.info("Aguardando conexão com o formulário do Netlify...")

    elif aba == "Anúncios Meta":
        st.subheader("🚀 Tráfego Pago")
        st.write("Selecione um veículo para configurar o anúncio.")
