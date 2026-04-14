import streamlit as st
import pandas as pd
from PIL import Image

# 1. Configuração de Página
st.set_page_config(page_title="CRM Amg Multimarcas", page_icon="🚗", layout="wide")

# 2. CSS ANTI-BUG (Limpeza de linhas, contornos e sombras)
st.markdown("""
    <style>
    /* RESET TOTAL: Remove contornos, sombras e forças fundo branco */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-stroke: 0px !important;
        text-shadow: none !important;
    }

    /* Blindagem de Títulos e Textos contra 'Modo Dark' do celular */
    h1, h2, h3, p, span, label, div, .stMarkdown {
        color: #000000 !important;
        text-shadow: none !important;
        -webkit-text-stroke: 0px !important;
        outline: none !important;
    }

    /* CORREÇÃO CAIXA DE UPLOAD (Texto invisível) */
    [data-testid="stFileUploadDropzone"] {
        background-color: #f1f3f5 !important;
        border: 2px dashed #999999 !important;
    }
    
    /* Força o texto de dentro da caixa de upload a ser preto */
    [data-testid="stFileUploadDropzone"] * {
        color: #000000 !important;
    }

    /* Card do Veículo Estilo Site */
    .car-card {
        background-color: #ffffff !important;
        border: 1px solid #e9ecef !important;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 25px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05) !important;
    }
    
    .price-tag {
        color: #28a745 !important;
        font-size: 26px;
        font-weight: 900;
        margin: 5px 0;
    }

    .spec-tag {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 700;
        margin-right: 8px;
        display: inline-block;
        border: 1px solid #dee2e6;
        margin-bottom: 5px;
    }

    /* Inputs Visíveis no Celular */
    .stTextInput input, .stNumberInput input, .stSelectbox div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }

    /* Sidebar (Menu) sem interferência do modo escuro */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e9ecef !important;
    }
    
    /* Otimização Mobile (Empilhamento) */
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ACESSO ---
if "autenticado" not in st.session_state:
    st.markdown("<h2 style='text-align: center; margin-top: 30px; color: #000;'>🔐 CRM AMG MULTIMARCAS</h2>", unsafe_allow_html=True)
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

    st.markdown("<h1 style='text-align: center; color: #000; font-weight: 900; letter-spacing: -1px;'>AMG MULTIMARCAS</h1>", unsafe_allow_html=True)
    
    menu = st.sidebar.radio("MENU", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque", "📈 Leads Site"])

    if menu == "➕ Cadastrar Veículo":
        st.subheader("📝 Detalhes do Veículo")
        with st.form("cadastro", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                marca = st.selectbox("Marca", ["Ford", "Chevrolet", "Volkswagen", "Fiat", "Toyota", "Hyundai", "Honda", "Nissan", "Mitsubishi", "Outra"])
                modelo = st.text_input("Modelo e Versão")
                ano = st.text_input("Ano/Modelo")
            with c2:
                preco = st.number_input("Preço de Venda (R$)", min_value=0, step=500)
                km = st.number_input("Quilometragem (KM)", min_value=0, step=1000)
                cambio = st.selectbox("Câmbio", ["Automático", "Manual"])
            
            # Caixa de Foto Principal (Corrigida)
            foto_input = st.file_uploader("📷 Selecionar Foto do Veículo", type=['jpg', 'png', 'jpeg'])
            
            if st.form_submit_button("🚀 PUBLICAR NO SISTEMA", use_container_width=True):
                if modelo and foto_input:
                    img = Image.open(foto_input)
                    st.session_state.estoque_dados.append({
                        "marca": marca, "modelo": modelo, "ano": ano, 
                        "preco": preco, "km": km, "cambio": cambio, "foto": img
                    })
                    st.success(f"{modelo} cadastrado com sucesso!")

    elif menu == "📑 Gerenciar Estoque":
        st.subheader(f"🚘 Pátio Atual ({len(st.session_state.estoque_dados)} carros)")
        
        for idx, carro in enumerate(st.session_state.estoque_dados):
            # Formatação Padrão Brasil (Ponto no KM e Virgula no Preço)
            km_f = f"{carro['km']:,.0f}".replace(",", ".")
            pr_f = f"R$ {carro['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            with st.container():
                st.markdown('<div class="car-card">', unsafe_allow_html=True)
                c_img, c_info = st.columns([1, 1.8])
                with c_img:
                    st.image(carro["foto"], use_container_width=True)
                with c_info:
                    st.markdown(f"<h3 style='margin:0; color:#000;'>{carro['marca']} {carro['modelo']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p class='price-tag'>{pr_f}</p>", unsafe_allow_html=True)
                    st.markdown(f"""
                        <span class="spec-tag">📅 {carro['ano']}</span>
                        <span class="spec-tag">🛣️ {km_f} KM</span>
                        <span class="spec-tag">⚙️ {carro['cambio']}</span>
                    """, unsafe_allow_html=True)
                    if st.button(f"🗑️ Remover Veículo", key=f"del_{idx}", use_container_width=True):
                        st.session_state.estoque_dados.pop(idx)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.divider()
    if st.sidebar.button("Fazer Logoff"):
        st.session_state.clear()
        st.rerun()
