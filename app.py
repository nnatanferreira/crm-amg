import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd

# --- 1. CONFIGURAÇÃO DO CLOUDINARY (MEMORIZADO) ---
cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

# Configuração da Página
st.set_page_config(
    page_title="CRM AMG Multimarcas", 
    page_icon="🚗", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SUPER LAYOUT (FOCO EM QUADROS E FONTES GRANDES) ---
st.markdown("""
    <style>
    /* Estilo Geral */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa !important;
        color: #1a1a1a !important;
    }
    
    /* Fontes de Títulos */
    h1 { font-size: 3.5rem !important; font-weight: 800 !important; }
    h2 { font-size: 2.8rem !important; margin-bottom: 30px !important; font-weight: 700 !important; }
    h3 { font-size: 2rem !important; font-weight: 700 !important; color: #000 !important; }
    
    /* MENU LATERAL */
    [data-testid="stSidebar"] {
        min-width: 350px !important;
        background-color: #ffffff !important;
    }
    
    /* INPUTS E QUADROS DE CADASTRO (TURBO) */
    /* Aumenta o tamanho das etiquetas (labels) acima dos campos */
    [data-testid="stWidgetLabel"] p {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #000 !important;
        margin-bottom: 10px !important;
    }

    /* Aumenta a caixa de texto, número e seleção */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 1.5rem !important;
        height: 70px !important;
        border-radius: 12px !important;
        border: 2px solid #ccc !important;
    }

    /* Ajuste específico para o seletor (dropdown) */
    div[data-baseweb="select"] > div {
        height: 70px !important;
        display: flex;
        align-items: center;
    }

    /* Aumenta o campo de upload de arquivo */
    [data-testid="stFileUploader"] {
        font-size: 1.3rem !important;
    }

    /* BOTÃO SALVAR (GIGANTE) */
    .stButton button {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        height: 85px !important;
        border-radius: 15px !important;
        background-color: #1e7e34 !important;
        color: white !important;
        margin-top: 20px !important;
    }

    /* ESTILO DOS CARDS DE ESTOQUE */
    .car-card { 
        border: 2px solid #eee; 
        border-radius: 20px; 
        padding: 25px; 
        background-color: #ffffff;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.1);
        height: 100%;
    }

    .preco-destaque { 
        color: #1e7e34 !important; 
        font-size: 2.5rem !important; 
        font-weight: 900 !important;
    }

    .info-carro { font-size: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXÃO COM GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    conexao_ok = True
except Exception as e:
    conexao_ok = False

# --- 4. SISTEMA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🚗 AMG Multimarcas</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA", use_container_width=True):
                if u == "amgmultimarcas" and p == "amg0031":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Dados incorretos.")
else:
    st.sidebar.markdown("# ⚙️ MENU AMG")
    menu = st.sidebar.radio("Navegar:", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR (QUADROS AMPLIADOS) ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Novo Cadastro de Veículo")
        with st.form("form_cadastro", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                marca = st.selectbox("Marca", ["Nissan", "Ford", "Chevrolet", "VW", "Fiat", "Toyota", "Honda", "Mitsubishi", "Renault", "Hyundai", "Jeep", "BMW", "Mercedes", "Outra"])
                modelo = st.text_input("Modelo e Versão")
                ano = st.text_input("Ano (Ex: 2020 ou 2020/2021)")
            with c2:
                preco = st.number_input("Preço de Venda (R$)", min_value=0.0, step=1000.0)
                km = st.number_input("Quilometragem Atual", min_value=0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            foto_arquivo = st.file_uploader("📷 Selecione a Foto do Carro", type=['jpg', 'jpeg', 'png'])
            
            # Botão de salvar agora é uma ação de destaque
            enviar = st.form_submit_button("🚀 SALVAR NO ESTOQUE", use_container_width=True)
            
            if enviar:
                if modelo and foto_arquivo:
                    with st.spinner('Cadastrando...'):
                        res = cloudinary.uploader.upload(foto_arquivo)
                        url_foto = res['secure_url']
                        df_atual = conn.read(ttl=0).dropna(how='all')
                        
                        novo = pd.DataFrame([{
                            "marca": marca, "modelo": modelo, "ano": str(ano), 
                            "preco": preco, "km": km, "foto": url_foto
                        }])
                        
                        df_final = pd.concat([df_atual, novo], ignore_index=True)
                        conn.update(data=df_final)
                        st.success(f"Veículo {modelo} salvo com sucesso!")
                else:
                    st.warning("Atenção: Modelo e Foto são obrigatórios.")

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read(ttl=0).dropna(how='all')
            if df.empty:
                st.info("O estoque está vazio no momento.")
            else:
                st.markdown(f"## 🚘 Estoque Atual ({len(df)} veículos)")
                cols = st.columns(3)
                for index, row in df.iterrows():
                    p_f = f"R$ {row['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    k_f = f"{int(row['km']):,}".replace(",", ".")
                    ano_limpo = str(row['ano']).replace(".0", "")
                    
                    with cols[index % 3]:
                        st.markdown(f"""
                            <div class="car-card">
                                <img src="{row['foto']}" style="width:100%; border-radius:15px; margin-bottom:15px;">
                                <h3>{row['marca']} {row['modelo']}</h3>
                                <p class="preco-destaque">{p_f}</p>
                                <div class="info-carro">
                                    <b>📅 Ano:</b> {ano_limpo}<br>
                                    <b>🛣️ KM:</b> {k_f}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"🗑️ Excluir", key=f"btn_{index}", use_container_width=True):
                            df_novo = df.drop(index)
                            conn.update(data=df_novo)
                            st.rerun()
                        st.markdown("<br>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar estoque: {e}")
