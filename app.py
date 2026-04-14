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

# --- 2. FUNÇÕES DA API FIPE ---
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
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
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
            else: st.error("Acesso negado")
else:
    menu = st.sidebar.radio("Navegação", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Novo Cadastro")
        
        marcas = get_marcas()
        dict_marcas = {m['name']: m['code'] for m in marcas}
        marca_n = st.selectbox("1. Marca", options=[""] + sorted(list(dict_marcas.keys())))

        if marca_n:
            modelos = get_modelos(dict_marcas[marca_n])
            dict_modelos = {m['name']: m['code'] for m in modelos}
            modelo_n = st.selectbox("2. Modelo", options=[""] + sorted(list(dict_modelos.keys())))

            if modelo_n:
                anos_fipe = get_anos(dict_marcas[marca_n], dict_modelos[modelo_n])
                dict_anos = {a['name']: a['code'] for a in anos_fipe}
                ano_fipe_sel = st.selectbox("3. Ano Modelo", options=[""] + list(dict_anos.keys()))

                if ano_fipe_sel:
                    dados_f = get_dados_finais(dict_marcas[marca_n], dict_modelos[modelo_n], dict_anos[ano_fipe_sel])
                    
                    with st.form("form_veiculo"):
                        st.subheader("🚗 Detalhes do Veículo")
                        
                        lista_anos = []
                        for a in range(2027, 1994, -1):
                            lista_anos.append(f"{a}/{a+1}")
                            lista_anos.append(f"{a}/{a}")
                        
                        try:
                            ano_ref = int(dados_f.get('modelYear', 2024))
                            sugestao_ano = f"{ano_ref-1}/{ano_ref}"
                        except: sugestao_ano = "2024/2025"

                        c1, c2 = st.columns(2)
                        marca_val = c1.text_input("Marca", value=dados_f.get('brand', marca_n))
                        modelo_val = c1.text_input("Modelo", value=dados_f.get('model', modelo_n))
                        placa = c1.text_input("Placa").upper()
                        
                        ano_combo = c2.selectbox("Ano Fab/Mod", options=lista_anos, 
                                               index=lista_anos.index(sugestao_ano) if sugestao_ano in lista_anos else 0)
                        cor = c2.text_input("Cor")
                        combust = c2.text_input("Combustível", value=dados_f.get('fuel', ''))

                        st.markdown("---")
                        c3, c4 = st.columns(2)
                        # Removemos caracteres especiais para a contagem, mas salvamos o que o usuário digitar
                        renavam = c3.text_input("Renavam")
                        chassi = c4.text_input("Chassi").upper()
                        
                        renavam_clean = "".join(filter(str.isdigit, renavam)) if renavam else ""
                        chassi_clean = chassi.replace(" ", "").replace("-", "") if chassi else ""

                        v1, v2 = st.columns(2)
                        p_fipe = dados_f.get('price', '0').replace('R$ ', '').replace('.', '').replace(',', '.')
                        preco = v1.text_input("Valor de Venda (R$)", value=p_fipe)
                        km = v2.text_input("KM Atual", value="0")

                        foto_v = st.file_uploader("📷 Foto do Veículo (Opcional)", type=['jpg','png','jpeg'])
                        
                        st.markdown("---")
                        t_nome = st.text_input("Nome do Titular")
                        t_doc = st.file_uploader("📂 Foto Documento", type=['jpg','png','jpeg'])

                        if st.form_submit_button("🚀 SALVAR NO ESTOQUE"):
                            # Validação flexível: se preencher, tem que ter a qtd correta. Se não preencher, passa.
                            erro_renavam = renavam and len(renavam_clean) not in [9, 11]
                            erro_chassi = chassi and len(chassi_clean) != 17
                            
                            if not erro_renavam and not erro_chassi and placa:
                                with st.spinner("Gravando dados..."):
                                    af, am = ano_combo.split('/')
                                    url_img = cloudinary.uploader.upload(foto_v)['secure_url'] if foto_v else ""
                                    url_doc = cloudinary.uploader.upload(t_doc)['secure_url'] if t_doc else ""
                                    
                                    try:
                                        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                                    except:
                                        df = pd.DataFrame(columns=["marca", "modelo", "placa", "ano_fab", "ano_mod", "renavam", "chassi", "cor", "combustivel", "preco", "km", "foto", "nome_titular", "doc_titular"])

                                    novo = pd.DataFrame([{
                                        "marca": marca_val, "modelo": modelo_val, "placa": placa,
                                        "ano_fab": af, "ano_mod": am, "renavam": renavam,
                                        "chassi": chassi, "cor": cor, "combustivel": combust,
                                        "preco": preco, "km": km, "foto": url_img,
                                        "nome_titular": t_nome, "doc_titular": url_doc
                                    }])
                                    
                                    df_final = pd.concat([df, novo], ignore_index=True)
                                    conn.update(worksheet="Estoque", data=df_final)
                                    st.success("Veículo cadastrado!")
                                    st.rerun()
                            else:
                                if not placa: st.error("A Placa é obrigatória.")
                                if erro_renavam: st.error(f"Renavam inválido ({len(renavam_clean)} dígitos). Use 9 ou 11.")
                                if erro_chassi: st.error(f"Chassi inválido ({len(chassi_clean)} caracteres). Use 17.")

    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        except:
            df = pd.DataFrame()

        if df.empty or "placa" not in df.columns:
            st.info("Estoque vazio.")
        else:
            for i, r in df.iterrows():
                st.markdown(f"""
                    <div class="car-card">
                        <img src="{r.get('foto', '')}" style="width:100%; border-radius:10px; height:200px; object-fit:cover;">
                        <h3>{r.get('modelo', 'Sem Nome')}</h3>
                        <p style="color:#1e7e34; font-size:1.4rem; font-weight:900;">R$ {r.get('preco', '0')}</p>
                        <p><b>Placa:</b> {r.get('placa', '-')} | <b>Ano:</b> {r.get('ano_fab', '')}/{r.get('ano_mod', '')}</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ Excluir {r.get('placa', i)}", key=f"del_{i}"):
                    conn.update(worksheet="Estoque", data=df.drop(i))
                    st.rerun()
