import streamlit as st
import pandas as pd
from PIL import Image

# 1. Configuração básica
st.set_page_config(page_title="CRM Amg Multimarcas", page_icon="🚗", layout="wide")

# 2. CSS Simplificado (Sem forçar bordas ou contornos)
st.markdown("""
    <style>
    /* Reset para cores limpas e sem bordas fantasmas */
    .main {
        background-color: #ffffff;
    }
    
    /* Força apenas a cor do texto principal para preto sólido */
    h1, h2, h3, p, label, .stMarkdown {
        color: #1a1a1a !important;
        text-decoration: none !important;
        border: none !important;
    }

    /* Estilo limpo para os Cards de Carros no Estoque */
    .car-card {
        border: 1px solid #eeeeee;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #ffffff;
    }

    .price-text {
        color: #28a745 !important;
        font-size: 24px;
        font-weight: bold;
    }

    /* Ajuste para que os campos de entrada não fiquem com bordas duplas */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN SIMPLES ---
if "autenticado" not in st.session_state:
    st.markdown("<h2 style='text-align: center; padding-top: 50px;'>Painel AMG Multimarcas</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
else:
    if 'estoque_dados' not in st.session_state:
        st.session_state.estoque_dados = []

    st.markdown("<h1 style='text-align: center;'>AMG MULTIMARCAS</h1>", unsafe_allow_html=True)
    
    menu = st.sidebar.radio("Navegação", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])

    # --- CADASTRO ---
    if menu == "➕ Cadastrar Veículo":
        st.subheader("📝 Detalhes do Veículo")
        
        # Colunas organizadas sem bordas bugadas
        c1, c2 = st.columns(2)
        with c1:
            marca = st.selectbox("Marca", ["Ford", "Chevrolet", "Volkswagen", "Fiat", "Toyota", "Hyundai", "Honda", "Nissan", "Outra"])
            modelo = st.text_input("Modelo e Versão")
            ano = st.text_input("Ano/Modelo")
        with c2:
            preco = st.number_input("Preço de Venda (R$)", min_value=0)
            km = st.number_input("Quilometragem (KM)", min_value=0)
            cambio = st.selectbox("Câmbio", ["Automático", "Manual"])
        
        foto = st.file_uploader("📷 Selecionar Foto", type=['jpg', 'jpeg', 'png'])
        
        if st.button("🚀 PUBLICAR NO SISTEMA", use_container_width=True):
            if modelo and foto:
                img = Image.open(foto)
                st.session_state.estoque_dados.append({
                    "marca": marca, "modelo": modelo, "ano": ano, 
                    "preco": preco, "km": km, "cambio": cambio, "foto": img
                })
                st.success(f"{modelo} adicionado ao pátio!")
            else:
                st.warning("Preencha o modelo e adicione uma foto.")

    # --- ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        st.subheader(f"🚘 Veículos no Pátio ({len(st.session_state.estoque_dados)})")
        
        for idx, carro in enumerate(st.session_state.estoque_dados):
            # Formatação simples
            km_formatado = f"{carro['km']:,}".replace(",", ".")
            preco_formatado = f"R$ {carro['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            with st.container():
                col_img, col_txt = st.columns([1, 1.5])
                with col_img:
                    st.image(carro["foto"], use_container_width=True)
                with col_txt:
                    st.markdown(f"### {carro['marca']} {carro['modelo']}")
                    st.markdown(f"<p class='price-text'>{preco_formatado}</p>", unsafe_allow_html=True)
                    st.write(f"📅 Ano: {carro['ano']} | ⚙️ {carro['cambio']}")
                    st.write(f"🛣️ KM: {km_formatado}")
                    if st.button(f"Remover {carro['modelo']}", key=f"del_{idx}"):
                        st.session_state.estoque_dados.pop(idx)
                        st.rerun()
                st.divider()

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()
