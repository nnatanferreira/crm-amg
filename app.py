import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests

# --- 1. CONFIGURAÇÕES ---
API_FIPE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI0ZDk3YTE4NC1kOGIzLTQwOTEtOWVhOC1kNWQ0ZGUzYWZiNWQiLCJlbWFpbCI6Im5uYXRhbmZlcnJlaXJhQGdtYWlsLmNvbSIsImlhdCI6MTc3NjIwMTM4NH0.v_0pe0vEEuLCIMenEsLWZXSl_hdkXVq4oTzfhT4kdXM"

cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

st.set_page_config(page_title="CRM AMG", page_icon="🚗", layout="wide")

# --- 2. FUNÇÃO DE CONSULTA API ---
def consultar_dados_veiculo(placa):
    try:
        placa_limpa = placa.replace("-", "").strip().upper()
        url = f"https://api.fipe.online/v1/veiculos/{placa_limpa}"
        headers = {"Authorization": f"Bearer {API_FIPE_KEY}", "Content-Type": "application/json"}
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# --- 3. ESTILO VISUAL (OTIMIZADO MOBILE) ---
st.markdown("""
    <style>
    /* Fundo e Texto Geral */
    html, body, [data-testid="stAppViewContainer"] { background-color: #f0f2f6 !important; color: #000000 !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #ddd; }
    [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 600 !important; }

    /* Inputs e Labels */
    [data-testid="stWidgetLabel"] p { font-size: 1.1rem !important; font-weight: 700 !important; color: #000000 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 1.1rem !important; height: 50px !important; border: 2px solid #000000 !important; 
        background-color: #ffffff !important; color: #000000 !important;
    }

    /* Botões */
    .stButton button {
        font-size: 1.2rem !important; font-weight: 800 !important; height: 60px !important;
        background-color: #1e7e34 !important; color: #ffffff !important; border-radius: 10px !important;
        border: none !important; width: 100% !important;
    }

    /* Cards Estoque */
    .car-card { 
        border: 2px solid #000000; border-radius: 15px; padding: 15px; 
        background-color: #ffffff; margin-bottom: 15px;
    }
    .preco-destaque { color: #1e7e34 !important; font-size: 1.6rem !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CONEXÃO E LOGIN ---
conn = st.connection("gsheets", type=GSheetsConnection)

if "autenticado" not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: black;'>🚗 AMG Multimarcas</h1>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR"):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
            else: st.error("Dados incorretos.")
else:
    menu = st.sidebar.radio("Menu:", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("<h2 style='color:black;'>📝 Cadastro de Veículo</h2>", unsafe_allow_html=True)
        
        c_busca1, c_busca2 = st.columns([2, 1])
        placa_in = c_busca1.text_input("Placa p/ Busca:", placeholder="ABC1D23").upper()
        
        if "dados_fipe" not in st.session_state: st.session_state.dados_fipe = {}

        if c_busca2.button("🔍 BUSCAR"):
            if placa_in:
                with st.spinner("Buscando..."):
                    res = consultar_dados_veiculo(placa_in)
                    if res:
                        st.session_state.dados_fipe = res.get("data", res)
                        st.success("Puxou!")
                    else: st.error("Não encontrado.")

        with st.form("form_veiculo", clear_on_submit=True):
            f = st.session_state.dados_fipe
            st.subheader("Informações do Carro")
            
            marca = st.text_input("Marca", value=f.get("marca", ""))
            modelo = st.text_input("Modelo/Versão", value=f.get("modelo", ""))
            placa = st.text_input("Placa Final", value=f.get("placa", placa_in))
            
            c1, c2 = st.columns(2)
            with c1:
                ano_fab = st.text_input("Ano Fab.", value=str(f.get("ano_fabricacao", "")))
                renavam = st.text_input("Renavam", value=f.get("renavam", ""))
                cor = st.text_input("Cor", value=f.get("cor", ""))
            with c2:
                ano_mod = st.text_input("Ano Mod.", value=str(f.get("ano_modelo", "")))
                chassi = st.text_input("Chassi", value=f.get("chassi", ""))
                comb = st.text_input("Combustível", value=f.get("combustivel", ""))

            preco_sug = f.get("preco_fipe", 0.0)
            try: p_val = float(preco_sug)
            except: p_val = 0.0
            
            preco = st.number_input("Preço de Venda (R$)", value=p_val)
            km = st.number_input("Quilometragem", min_value=0)
            foto_v = st.file_uploader("📷 Foto do Carro", type=['jpg','png'])

            st.markdown("---")
            st.subheader("Proprietário (Opcional)")
            nome_t = st.text_input("Nome Titular")
            cpf_t = st.text_input("CPF")
            rg_t = st.text_input("RG")
            end_t = st.text_input("Endereço")
            doc_t = st.file_uploader("📂 Foto Documento Titular", type=['jpg','png'])

            if st.form_submit_button("🚀 SALVAR NO ESTOQUE"):
                if modelo and placa and foto_v:
                    with st.spinner('Salvando...'):
                        img_car = cloudinary.uploader.upload(foto_v)
                        img_doc = ""
                        if doc_t:
                            img_doc = cloudinary.uploader.upload(doc_t)['secure_url']
                        
                        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                        novo = pd.DataFrame([{
                            "marca": marca, "modelo": modelo, "placa": placa.upper(),
                            "ano_fab": str(ano_fab), "ano_mod": str(ano_mod),
                            "renavam": renavam, "chassi": chassi.upper(),
                            "cor": cor, "combustivel": comb, "preco": preco, "km": km,
                            "foto": img_car['secure_url'], "nome_titular": nome_t,
                            "cpf_titular": cpf_t, "rg_titular": rg_t,
                            "endereco_titular": end_t, "doc_titular": img_doc
                        }])
                        conn.update(worksheet="Estoque", data=pd.concat([df, novo], ignore_index=True))
                        st.session_state.dados_fipe = {}
                        st.success("Cadastrado!")
                        st.rerun()
                else: st.warning("Modelo, Placa e Foto são obrigatórios.")

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        if df.empty: st.info("Vazio.")
        else:
            for i, r in df.iterrows():
                st.markdown(f"""
                    <div class="car-card">
                        <img src="{r['foto']}" style="width:100%; border-radius:10px; height:220px; object-fit:cover;">
                        <h3 style='color:black;'>{r['modelo']}</h3>
                        <p class="preco-destaque">R$ {r['preco']:,.2f}</p>
                        <p style='color:black;'><b>Placa:</b> {r['placa']} | <b>Ano:</b> {str(r['ano_fab']).replace('.0','')}/{str(r['ano_mod']).replace('.0','')}</p>
                        {f"<p style='color:black;'><b>Titular:</b> {r['nome_titular']}</p>" if r['nome_titular'] else ""}
                    </div>
                """, unsafe_allow_html=True)
                
                if 'doc_titular' in r and r['doc_titular']:
                    st.link_button("📂 Ver Documento", r['doc_titular'], use_container_width=True)
                
                if st.button(f"🗑️ Excluir {r['placa']}", key=f"del_{i}"):
                    conn.update(worksheet="Estoque", data=df.drop(i))
                    st.rerun()
                st.markdown("---")
