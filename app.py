import streamlit as st
import pandas as pd
import cloudinary
import cloudinary.uploader
from PIL import Image

# 1. CONFIGURAÇÃO DO CLOUDINARY (Substitua pelos seus dados)
cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="CRM AMG Multimarcas", page_icon="🚗", layout="wide")

# CSS Limpo e Anti-Bug para Mobile
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2, h3, p, label { color: #1a1a1a !important; }
    .car-card {
        border: 1px solid #eee;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #ffffff;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    .preco-destaque { color: #28a745 !important; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.markdown("<h2 style='text-align: center; padding-top: 40px;'>Painel Administrativo</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Acesso negado")
else:
    # Lógica de Armazenamento Temporário (Enquanto não conectamos o Sheets)
    if 'estoque_permanente' not in st.session_state:
        st.session_state.estoque_permanente = []

    st.markdown("<h1 style='text-align: center;'>AMG MULTIMARCAS</h1>", unsafe_allow_html=True)
    
    aba = st.sidebar.radio("Navegação", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])

    # --- ABA: CADASTRO ---
    if aba == "➕ Cadastrar Veículo":
        st.subheader("📝 Novo Cadastro (Hospedagem Automática)")
        
        with st.form("cadastro_amg", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                marca = st.selectbox("Marca", ["Nissan", "Ford", "Chevrolet", "VW", "Fiat", "Toyota", "Honda", "Mitsubishi"])
                modelo = st.text_input("Modelo e Versão")
                ano = st.text_input("Ano/Modelo")
            with c2:
                preco = st.number_input("Preço de Venda (R$)", min_value=0)
                km = st.number_input("Quilometragem (KM)", min_value=0)
                cambio = st.selectbox("Câmbio", ["Automático", "Manual"])
            
            foto_arquivo = st.file_uploader("📷 Selecionar Foto do Carro", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("🚀 PUBLICAR E HOSPEDAR FOTO", use_container_width=True):
                if modelo and foto_arquivo:
                    with st.spinner('Enviando foto para o servidor...'):
                        # UPLOAD REAL PARA O CLOUDINARY
                        resultado = cloudinary.uploader.upload(foto_arquivo)
                        url_da_foto = resultado['secure_url']
                        
                        # SALVANDO OS DADOS
                        dados_carro = {
                            "marca": marca, "modelo": modelo, "ano": ano,
                            "preco": preco, "km": km, "cambio": cambio, "foto": url_da_foto
                        }
                        st.session_state.estoque_permanente.append(dados_carro)
                        st.success(f"Veículo {modelo} publicado! Foto hospedada em: {url_da_foto}")
                else:
                    st.warning("Preencha o modelo e anexe uma foto.")

    # --- ABA: ESTOQUE ---
    elif aba == "📑 Gerenciar Estoque":
        st.subheader(f"🚘 Pátio Digital ({len(st.session_state.estoque_permanente)} veículos)")
        
        for idx, carro in enumerate(st.session_state.estoque_permanente):
            km_f = f"{carro['km']:,}".replace(",", ".")
            pr_f = f"R$ {carro['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            with st.container():
                st.markdown('<div class="car-card">', unsafe_allow_html=True)
                col_img, col_txt = st.columns([1, 1.8])
                with col_img:
                    # Aqui ele já puxa a foto direto da internet (Cloudinary)
                    st.image(carro["foto"], use_container_width=True)
                with col_txt:
                    st.markdown(f"### {carro['marca']} {carro['modelo']}")
                    st.markdown(f"<p class='preco-destaque'>{pr_f}</p>", unsafe_allow_html=True)
                    st.write(f"📅 Ano: {carro['ano']} | ⚙️ {carro['cambio']}")
                    st.write(f"🛣️ KM: {km_f}")
                    st.caption(f"🔗 Link da Foto: {carro['foto']}")
                    if st.button(f"Remover {idx}", key=f"del_{idx}"):
                        st.session_state.estoque_permanente.pop(idx)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()
