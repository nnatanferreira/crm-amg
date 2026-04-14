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
    return requests.get(f"{BASE_URL}/brands").json()

def get_modelos(brand_id):
    return requests.get(f"{BASE_URL}/brands/{brand_id}/models").json()

def get_anos(brand_id, model_id):
    return requests.get(f"{BASE_URL}/brands/{brand_id}/models/{model_id}/years").json()

def get_dados_finais(brand_id, model_id, year_id):
    return requests.get(f"{BASE_URL}/brands/{brand_id}/models/{model_id}/years/{year_id}").json()

# --- 3. ESTILO VISUAL (MESMO QUE VOCÊ GOSTOU) ---
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
    .preco-destaque { color: #1e7e34 !important; font-size: 1.6rem !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CONEXÃO E LOGIN ---
conn = st.connection("gsheets", type=GSheetsConnection)

if "autenticado" not in st.session_state:
    st.markdown("<h1 style='text-align: center;'>🚗 CRM AMG</h1>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR SISTEMA"):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
            else: st.error("Acesso Negado")
else:
    menu = st.sidebar.radio("Navegação", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Cadastro via Tabela FIPE")
        
        # Etapa 1: Marca
        marcas = get_marcas()
        dict_marcas = {m['name']: m['code'] for m in marcas}
        marca_n = st.selectbox("1. Selecione a Marca", options=[""] + sorted(list(dict_marcas.keys())))

        if marca_n:
            # Etapa 2: Modelo
            modelos = get_modelos(dict_marcas[marca_n])
            dict_modelos = {m['name']: m['code'] for m in modelos}
            modelo_n = st.selectbox("2. Selecione o Modelo", options=[""] + sorted(list(dict_modelos.keys())))

            if modelo_n:
                # Etapa 3: Ano
                anos = get_anos(dict_marcas[marca_n], dict_modelos[modelo_n])
                dict_anos = {a['name']: a['code'] for a in anos}
                ano_n = st.selectbox("3. Selecione o Ano/Combustível", options=[""] + list(dict_anos.keys()))

                if ano_n:
                    # Carrega dados da FIPE para preencher o formulário
                    dados_fipe = get_dados_finais(dict_marcas[marca_n], dict_modelos[modelo_n], dict_anos[ano_n])
                    
                    with st.form("form_cadastro", clear_on_submit=True):
                        st.subheader("🚗 Detalhes do Veículo")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            marca_final = st.text_input("Marca", value=dados_fipe.get('brand', marca_n))
                            modelo_final = st.text_input("Modelo", value=dados_fipe.get('model', modelo_n))
                            placa = st.text_input("Placa", placeholder="ABC1D23").upper()
                        with col2:
                            ano_mod = st.text_input("Ano Modelo", value=str(dados_fipe.get('modelYear', '')))
                            combust = st.text_input("Combustível", value=dados_fipe.get('fuel', ''))
                            cor = st.text_input("Cor")

                        c3, c4, c5 = st.columns(3)
                        renavam = c3.text_input("Renavam")
                        chassi = c4.text_input("Chassi").upper()
                        ano_fab = c5.text_input("Ano Fabricação")

                        v1, v2 = st.columns(2)
                        # Limpeza do preço FIPE para número
                        p_fipe_str = dados_fipe.get('price', '0').replace('R$ ', '').replace('.', '').replace(',', '.')
                        preco_venda = v1.number_input("Preço de Venda (R$)", value=float(p_fipe_str))
                        km = v2.number_input("Quilometragem", min_value=0)

                        foto_v = st.file_uploader("📷 Foto do Veículo", type=['jpg','png','jpeg'])

                        st.markdown("---")
                        st.subheader("👤 Proprietário (Opcional)")
                        t_nome = st.text_input("Nome Completo")
                        t_doc = st.file_uploader("📂 Foto Documento", type=['jpg','png','jpeg'])

                        if st.form_submit_button("🚀 SALVAR NO ESTOQUE"):
                            if modelo_final and placa and foto_v:
                                with st.spinner("Salvando dados e imagens..."):
                                    # Upload Cloudinary
                                    url_foto = cloudinary.uploader.upload(foto_v)['secure_url']
                                    url_doc = cloudinary.uploader.upload(t_doc)['secure_url'] if t_doc else ""

                                    # Lógica Google Sheets
                                    try:
                                        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                                    except:
                                        df = pd.DataFrame()

                                    novo = pd.DataFrame([{
                                        "marca": marca_final, "modelo": modelo_final, "placa": placa,
                                        "ano_fab": ano_fab, "ano_mod": ano_mod, "renavam": renavam,
                                        "chassi": chassi, "cor": cor, "combustivel": combust,
                                        "preco": preco_venda, "km": km, "foto": url_foto,
                                        "nome_titular": t_nome, "doc_titular": url_doc
                                    }])

                                    conn.update(worksheet="Estoque", data=pd.concat([df, novo], ignore_index=True))
                                    st.success("Veículo cadastrado com sucesso!")
                                    st.rerun()
                            else:
                                st.warning("Preencha Placa, Modelo e Foto do Veículo.")

    # --- ABA: GERENCIAR ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        except:
            df = pd.DataFrame()

        if df.empty:
            st.info("Estoque vazio.")
        else:
            for i, r in df.iterrows():
                st.markdown(f"""
                    <div class="car-card">
                        <img src="{r.get('foto', '')}" style="width:100%; border-radius:10px; height:220px; object-fit:cover;">
                        <h3>{r.get('modelo', 'Sem Nome')}</h3>
                        <p class="preco-destaque">R$ {float(r.get('preco', 0)):,.2f}</p>
                        <p><b>Placa:</b> {r.get('placa', '-')} | <b>KM:</b> {r.get('km', 0)}</p>
                        <p><b>Ano:</b> {r.get('ano_mod', '-')} | <b>Cor:</b> {r.get('cor', '-')}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🗑️ Excluir {r.get('placa', i)}", key=f"del_{i}"):
                    conn.update(worksheet="Estoque", data=df.drop(i))
                    st.rerun()
                st.markdown("---")
