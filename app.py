import streamlit as st
import pandas as pd

# 1. Configuração da Página e Identidade Visual (Aba do Navegador)
st.set_page_config(
    page_title="CRM Amg Multimarcas",
    page_icon="🚗",
    layout="wide", # Essencial para responsividade
    initial_sidebar_state="collapsed" # Começa com menu fechado no celular
)

# 2. Estilização CSS para Dark Mode e Layout Responsivo
# Usamos Markdown para injetar CSS direto na página.
st.markdown("""
    <style>
    /* Fundo Totalmente Preto da Aplicação */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }

    /* Estilo da Barra Lateral (Menu) - Cinza Escuro */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
        color: #ffffff;
    }
    
    /* Cor dos textos e ícones na barra lateral */
    [data-testid="stSidebar"] *, .st-emotion-cache-10trblm {
        color: #ffffff !important;
    }

    /* Títulos Principais em Branco */
    h1, h2, h3, .stSubheader {
        color: #ffffff !important;
        font-weight: 700;
    }

    /* Inputs de Texto e Botões (Formulários) */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #262626;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    /* Botões Principais (Salvar, Enviar) */
    .stButton>button {
        background-color: #ffffff;
        color: #000000;
        border-radius: 5px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #cccccc;
    }

    /* Cards de Veículos no Estoque - Estilo Site */
    .car-card {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .car-card:hover {
        border-color: #555555;
    }

    /* Tags de Características (Ano, KM, Câmbio) */
    .tag {
        background-color: #333333;
        color: #eeeeee;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        margin-right: 5px;
        display: inline-block;
        margin-bottom: 5px;
    }

    /* Preço em Destaque (Verde para contraste) */
    .price-tag {
        color: #00ff00;
        font-size: 20px;
        font-weight: bold;
    }

    /* Responsividade para Imagens */
    img {
        max-width: 100%;
        height: auto;
    }
    
    /* Responsividade para tabelas */
    .stDataFrame {
        width: 100% !important;
    }

    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
def check_password():
    """Retorna True se o usuário inseriu a senha correta."""
    def password_guessed():
        if st.session_state["username"] == "amgmultimarcas" and st.session_state["password"] == "amg0031":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Remove a senha da memória
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Tela de Login Estilizada para Dark Mode
        st.markdown("<h1 style='text-align: center;'>🔐 Acesso AMG Multimarcas</h1>", unsafe_allow_html=True)
        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            st.button("Entrar no CRM", on_click=password_guessed, use_container_width=True)
        return False
    elif not st.session_state["password_correct"]:
        st.error("Usuário ou senha incorretos.")
        # ... (reexibe o form de login)
        return False
    return True

# --- EXECUÇÃO DO SISTEMA PRINCIPAL ---
if check_password():
    
    # Inicialização de dados na memória (se não existirem)
    if 'meu_estoque' not in st.session_state: st.session_state.meu_estoque = []
    if 'leads' not in st.session_state: st.session_state.leads = []

    # 3. Logo AMG no Topo (Centralizado e Responsivo)
    # Como não temos o arquivo do logo puro, usamos o texto estilizado
    st.markdown("<h1 style='text-align: center; font-size: 40px; letter-spacing: 2px;'>AMG <span style='font-weight:100; font-size:20px;'>MULTIMARCAS</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Gravataí - RS</p>", unsafe_allow_html=True)
    st.divider()

    # Menu Lateral (Dark Mode)
    st.sidebar.markdown("<h2 style='color:white; text-align:center;'>Menu</h2>", unsafe_allow_html=True)
    aba = st.sidebar.radio("Navegação", ["Estoque / Cadastro", "Leads Site", "Anúncios Meta"])
    
    st.sidebar.divider()
    if st.sidebar.button("Sair (Logout)", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()

    # --- ABA: ESTOQUE (Estilo Dark Site) ---
    if aba == "Estoque / Cadastro":
        st.subheader("📋 Cadastrar Veículo")
        with st.form("novo_carro", clear_on_submit=True):
            # Organização em colunas para PC, empilha no celular automaticamente
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                modelo = st.text_input("Modelo (Ex: Ranger Limited 3.2)")
                marca = st.selectbox("Marca", ["Ford", "Chevrolet", "Volkswagen", "Fiat", "Hyundai", "Toyota", "Honda", "Renault", "Outros"])
                ano = st.text_input("Ano (Ex: 2019/2020)")
            with c2:
                km = st.number_input("KM", min_value=0, step=1000)
                cambio = st.selectbox("Câmbio", ["Automático", "Manual"])
            with c3:
                valor = st.number_input("Preço (R$)", min_value=0, step=1000)
                cor = st.text_input("Cor")
                foto = st.file_uploader("Foto Principal", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("Adicionar ao CRM", use_container_width=True):
                if modelo and valor > 0:
                    st.session_state.meu_estoque.append({
                        "Modelo": modelo, "Marca": marca, "Ano": ano, "KM": km,
                        "Cambio": cambio, "Preço": valor, "Cor": cor, "Foto": foto
                    })
                    st.success(f"{modelo} adicionado!")
                else:
                    st.error("Preencha Modelo e Preço.")

        # Exibição do Estoque (Cards Responsivos)
        if st.session_state.meu_estoque:
            st.divider()
            st.subheader("🚘 Estoque Atual")
            
            for idx, carro in enumerate(st.session_state.meu_estoque):
                # Cria o card visual usando HTML/CSS dentro do Streamlit
                st.markdown(f"""
                <div class="car-card">
                    <div style="display: flex; flex-wrap: wrap; gap: 15px; align-items: center;">
                        <div style="flex: 1; min-width: 200px; max-width: 300px;">
                            </div>
                        <div style="flex: 2; min-width: 250px;">
                            <h3 style="margin: 0 0 5px 0;">{carro['Marca']} {carro['Modelo']}</h3>
                            <p class="price-tag">R$ {carro['Preço']:,.2f}</p>
                            <div style="margin-top: 10px;">
                                <span class="tag">📅 {carro['Ano']}</span>
                                <span class="tag">🛣️ {carro['KM']:,} KM</span>
                                <span class="tag">⚙️ {carro['Cambio']}</span>
                                <span class="tag">🎨 {carro['Cor']}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Renderiza a foto de forma responsiva acima do texto do card (limitação do Streamlit)
                if carro["Foto"]:
                    st.image(carro["Foto"], width=200)
                else:
                    st.info("Sem foto")
                st.divider()

    # --- ABA: LEADS ---
    elif aba == "Leads Site":
        st.subheader("👤 Leads Recebidos (Netlify)")
        if not st.session_state.leads:
            st.info("Aguardando novas conexões do site...")
        else:
            # Exibe os leads em uma tabela responsiva
            df_leads = pd.DataFrame(st.session_state.leads)
            st.dataframe(df_leads, use_container_width=True)

    # --- ABA: ANÚNCIOS ---
    elif aba == "Anúncios Meta":
        st.subheader("🚀 Gerenciador de Tráfego Facilitado")
        st.write("Selecione o veículo do estoque para configurar a campanha no Facebook Ads.")
        # (Próximo passo: Integração de API)
