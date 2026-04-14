import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests

# --- 1. CONFIGURAÇÕES ---
# Chave da API (Verifique se ainda é válida ou se não expirou os créditos)
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
        # Aumentei o tempo de espera para 20 segundos para evitar erro de conexão lenta
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #f0f2f6 !important; color: #000000 !important; }
    [data-testid="stWidgetLabel"] p { font-size: 1.1rem !important; font-weight: 700 !important; color: #000000 !important; }
    .stTextInput input, .stNumberInput input { border: 2px solid #000000 !important; }
    button, .stButton>button, div.stFormSubmitButton>button {
        background-color: #1e7e34 !important; color: #ffffff !important;
        font-size: 1.2rem !important; font-weight: 900 !important;
        border-radius: 12px !important; height: 60px !important; width: 100% !important;
    }
    .car-card { border: 2px solid #000000; border-radius: 15px; padding: 15px; background-color: #ffffff; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CONEXÃO ---
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
            else: st.error("Acesso negado.")
else:
    menu = st.sidebar.radio("Navegação", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Novo Cadastro")
        
        if "dados_fipe" not in st.session_state: st.session_state.dados_fipe = {}

        c_p1, c_p2 = st.columns([2, 1])
        placa_busca = c_p1.text_input("Placa:", placeholder="ABC1D23").upper()
        
        if c_p2.button("🔍 BUSCAR DADOS"):
            if placa_busca:
                with st.spinner("Buscando na base nacional..."):
                    res = consultar_dados_veiculo(placa_busca)
                    if res:
                        st.session_state.dados_fipe = res.get("data", res)
                        st.success("Veículo localizado!")
                    else:
                        st.error("Veículo não encontrado na API. Preencha manualmente abaixo.")
                        st.session_state.dados_fipe = {} # Limpa para permitir manual

        with st.form("form_final", clear_on_submit=True):
            f = st.session_state.dados_fipe
            st.subheader("🚗 Informações do Veículo")
            
            marca = st.text_input("Marca", value=f.get("marca", ""))
            modelo = st.text_input("Modelo/Versão", value=f.get("modelo", ""))
            placa_f = st.text_input("Placa", value=f.get("placa", placa_busca))
            
            c1, c2, c3 = st.columns(3)
            ano_f = c1.text_input("Ano Fab.", value=str(f.get("ano_fabricacao", "")))
            ano_m = c2.text_input("Ano Mod.", value=str(f.get("ano_modelo", "")))
            cor = c3.text_input("Cor", value=f.get("cor", ""))
            
            renavam = c1.text_input("Renavam", value=f.get("renavam", ""))
            chassi = c2.text_input("Chassi", value=f.get("chassi", ""))
            comb = c3.text_input("Combustível", value=f.get("combustivel", ""))

            v1, v2 = st.columns(2)
            # Tenta pegar preço da FIPE, se não tiver, fica 0.0
            p_fipe = f.get("preco_fipe", 0.0)
            try: p_val = float(str(p_fipe).replace("R$", "").replace(".", "").replace(",", ".").strip())
            except: p_val = 0.0
            
            preco = v1.number_input("Preço de Venda (R$)", value=p_val)
            km = v2.number_input("KM Atual", min_value=0)

            foto_v = st.file_uploader("📷 Foto do Carro (Obrigatório)", type=['jpg','png','jpeg'])

            st.markdown("---")
            st.subheader("👤 Proprietário")
            nome_t = st.text_input("Nome")
            doc_t = st.file_uploader("📂 Documento do Titular", type=['jpg','png','jpeg'])

            if st.form_submit_button("🚀 FINALIZAR E SALVAR"):
                if modelo and placa_f and foto_v:
                    with st.spinner("Enviando dados..."):
                        url_foto = cloudinary.uploader.upload(foto_v)['secure_url']
                        url_doc = cloudinary.uploader.upload(doc_t)['secure_url'] if doc_t else ""
                        
                        try: df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                        except: df = pd.DataFrame()

                        novo = pd.DataFrame([{
                            "marca": marca, "modelo": modelo, "placa": placa_f.upper(),
                            "ano_fab": str(ano_f), "ano_mod": str(ano_m), "renavam": renavam,
                            "chassi": chassi.upper(), "cor": cor, "combustivel": comb,
                            "preco": preco, "km": km, "foto": url_foto,
                            "nome_titular": nome_t, "doc_titular": url_doc
                        }])
                        
                        conn.update(worksheet="Estoque", data=pd.concat([df, novo], ignore_index=True))
                        st.session_state.dados_fipe = {}
                        st.success("Veículo salvo com sucesso!")
                        st.rerun()
                else: st.warning("Por favor, preencha o Modelo, Placa e envie a Foto.")

    elif menu == "📑 Gerenciar Estoque":
        try: df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        except: df = pd.DataFrame()

        if df.empty: st.info("Estoque vazio.")
        else:
            for i, r in df.iterrows():
                st.markdown(f"""
                    <div class="car-card">
                        <img src="{r.get('foto', '')}" style="width:100%; border-radius:10px; height:200px; object-fit:cover;">
                        <h3>{r.get('modelo', 'Sem Modelo')}</h3>
                        <p style="color:#1e7e34; font-size:1.5rem; font-weight:900;">R$ {float(r.get('preco', 0)):,.2f}</p>
                        <p><b>Placa:</b> {r.get('placa', '-')} | <b>Ano:</b> {r.get('ano_fab', '')}/{r.get('ano_mod', '')}</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ Remover {r.get('placa', i)}", key=f"del_{i}"):
                    conn.update(worksheet="Estoque", data=df.drop(i))
                    st.rerun()
