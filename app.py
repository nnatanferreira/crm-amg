import streamlit as st
import pandas as pd
from PIL import Image

# Configuração da Página
st.set_page_config(page_title="CRM Amg Multimarcas", page_icon="🚗", layout="wide")

# --- ESTILIZAÇÃO PARA FICAR IGUAL AO SITE ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .car-card {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
    }
    .price-tag {
        color: #28a745;
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0;
    }
    .tag {
        background-color: #f1f3f5;
        color: #495057;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 14px;
        margin-right: 8px;
        font-weight: 500;
        display: inline-block;
    }
    h1, h2, h3 { color: #1a1a1a !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
def login():
    if "autenticado" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔐 Painel Administrativo AMG</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.button("Entrar", use_container_width=True):
                if u == "amgmultimarcas" and p == "amg0031":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Dados incorretos")
        return False
    return True

if login():
    if 'estoque_dados' not in st.session_state:
        st.session_state.estoque_dados = []

    # LOGO E TÍTULO
    st.markdown("<h1 style='text-align: center; margin-bottom:0;'>AMG <span style='font-weight:200;'>MULTIMARCAS</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Gestão de Estoque e Tráfego</p>", unsafe_allow_html=True)
    st.divider()

    aba = st.sidebar.radio("Navegação", ["📦 Cadastrar Carro", "🚘 Ver Estoque (Site)", "📈 Leads"])

    if aba == "📦 Cadastrar Carro":
        st.subheader("Cadastrar Veículo no Sistema")
        with st.form("form_carro", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                marca_modelo = st.text_input("Marca e Modelo (Ex: Nissan Frontier XE)")
                ano = st.text_input("Ano/Modelo (Ex: 2013/2013)")
                km = st.number_input("Quilometragem", min_value=0)
            with c2:
                valor = st.number_input("Preço de Venda (R$)", min_value=0)
                cambio = st.selectbox("Câmbio", ["Automático", "Manual"])
                foto_arquivo = st.file_uploader("Carregar Foto do Veículo", type=['jpg', 'jpeg', 'png'])
            
            enviar = st.form_submit_button("PUBLICAR NO CRM")
            
            if enviar:
                if marca_modelo and foto_arquivo:
                    # Guardamos a imagem em memória para exibição imediata
                    img = Image.open(foto_arquivo)
                    st.session_state.estoque_dados.append({
                        "nome": marca_modelo, "ano": ano, "km": km,
                        "valor": valor, "cambio": cambio, "foto": img
                    })
                    st.success(f"{marca_modelo} publicado com sucesso!")
                else:
                    st.error("Por favor, preencha o nome e carregue uma foto.")

    elif aba == "🚘 Ver Estoque (Site)":
        st.subheader("Vitrine de Veículos")
        if not st.session_state.estoque_dados:
            st.info("Nenhum carro cadastrado ainda.")
        else:
            for carro in st.session_state.estoque_dados:
                with st.container():
                    col_img, col_info = st.columns([1, 1.5])
                    with col_img:
                        st.image(carro["foto"], use_container_width=True)
                    with col_info:
                        st.markdown(f"## {carro['nome']}")
                        st.markdown(f"<div class='price-tag'>R$ {carro['valor']:,.2f}</div>", unsafe_allow_html=True)
                        st.markdown(f"""
                            <span class='tag'>📅 {carro['ano']}</span>
                            <span class='tag'>🛣️ {carro['km']:,} KM</span>
                            <span class='tag'>⚙️ {carro['cambio']}</span>
                        """, unsafe_allow_html=True)
                        st.write("")
                        if st.button(f"Anunciar no Meta", key=carro['nome']):
                            st.toast("Preparando criativo para o Facebook...")
                    st.divider()

    st.sidebar.button("Sair", on_click=lambda: st.session_state.clear())
