import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests

# --- 1. CONFIGURAÇÕES CLOUDINARY ---
cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

st.set_page_config(page_title="CRM AMG Multimarcas", page_icon="🚗", layout="wide")

# --- 2. FUNÇÕES DA API FIPE (PARALLELUM) ---
BASE_URL = "https://fipe.parallelum.com.br/api/v2/cars"

@st.cache_data(ttl=3600)
def get_marcas():
    try: return requests.get(f"{BASE_URL}/brands").json()
    except: return []

def get_modelos(brand_id):
    try: return requests.get(f"{BASE_URL}/brands/{brand_id}/models").json()
    except: return []

def get_anos(brand_id, model_id):
    try: return requests.get(f"{BASE_URL}/brands/{brand_id}/models/{model_id}/years").json()
    except: return []

def get_dados_finais(brand_id, model_id, year_id):
    try: return requests.get(f"{BASE_URL}/brands/{brand_id}/models/{model_id}/years/{year_id}").json()
    except: return {}

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #f0f2f6 !important; color: #000000 !important; }
    [data-testid="stWidgetLabel"] p { font-size: 1.1rem !important; font-weight: 700 !important; color: #000000 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        border: 2px solid #000000 !important; color: #000000 !important; background-color: #ffffff !important;
    }
    button, .stButton>button, div.stFormSubmitButton>button {
        background-color: #1e7e34 !important; color: #ffffff !important;
        font-size: 1.2rem !important; font-weight: 900 !important;
        text-transform: uppercase !important; border-radius: 12px !important;
        height: 60px !important; width: 100% !important; border: none !important;
    }
    .car-card { border: 2px solid #000000; border-radius: 15px; padding: 15px; background-color: #ffffff; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CONEXÃO E LOGIN ---
conn = st.connection("gsheets", type=GSheetsConnection)

if "autenticado" not in st.session_state:
    st.markdown("<h1 style='text-align: center;'>🚗 CRM AMG</h1>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ENTRAR"):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
            else: st.error("Dados incorretos.")
else:
    menu = st.sidebar.radio("Navegação", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Cadastro de Veículo")
        
        # Seleção FIPE
        marcas = get_marcas()
        dict_marcas = {m['name']: m['code'] for m in marcas}
        marca_n = st.selectbox("1. Selecione a Marca", options=[""] + sorted(list(dict_marcas.keys())))

        if marca_n:
            modelos = get_modelos(dict_marcas[marca_n])
            dict_modelos = {m['name']: m['code'] for m in modelos}
            modelo_n = st.selectbox("2. Selecione o Modelo", options=[""] + sorted(list(dict_modelos.keys())))

            if modelo_n:
                anos_fipe = get_anos(dict_marcas[marca_n], dict_modelos[modelo_n])
                dict_anos = {a['name']: a['code'] for a in anos_fipe}
                ano_fipe_sel = st.selectbox("3. Selecione o Ano FIPE", options=[""] + list(dict_anos.keys()))

                if ano_fipe_sel:
                    dados = get_dados_finais(dict_marcas[marca_n], dict_modelos[modelo_n], dict_anos[ano_fipe_sel])
                    
                    with st.form("form_cadastro", clear_on_submit=True):
                        st.subheader("🚗 Detalhes do Veículo")
                        
                        # Preparar lista de Ano Fabricação/Modelo (Ex: 2024/2025)
                        # Geramos combinações: Ano/Ano e Ano/Ano+1
                        lista_anos_combinados = []
                        for a in range(2027, 1994, -1):
                            lista_anos_combinados.append(f"{a}/{a+1}")
                            lista_anos_combinados.append(f"{a}/{a}")
                        
                        # Sugestão baseada na FIPE
                        ano_fipe_num = int(dados.get('modelYear', 2024))
                        sugestao = f"{ano_fipe_num-1}/{ano_fipe_num}"
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            marca_f = st.text_input("Marca", value=dados.get('brand', marca_n))
                            modelo_f = st.text_input("Modelo", value=dados.get('model', modelo_n))
                            placa = st.text_input("Placa", placeholder="ABC1D23").upper()
                        
                        with col2:
                            ano_combo = st.selectbox("Ano Fabricação/Modelo", options=lista_anos_combinados, 
                                                   index=lista_anos_combinados.index(sugestao) if sugestao in lista_anos_combinados else 0)
                            cor = st.text_input("Cor")
                            combust = st.text_input("Combustível", value=dados.get('fuel', ''))

                        c1, c2 = st.columns(2)
                        renavam = c1.text_input("Renavam")
                        chassi = c2.text_input("Chassi").upper()

                        v1, v2 = st.columns(2)
                        p_fipe_str = dados.get('price', '0').replace('R$ ', '').replace('.', '').replace(',', '.')
                        preco = v1.number_input("Preço de Venda (R$)", value=float(p_fipe_str))
                        km = v2.number_input("Quilometragem", min_value=0)

                        foto_v = st.file_uploader("📷 Foto do Veículo", type=['jpg','png','jpeg'])
                        
                        st.markdown("---")
                        t_nome = st.text_input("Nome do Titular")
                        t_doc = st.file_uploader("📂 Documento do Titular", type=['jpg','png','jpeg'])

                        if st.form_submit_button("🚀 SALVAR VEÍCULO"):
                            if placa and foto_v:
                                with st.spinner("Salvando..."):
                                    # Separar os anos selecionados
                                    ano_f_save, ano_m_save = ano_combo.split('/')
                                    
                                    url_foto = cloudinary.uploader.upload(foto_v)['secure_url']
                                    url_doc = cloudinary.uploader.upload(t_doc)['secure_url'] if t_doc else ""
                                    
                                    try: df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                                    except: df = pd.DataFrame()

                                    novo = pd.DataFrame([{
                                        "marca": marca_f, "modelo": modelo_f, "placa": placa,
                                        "ano_fab": ano_f_save, "ano_mod": ano_m_save, "renavam": renavam,
                                        "chassi": chassi, "cor": cor, "combustivel": combust,
                                        "preco": preco, "km": km, "foto": url_foto,
                                        "nome_titular": t_nome, "doc_titular": url_doc
                                    }])
                                    conn.update(worksheet="Estoque", data=pd.concat([df, novo], ignore_index=True))
                                    st.success(f"Veículo {ano_combo} Salvo!")
                                    st.rerun()
                            else: st.warning("Placa e Foto são obrigatórios.")

    elif menu == "📑 Gerenciar Estoque":
        try: df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        except: df = pd.DataFrame()

        if df.empty: st.info("Estoque vazio.")
        else:
            for i, r in df.iterrows():
                st.markdown(f"""
                    <div class="car-card">
                        <img src="{r.get('foto', '')}" style="width:100%; border-radius:10px; height:200px; object-fit:cover;">
                        <h3>{r.get('modelo', 'Sem Nome')}</h3>
                        <p style="color:#1e7e34; font-size:1.4rem; font-weight:900;">R$ {float(r.get('preco', 0)):,.2f}</p>
                        <p><b>Placa:</b> {r.get('placa', '-')} | <b>Ano:</b> {r.get('ano_fab', '')}/{r.get('ano_mod', '')}</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ Excluir {r.get('placa', i)}", key=f"del_{i}"):
                    conn.update(worksheet="Estoque", data=df.drop(i))
                    st.rerun()
