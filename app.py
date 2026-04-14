import streamlit as st
import pandas as pd
from PIL import Image

# 1. Configuração de Página
st.set_page_config(page_title="CRM Amg Multimarcas", page_icon="🚗", layout="wide")

# 2. Estilização Reforçada para Mobile e Desktop (Fundo Branco Forçado)
st.markdown("""
    <style>
    /* Força o fundo branco e texto preto em todo o app para evitar bugs em mobile */
    .stApp {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }

    /* Ajuste de contraste para textos e labels */
    .stMarkdown, p, span, label, .stSubheader, h1, h2, h3 {
        color: #1a1a1a !important;
    }

    /* Estilo dos Cards de Veículos */
    .car-card {
        background-color: #ffffff !important;
        border: 1px solid #e0e6ed !important;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    }
    
    .price-tag {
        color: #28a745 !important;
        font-size: 24px;
        font-weight: 800;
        margin: 5px 0;
    }

    .spec-tag {
        background-color: #f1f3f5 !important;
        color: #495057 !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 5px;
        display: inline-block;
        margin-bottom: 5px;
        border: 1px solid #ddd;
    }

    /* Otimização para Mobile: Empilhar colunas */
    @media (max-width: 640px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
        .main-title {
            font-size: 28px !important;
        }
    }

    .main-title {
        text-align: center;
        font-weight: 900;
        letter-spacing: -1px;
        color: #000000 !important;
    }

    /* Inputs e Selects com fundo cinza claro para destacar do branco */
    input, select, textarea {
        background-color: #f8f9fa !important;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ACESSO ---
if "autenticado" not in st.session_state:
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>🔐 CRM AMG MULTIMARCAS</h2>", unsafe_allow_html=True)
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

    st.markdown("<h1 class='main-title'>AMG <span style='font-weight:100;'>MULTIMARCAS</span></h1>", unsafe_allow_html=True)
    
    menu = st.sidebar.radio("PAINEL", ["➕ Cadastrar", "📑 Estoque", "📊 Leads"])

    # --- ABA: CADASTRO ---
    if menu == "➕ Cadastrar":
        st.subheader("📝 Novo Veículo")
        with st.form("cadastro", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                marca = st.selectbox("Marca", ["Ford", "Chevrolet", "Volkswagen", "Fiat", "Toyota", "Hyundai", "Honda", "Nissan", "Mitsubishi", "Outra"])
                modelo = st.text_input("Modelo e Versão")
                ano = st.text_input("Ano/Modelo")
            with c2:
                preco = st.number_input("Preço", min_value=0, step=500)
                km = st.number_input("KM", min_value=0, step=1000)
                cambio = st.selectbox("Câmbio", ["Automático", "Manual"])
            
            foto_input = st.file_uploader("📷 Foto Principal", type=['jpg', 'png', 'jpeg'])
            
            if st.form_submit_button("🚀 PUBLICAR", use_container_width=True):
                if modelo and foto_input:
                    img = Image.open(foto_input)
                    st.session_state.estoque_dados.append({
                        "marca": marca, "modelo": modelo, "ano": ano, 
                        "preco": preco, "km": km, "cambio": cambio, "foto": img
                    })
                    st.success(f"{modelo} cadastrado!")

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Estoque":
        st.subheader(f"🚘 Pátio ({len(st.session_state.estoque_dados)} veículos)")
        
        for idx, carro in enumerate(st.session_state.estoque_dados):
            # Formatação Padrão Brasil
            km_f = f"{carro['km']:,.0f}".replace(",", ".")
            pr_f = f"R$ {carro['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            with st.container():
                st.markdown('<div class="car-card">', unsafe_allow_html=True)
                col_img, col_info = st.columns([1, 1.5])
                with col_img:
                    st.image(carro["foto"], use_container_width=True)
                with col_info:
                    st.markdown(f"### {carro['marca']} {carro['modelo']}")
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
                st.write("") # Espaço entre cards

    st.sidebar.button("Sair", on_click=lambda: st.session_state.clear())
