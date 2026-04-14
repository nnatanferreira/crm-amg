import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests
import time

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
        height: 50px !important; width: 100% !important; border: none !important;
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

    # --- ABA: CADASTRAR ---
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
                        renavam = c3.text_input("Renavam")
                        chassi = c4.text_input("Chassi").upper()
                        
                        v1, v2 = st.columns(2)
                        p_fipe = dados_f.get('price', '0').replace('R$ ', '').replace('.', '').replace(',', '.')
                        preco = v1.text_input("Valor de Venda (R$)", value=p_fipe)
                        km = v2.text_input("KM Atual", value="0")

                        foto_v = st.file_uploader("📷 Foto do Veículo (Opcional)", type=['jpg','png','jpeg'])
                        t_nome = st.text_input("Nome do Titular")
                        t_doc = st.file_uploader("📂 Foto Documento Titular", type=['jpg','png','jpeg'])

                        if st.form_submit_button("🚀 SALVAR NO ESTOQUE"):
                            r_clean = "".join(filter(str.isdigit, renavam)) if renavam else ""
                            c_clean = chassi.replace(" ", "").replace("-", "") if chassi else ""
                            
                            erro_r = renavam and len(r_clean) not in [9, 11]
                            erro_c = chassi and len(c_clean) != 17
                            
                            if not erro_r and not erro_c and placa:
                                barra_info = st.info("⏳ Salvando... Por favor, não feche a página.")
                                try:
                                    url_img = cloudinary.uploader.upload(foto_v)['secure_url'] if foto_v else ""
                                    url_doc = cloudinary.uploader.upload(t_doc)['secure_url'] if t_doc else ""
                                    
                                    af, am = ano_combo.split('/')
                                    df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                                    
                                    novo = pd.DataFrame([{
                                        "marca": marca_val, "modelo": modelo_val, "placa": placa,
                                        "ano_fab": af, "ano_mod": am, "renavam": renavam,
                                        "chassi": chassi, "cor": cor, "combustivel": combust,
                                        "preco": preco, "km": km, "foto": url_img,
                                        "nome_titular": t_nome, "doc_titular": url_doc
                                    }])
                                    
                                    conn.update(worksheet="Estoque", data=pd.concat([df, novo], ignore_index=True))
                                    barra_info.empty()
                                    st.success("✅ Concluído com sucesso!")
                                    time.sleep(1.5)
                                    st.rerun()
                                except Exception as e: st.error(f"Erro ao salvar: {e}")
                            else:
                                st.error("Corrija a Placa ou a quantidade de caracteres de Renavam/Chassi.")

    # --- ABA: ESTOQUE E EDIÇÃO ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        except:
            df = pd.DataFrame()

        if df.empty:
            st.info("Estoque vazio.")
        elif "edit_index" in st.session_state:
            idx = st.session_state.edit_index
            carro = df.iloc[idx]
            st.markdown(f"### ✏️ Editando: {carro['placa']}")
            
            with st.form("form_edicao"):
                lista_anos = [f"{a}/{a+1}" for a in range(2027, 1994, -1)] + [f"{a}/{a}" for a in range(2027, 1994, -1)]
                lista_anos.sort(reverse=True)
                
                c1, c2 = st.columns(2)
                m_e = c1.text_input("Marca", value=carro['marca'])
                mo_e = c1.text_input("Modelo", value=carro['modelo'])
                pl_e = c1.text_input("Placa", value=carro['placa']).upper()
                
                ano_atual = f"{carro['ano_fab']}/{carro['ano_mod']}"
                an_e = c2.selectbox("Ano Fab/Mod", options=lista_anos, index=lista_anos.index(ano_atual) if ano_atual in lista_anos else 0)
                co_e = c2.text_input("Cor", value=carro['cor'])
                cm_e = c2.text_input("Combustível", value=carro['combustivel'])
                
                st.markdown("---")
                v1, v2 = st.columns(2)
                pr_e = v1.text_input("Preço", value=carro['preco'])
                km_e = v2.text_input("KM", value=carro['km'])
                
                f_e = st.file_uploader("Trocar Foto", type=['jpg','png','jpeg'])
                
                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 CONCLUIR EDIÇÃO"):
                    st.info("⏳ Atualizando dados...")
                    u_f = carro['foto']
                    if f_e: u_f = cloudinary.uploader.upload(f_e)['secure_url']
                    
                    af_e, am_e = an_e.split('/')
                    df.at[idx, 'marca'] = m_e
                    df.at[idx, 'modelo'] = mo_e
                    df.at[idx, 'placa'] = pl_e
                    df.at[idx, 'ano_fab'] = af_e
                    df.at[idx, 'ano_mod'] = am_e
                    df.at[idx, 'preco'] = pr_e
                    df.at[idx, 'km'] = km_e
                    df.at[idx, 'foto'] = u_f
                    
                    conn.update(worksheet="Estoque", data=df)
                    st.success("✅ Atualizado!")
                    del st.session_state.edit_index
                    time.sleep(1)
                    st.rerun()
                
                if b2.form_submit_button("❌ CANCELAR"):
                    del st.session_state.edit_index
                    st.rerun()
        else:
            for i, r in df.iterrows():
                st.markdown(f"""
                    <div class="car-card">
                        <img src="{r.get('foto', '')}" style="width:100%; border-radius:10px; height:200px; object-fit:cover;">
                        <h3>{r.get('modelo', '')}</h3>
                        <p style="color:#1e7e34; font-size:1.4rem; font-weight:900;">R$ {r.get('preco', '0')}</p>
                        <p><b>Placa:</b> {r.get('placa', '-')} | <b>Ano:</b> {r.get('ano_fab', '')}/{r.get('ano_mod', '')}</p>
                    </div>
                """, unsafe_allow_html=True)
                col_a, col_b = st.columns(2)
                if col_a.button(f"✏️ Editar", key=f"e_{i}"):
                    st.session_state.edit_index = i
                    st.rerun()
                if col_b.button(f"🗑️ Excluir", key=f"d_{i}"):
                    conn.update(worksheet="Estoque", data=df.drop(i))
                    st.rerun()
