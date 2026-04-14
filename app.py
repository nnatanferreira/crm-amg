import streamlit as st
import pandas as pd
from PIL import Image

# 1. Configuração de Página
st.set_page_config(page_title="CRM Amg Multimarcas", page_icon="🚗", layout="wide")

# 2. Estilização Avançada (Foco em UI/UX de Loja de Veículos)
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    
    /* Card do Veículo Estilo Marketplace */
    .car-card {
        background-color: white;
        border-radius: 15px;
        padding: 0px;
        border: 1px solid #e0e6ed;
        margin-bottom: 30px;
        overflow: hidden;
        display: flex;
        flex-direction: row;
    }
    
    .price-tag {
        color: #1a1a1a;
        font-size: 28px;
        font-weight: 800;
        margin: 5px 0;
    }

    .spec-tag {
        background-color: #f8f9fa;
        color: #5f6368;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 8px;
        border: 1px solid #eee;
    }

    /* Customização dos Inputs */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 10px !important;
    }
    
    .main-title {
        text-align: center;
        font-weight: 900;
        letter-spacing: -1px;
        color: #1a1a1a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ACESSO ---
if "autenticado" not in st.session_state:
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>🔐 CRM AMG MULTIMARCAS</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
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
    # --- INTERFACE DO CRM ---
    if 'estoque_dados' not in st.session_state:
        st.session_state.estoque_dados = []

    st.markdown("<h1 class='main-title'>AMG <span style='font-weight:100;'>MULTIMARCAS</span></h1>", unsafe_allow_html=True)
    
    menu = st.sidebar.radio("PAINEL DE CONTROLE", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque", "📊 Leads & Vendas"])

    # --- ABA 1: CADASTRO IGUAL AO SITE ---
    if menu == "➕ Cadastrar Veículo":
        st.subheader("📝 Detalhes do Veículo")
        
        with st.form("cadastro_completo", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                marca = st.selectbox("Marca", ["Ford", "Chevrolet", "Volkswagen", "Fiat", "Toyota", "Hyundai", "Honda", "Nissan", "Mitsubishi", "Outra"])
                modelo = st.text_input("Modelo e Versão (Ex: Frontier 2.5 Diesel 4x4)")
                ano = st.text_input("Ano/Modelo (Ex: 2013/2013)")
            
            with col2:
                preco = st.number_input("Preço de Venda (R$)", min_value=0, step=500)
                km = st.number_input("Quilometragem Atual", min_value=0, step=1000)
                cor = st.text_input("Cor do Veículo")
            
            with col3:
                combustivel = st.selectbox("Combustível", ["Diesel", "Flex", "Gasolina", "Híbrido", "Elétrico"])
                cambio = st.selectbox("Câmbio", ["Automático", "Manual"])
                placa = st.text_input("Final da Placa")

            st.divider()
            
            c_foto, c_desc = st.columns([1, 2])
            with c_foto:
                foto_input = st.file_uploader("📷 Foto Principal", type=['jpg', 'png', 'jpeg'])
            with c_desc:
                opcionais = st.multiselect("Opcionais de Destaque", ["Ar Condicionado", "Direção Hidráulica", "Vidros Elétricos", "Teto Solar", "Tração 4x4", "Bancos em Couro", "Multimídia"])
                obs = st.text_area("Descrição para o Anúncio (O que vai pro Facebook/Site)")

            if st.form_submit_button("🚀 PUBLICAR VEÍCULO", use_container_width=True):
                if modelo and foto_input:
                    # Salva o objeto da imagem
                    img = Image.open(foto_input)
                    st.session_state.estoque_dados.append({
                        "marca": marca, "modelo": modelo, "ano": ano, "preco": preco,
                        "km": km, "cor": cor, "combustivel": combustivel, "cambio": cambio,
                        "foto": img, "obs": obs, "opcionais": opcionais
                    })
                    st.success(f"Sucesso! {modelo} agora faz parte do seu estoque.")
                else:
                    st.warning("Preencha o modelo e adicione uma foto.")

    # --- ABA 2: ESTOQUE ESTILO VITRINE ---
    elif menu == "📑 Gerenciar Estoque":
        st.subheader(f"🚘 Seu Pátio ({len(st.session_state.estoque_dados)} veículos)")
        
        if not st.session_state.estoque_dados:
            st.info("O estoque está vazio. Vá em 'Cadastrar Veículo' para começar.")
        
        for idx, carro in enumerate(st.session_state.estoque_dados):
            with st.container():
                # Layout de Card Profissional
                col_img, col_info = st.columns([1, 1.8])
                
                with col_img:
                    st.image(carro["foto"], use_container_width=True)
                
                with col_info:
                    st.markdown(f"### {carro['marca']} {carro['modelo']}")
                    st.markdown(f"<div class='price-tag'>R$ {carro['preco']:,.2f}</div>", unsafe_allow_html=True)
                    
                    # Tags de specs
                    st.markdown(f"""
                        <span class="spec-tag">📅 {carro['ano']}</span>
                        <span class="spec-tag">🛣️ {carro['km']:,} KM</span>
                        <span class="spec-tag">⚙️ {carro['cambio']}</span>
                        <span class="spec-tag">⛽ {carro['combustivel']}</span>
                        <span class="spec-tag">🎨 {carro['cor']}</span>
                    """, unsafe_allow_html=True)
                    
                    st.write(f"**Descrição:** {carro['obs'][:150]}...")
                    
                    # Botões de ação
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button(f"📢 Criar Anúncio Meta", key=f"ads_{idx}"):
                            st.toast("Gerando criativo...")
                    with c_btn2:
                        if st.button(f"🗑️ Remover", key=f"del_{idx}"):
                            st.session_state.estoque_dados.pop(idx)
                            st.rerun()
                st.divider()

    st.sidebar.button("Logoff", on_click=lambda: st.session_state.clear())
