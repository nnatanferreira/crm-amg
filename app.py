import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests

# --- 1. CONFIGURAÇÕES (API & CLOUDINARY) ---
API_FIPE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI0ZDk3YTE4NC1kOGIzLTQwOTEtOWVhOC1kNWQ0ZGUzYWZiNWQiLCJlbWFpbCI6Im5uYXRhbmZlcnJlaXJhQGdtYWlsLmNvbSIsImlhdCI6MTc3NjIwMTM4NH0.v_0pe0vEEuLCIMenEsLWZXSl_hdkXVq4oTzfhT4kdXM"

cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

st.set_page_config(page_title="CRM AMG Multimarcas", page_icon="🚗", layout="wide")

# --- 2. FUNÇÃO DE CONSULTA API ---
def consultar_dados_veiculo(placa):
    try:
        placa_limpa = placa.replace("-", "").strip().upper()
        if len(placa_limpa) != 7: return None
        url = f"https://api.fipe.online/v1/veiculos/{placa_limpa}"
        headers = {"Authorization": f"Bearer {API_FIPE_KEY}", "Content-Type": "application/json"}
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# --- 3. ESTILO VISUAL OTIMIZADO ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #f0f2f6 !important; color: #000000 !important; }
    h1, h2, h3 { color: #000000 !important; font-weight: 800 !important; }
    [data-testid="stWidgetLabel"] p { font-size: 1.1rem !important; font-weight: 700 !important; color: #000000 !important; }

    /* Inputs e Selects */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        border: 2px solid #000000 !important; color: #000000 !important; background-color: #ffffff !important;
    }

    /* BOTOES COM TEXTO BRANCO E FUNDO VERDE */
    button, .stButton>button, div.stFormSubmitButton>button {
        background-color: #1e7e34 !important;
        color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        border-radius: 12px !important;
        height: 60px !important;
        width: 100% !important;
        border: none !important;
    }

    /* Botão de Upload */
    [data-testid="stFileUploader"] section button {
        background-color: #333333 !important;
        color: #ffffff !important;
    }

    .car-card { border: 2px solid #000000; border-radius: 15px; padding: 15px; background-color: #ffffff; margin-bottom: 15px; }
    .preco-destaque { color: #1e7e34 !important; font-size: 1.8rem !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CONEXÃO E LOGIN ---
conn = st.connection("gsheets", type=GSheetsConnection)

if "autenticado" not in st.session_state:
    st.markdown("<h1 style='text-align: center;'>🚗 AMG Multimarcas</h1>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR SISTEMA"):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
            else: st.error("Dados de acesso incorretos.")
else:
    menu = st.sidebar.radio("Navegar:", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Cadastro de Veículo")
        
        c_busca1, c_busca2 = st.columns([2, 1])
        placa_in = c_busca1.text_input("Placa para consulta:", placeholder="ABC1D23").upper()
        
        if "dados_fipe" not in st.session_state: st.session_state.dados_fipe = {}

        if c_busca2.button("🔍 BUSCAR DADOS"):
            if placa_in:
                with st.spinner("Consultando FIPE..."):
                    res = consultar_dados_veiculo(placa_in)
                    if res:
                        st.session_state.dados_fipe = res.get("data", res)
                        st.success("Dados preenchidos!")
                    else: st.error("Erro na consulta.")

        with st.form("form_veiculo", clear_on_submit=True):
            f = st.session_state.dados_fipe
            st.subheader("🚗 Dados do Veículo")
            
            marca = st.text_input("Marca", value=f.get("marca", ""))
            modelo = st.text_input("Modelo e Versão", value=f.get("modelo", ""))
            placa_f = st.text_input("Placa Final", value=f.get("placa", placa_in))
            
            c1, c2, c3 = st.columns(3)
            with c1:
                ano_fab = st.text_input("Ano Fab.", value=str(f.get("ano_fabricacao", "")))
                renavam = st.text_input("Renavam", value=f.get("renavam", ""))
            with c2:
                ano_mod = st.text_input("Ano Mod.", value=str(f.get("ano_modelo", "")))
                chassi = st.text_input("Chassi", value=f.get("chassi", ""))
            with c3:
                cor = st.text_input("Cor", value=f.get("cor", ""))
                comb = st.text_input("Combustível", value=f.get("combustivel", ""))

            v1, v2 = st.columns(2)
            with v1:
                preco_f = f.get("preco_fipe", 0.0)
                try: p_val = float(preco_f)
                except: p_val = 0.0
                preco = st.number_input("Preço de Venda (R$)", value=p_val)
            with v2:
                km = st.number_input("Quilometragem", min_value=0)

            foto_v = st.file_uploader("📷 Foto Principal do Veículo", type=['jpg','png','jpeg'])

            st.markdown("---")
            st.subheader("👤 Proprietário / Titular (Opcional)")
            t1, t2 = st.columns(2)
            with t1:
                nome_t = st.text_input("Nome Completo")
                cpf_t = st.text_input("CPF")
            with t2:
                rg_t = st.text_input("RG")
                end_t = st.text_input("Endereço")
            
            doc_t = st.file_uploader("📂 Foto Documento Titular", type=['jpg','png','jpeg'])

            if st.form_submit_button("🚀 SALVAR EM ESTOQUE"):
                if modelo and placa_f and foto_v:
                    with st.spinner('Salvando...'):
                        img_car = cloudinary.uploader.upload(foto_v)
                        img_doc = ""
                        if doc_t:
                            img_doc = cloudinary.uploader.upload(doc_t)['secure_url']
                        
                        try:
                            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                        except:
                            df = pd.DataFrame()

                        novo = pd.DataFrame([{
                            "marca": marca, "modelo": modelo, "placa": placa_f.upper(),
                            "ano_fab": str(ano_fab), "ano_mod": str(ano_mod),
                            "renavam": renavam, "chassi": chassi.upper(),
                            "cor": cor, "combustivel": comb, "preco": preco, "km": km,
                            "foto": img_car['secure_url'], "nome_titular": nome_t,
                            "cpf_titular": cpf_t, "rg_titular": rg_t,
                            "endereco_titular": end_t, "doc_titular": img_doc
                        }])
                        conn.update(worksheet="Estoque", data=pd.concat([df, novo], ignore_index=True))
                        st.session_state.dados_fipe = {}
                        st.success("Veículo Cadastrado!")
                        st.rerun()
                else: st.warning("Obrigatório: Modelo, Placa e Foto do Carro.")

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        except:
            df = pd.DataFrame()

        if df.empty:
            st.info("Estoque vazio.")
        else:
            for i, r in df.iterrows():
                v_foto = r.get('foto', '')
                v_mod = r.get('modelo', 'Sem Modelo')
                v_pla = r.get('placa', '---')
                v_pre = r.get('preco', 0.0)
                
                st.markdown(f"""
                    <div class="car-card">
                        <img src="{v_foto}" style="width:100%; border-radius:10px; height:200px; object-fit:cover;">
                        <h3>{v_mod}</h3>
                        <p class="preco-destaque">R$ {float(v_pre):,.2f}</p>
                        <p><b>Placa:</b> {v_pla} | <b>Ano:</b> {r.get('ano_fab','')}/{r.get('ano_mod','')}</p>
                        <p><b>KM:</b> {r.get('km',0)} | <b>Cor:</b> {r.get('cor','')}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if r.get('doc_titular',''):
                    st.link_button("📂 Ver Documento Titular", r['doc_titular'], use_container_width=True)
                
                if st.button(f"🗑️ Excluir {v_pla}", key=f"del_{i}", use_container_width=True):
                    conn.update(worksheet="Estoque", data=df.drop(i))
                    st.rerun()
                st.markdown("---")
