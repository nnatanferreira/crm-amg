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
    try:
        response = requests.get(f"{BASE_URL}/brands")
        return response.json()
    except:
        return []

def get_modelos(brand_id):
    try:
        response = requests.get(f"{BASE_URL}/brands/{brand_id}/models")
        return response.json()
    except:
        return []

def get_anos(brand_id, model_id):
    try:
        response = requests.get(f"{BASE_URL}/brands/{brand_id}/models/{model_id}/years")
        return response.json()
    except:
        return []

def get_dados_finais(brand_id, model_id, year_id):
    try:
        response = requests.get(f"{BASE_URL}/brands/{brand_id}/models/{model_id}/years/{year_id}")
        return response.json()
    except:
        return {}

# --- 3. ESTILO VISUAL CUSTOMIZADO ---
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
    .preco-destaque { color: #1e7e34 !important; font-size: 1.5rem !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CONEXÃO E SISTEMA DE LOGIN ---
conn = st.connection("gsheets", type=GSheetsConnection)

if "autenticado" not in st.session_state:
    st.markdown("<h1 style='text-align: center;'>🚗 CRM AMG</h1>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ENTRAR NO SISTEMA"):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")
else:
    menu = st.sidebar.radio("Navegação", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    if st.sidebar.button("Encerrar Sessão"):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR VEÍCULO ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Cadastro de Veículo")
        
        # Fluxo de Seleção FIPE
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
                ano_fipe_sel = st.selectbox("3. Selecione o Ano Modelo", options=[""] + list(dict_anos.keys()))

                if ano_fipe_sel:
                    dados = get_dados_finais(dict_marcas[marca_n], dict_modelos[modelo_n], dict_anos[ano_fipe_sel])
                    
                    with st.form("form_cadastro", clear_on_submit=True):
                        st.subheader("🚗 Detalhes Técnicos")
                        
                        # Lista de Ano Fabricação/Modelo Combinados (1995 até 2027)
                        lista_anos_combinados = []
                        for a in range(2027, 1994, -1):
                            lista_anos_combinados.append(f"{a}/{a+1}")
                            lista_anos_combinados.append(f"{a}/{a}")
                        
                        try:
                            ano_fipe_num = int(dados.get('modelYear', 2024))
                            sugestao = f"{ano_fipe_num-1}/{ano_fipe_num}"
                        except:
                            sugestao = "2024/2025"
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            marca_f = st.text_input("Marca", value=dados.get('brand', marca_n))
                            modelo_f = st.text_input("Modelo/Versão", value=dados.get('model', modelo_n))
                            placa = st.text_input("Placa", placeholder="ABC1D23").upper()
                        
                        with col2:
                            ano_combo = st.selectbox("Ano Fabricação/Modelo", options=lista_anos_combinados, 
                                                   index=lista_anos_combinados.index(sugestao) if sugestao in lista_anos_combinados else 0)
                            cor = st.text_input("Cor")
                            combust = st.text_input("Combustível", value=dados.get('fuel', ''))

                        st.markdown("---")
                        c1, c2 = st.columns(2)
                        
                        # --- VALIDAÇÕES DE CHASSI E RENAVAM ---
                        renavam = c1.text_input("Renavam", help="9 ou 11 dígitos conforme o ano.")
                        chassi = c2.text_input("Chassi", help="Exatamente 17 caracteres.").upper()
                        
                        val_erros = []
                        if renavam and len(renavam) not in [9, 11]:
                            val_erros.append(f"❌ Renavam com {len(renavam)} dígitos. O correto é 9 ou 11.")
                        if chassi and len(chassi) != 17:
                            val_erros.append(f"❌ Chassi com {len(chassi)} caracteres. O correto é 17.")
                        
                        for erro in val_erros:
                            st.error(erro)

                        v1, v2 = st.columns(2)
                        p_fipe_str = dados.get('price', '0').replace('R$ ', '').replace('.', '').replace(',', '.')
                        preco = v1.number_input("Preço de Venda (R$)", value=float(p_fipe_str))
                        km = v2.number_input("Quilometragem (KM)", min_value=0)

                        foto_v = st.file_uploader("📷 Foto Principal do Veículo", type=['jpg','png','jpeg'])
                        
                        st.markdown("---")
                        st.subheader("👤 Proprietário / Titular")
                        t_nome = st.text_input("Nome Completo")
                        t_doc = st.file_uploader("📂 Foto do Documento (RG/CNH)", type=['jpg','png','jpeg'])

                        # BOTÃO DE SALVAMENTO COM TRAVA DE SEGURANÇA
                        if st.form_submit_button("🚀 FINALIZAR E SALVAR NO ESTOQUE"):
                            if not val_erros and placa and foto_v:
                                with st.spinner("Enviando dados para a nuvem..."):
                                    # Desmembrar ano selecionado
                                    ano_f_save, ano_m_save = ano_combo.split('/')
                                    
                                    # Upload Cloudinary
                                    url_foto = cloudinary.uploader.upload(foto_v)['secure_url']
                                    url_doc = cloudinary.uploader.upload(t_doc)['secure_url'] if t_doc else ""
                                    
                                    # Gravação na Planilha
                                    try:
                                        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                                    except:
                                        df = pd.DataFrame()

                                    novo = pd.DataFrame([{
                                        "marca": marca_f, "modelo": modelo_f, "placa": placa,
                                        "ano_fab": ano_f_save, "ano_mod": ano_m_save, "renavam": renavam,
                                        "chassi": chassi, "cor": cor, "combustivel": combust,
                                        "preco": preco, "km": km, "foto": url_foto,
                                        "nome_titular": t_nome, "doc_titular": url_doc
                                    }])
                                    
                                    df_final = pd.concat([df, novo], ignore_index=True)
                                    conn.update(worksheet="Estoque", data=df_final)
                                    
                                    st.success(f"Veículo {placa} cadastrado com sucesso!")
                                    st.rerun()
                            elif val_erros:
                                st.warning("Por favor, corrija os erros de digitação acima.")
                            else:
                                st.warning("Placa e Foto são campos obrigatórios.")

    # --- ABA: GERENCIAR ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        st.markdown("## 📑 Veículos em Estoque")
        try:
            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        except:
            df = pd.DataFrame()

        if df.empty:
            st.info("O estoque está vazio no momento.")
        else:
            # Grid de exibição
            for i, r in df.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="car-card">
                            <img src="{r.get('foto', '')}" style="width:100%; border-radius:10px; height:230px; object-fit:cover; border: 1px solid #ddd;">
                            <h2 style="margin-top:10px;">{r.get('marca', '')} {r.get('modelo', 'Sem Nome')}</h2>
                            <p class="preco-destaque">R$ {float(r.get('preco', 0)):,.2f}</p>
                            <p><b>Placa:</b> {r.get('placa', '-')} | <b>KM:</b> {r.get('km', 0)}</p>
                            <p><b>Ano:</b> {r.get('ano_fab', '')}/{r.get('ano_mod', '')} | <b>Cor:</b> {r.get('cor', '-')}</p>
                            <p><b>Combustível:</b> {r.get('combustivel', '-')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Botão de exclusão para cada veículo
                    if st.button(f"🗑️ Remover {r.get('placa', i)}", key=f"btn_del_{i}"):
                        novo_df = df.drop(i)
                        conn.update(worksheet="Estoque", data=novo_df)
                        st.success("Veículo removido!")
                        st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)
