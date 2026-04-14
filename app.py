import streamlit as st
import pandas as pd
import base64

# 1. Configuração da Página
st.set_page_config(page_title="CRM Amg Multimarcas", page_icon="🚗", layout="wide")

# Função para carregar a imagem de fundo e transformar em CSS
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Tenta aplicar o wallpaper. Se o arquivo não existir, o sistema roda com fundo padrão.
try:
    bin_str = get_base64('background.jpg')
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* Caixa de conteúdo semi-transparente para leitura */
    [data-testid="stVerticalBlock"] > div {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }}

    /* Estilo da barra lateral */
    [data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.8) !important;
    }}
    
    .st-emotion-cache-10trblm {{
        color: white !important;
    }}

    .tag {{
        background-color: #f1f1f1;
        padding: 4px 8px;
        border-radius: 5px;
        font-size: 12px;
        margin-right: 5px;
        border: 1px solid #ddd;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)
except Exception:
    st.info("Dica: Adicione o arquivo 'background.jpg' na pasta para ativar o wallpaper.")

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
        st.title("🔐 Login AMG Multimarcas")
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Entrar", on_click=password_guessed)
        return False
    elif not st.session_state["password_correct"]:
        st.error("Usuário ou senha incorretos")
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Entrar", on_click=password_guessed)
        return False
    return True

if check_password():
    # Inicialização de dados na memória
    if 'meu_estoque' not in st.session_state: st.session_state.meu_estoque = []
    if 'leads' not in st.session_state: st.session_state.leads = []

    st.title("🚗 CRM AMG Multimarcas")

    # Menu Lateral
    st.sidebar.markdown("<h2 style='color:white;'>Painel de Controle</h2>", unsafe_allow_html=True)
    aba = st.sidebar.radio("Navegação", ["Estoque / Cadastro", "Leads Site", "Anúncios Meta"])
    
    if st.sidebar.button("Sair"):
        st.session_state["password_correct"] = False
        st.rerun()

    # --- ABA: ESTOQUE ---
    if aba == "Estoque / Cadastro":
        st.subheader("📋 Cadastrar Veículo (Padrão Site)")
        with st.form("novo_carro", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                modelo = st.text_input("Modelo")
                marca = st.selectbox("Marca", ["Chevrolet", "Volkswagen", "Fiat", "Ford", "Hyundai", "Toyota", "Honda", "Nissan", "Renault", "Outros"])
                ano = st.text_input("Ano (Ex: 2013/2013)")
            with c2:
                km = st.number_input("Quilometragem", min_value=0)
                cambio = st.selectbox("Câmbio", ["Manual", "Automático"])
                combustivel = st.selectbox("Combustível", ["Flex", "Gasolina", "Diesel", "GNV"])
            with c3:
                valor = st.number_input("Preço de Venda (R$)", min_value=0)
                cor = st.text_input("Cor")
                foto = st.file_uploader("Foto Principal", type=['jpg', 'png', 'jpeg'])
            
            if st.form_submit_button("Adicionar ao Inventário"):
                st.session_state.meu_estoque.append({
                    "Modelo": modelo, "Marca": marca, "Ano": ano, "KM": km,
                    "Cambio": cambio, "Combustivel": combustivel,
                    "Preço": valor, "Cor": cor, "Foto": foto
                })
                st.success("Veículo cadastrado com sucesso!")

        # Lista de Veículos
        for idx, carro in enumerate(st.session_state.meu_estoque):
            with st.container():
                col_img, col_txt = st.columns([1, 2])
                with col_img:
                    if carro["Foto"]: st.image(carro["Foto"], use_container_width=True)
                with col_txt:
                    st.subheader(f"{carro['Marca']} {carro['Modelo']}")
                    st.markdown(f"**Valor:** <span style='color:green; font-size:18px;'>R$ {carro['Preço']:,.2f}</span>", unsafe_allow_html=True)
                    st.markdown(f"""
                        <span class="tag">📅 {carro['Ano']}</span>
                        <span class="tag">🛣️ {carro['KM']:,} KM</span>
                        <span class="tag">⚙️ {carro['Cambio']}</span>
                        <span class="tag">⛽ {carro['Combustivel']}</span>
                    """, unsafe_allow_html=True)
                st.divider()

    # --- ABA: LEADS ---
    elif aba == "Leads Site":
        st.subheader("👤 Leads Recebidos do Netlify")
        if not st.session_state.leads:
            st.info("Aguardando novas conexões do site...")
        else:
            st.table(pd.DataFrame(st.session_state.leads))

    # --- ABA: ANÚNCIOS ---
    elif aba == "Anúncios Meta":
        st.subheader("🚀 Gerador de Tráfego Facilitado")
        st.write("Selecione um carro do estoque para disparar um anúncio no Meta Ads.")
