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

st.set_page_config(page_title="CRM AMG Multimarcas", page_icon="🚗", layout="wide")

# --- 2. FUNÇÃO DE CONSULTA API ---
def consultar_dados_veiculo(placa):
    try:
        placa_limpa = placa.replace("-", "").strip().upper()
        if len(placa_limpa) != 7: return None
        url = f"https://api.fipe.online/v1/veiculos/{placa_limpa}"
        headers = {"Authorization": f"Bearer {API_FIPE_KEY}", "Content-Type": "application/json"}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# --- 3. ESTILO VISUAL (CONTRASTE PARA MOBILE) ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #f0f2f6 !important; color: #000000 !important; }
    [data-testid="stWidgetLabel"] p { font-size: 1.1rem !important; font-weight: 700 !important; color: #000000 !important; }
    
    .stTextInput input, .stNumberInput input {
        border: 2px solid #000000 !important; color: #000000 !important; background-color: #ffffff !important;
    }

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

    .car-card { border: 2px solid #000000; border-radius: 15px; padding: 15px; background-color: #ffffff; margin-bottom: 15px; }
    .preco-destaque { color: #1e7e34 !important; font-size: 1.8rem !important; font-weight: 900 !important; }
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

    # --- ABA: CADASTRAR ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Novo Cadastro")
        
        # Estado para manter os dados da FIPE na tela
        if "dados_fipe" not in st.session_state:
            st.session_state.dados_fipe = {}

        c_p1, c_p2 = st.columns([2, 1])
        placa_busca = c_p1.text_input("Placa para consulta:", placeholder="ABC1D23").upper()
        
        if c_p2.button("🔍 BUSCAR DADOS"):
            if placa_busca:
                with st.spinner("Buscando..."):
                    res = consultar_dados_veiculo(placa_busca)
                    if res:
                        st.session_state.dados_fipe = res.get("data", res)
                        st.success("Dados encontrados!")
                    else: st.error("Veículo não encontrado.")

        with st.form("form_cadastro", clear_on_submit=True):
            f = st.session_state.dados_fipe
            st.subheader("🚗 Dados do Carro")
            
            marca = st.text_input("Marca", value=f.get("marca", ""))
            modelo = st.text_input("Modelo", value=f.get("modelo", ""))
            placa_f = st.text_input("Placa Final", value=f.get("placa", placa_busca))
            
            c1, c2, c3 = st.columns(3)
            with c1:
                ano_f = st.text_input("Ano Fab.", value=str(f.get("ano_fabricacao", "")))
                renavam = st.text_input("Renavam", value=f.get("renavam", ""))
            with c2:
                ano_m = st.text_input("Ano Mod.", value=str(f.get("ano_modelo", "")))
                chassi = st.text_input("Chassi", value=f.get("chassi", ""))
            with c3:
                cor = st.text_input("Cor", value=f.get("cor", ""))
                comb = st.text_input("Combustível", value=f.get("combustivel", ""))

            v1, v2 = st.columns(2)
            with v1:
                p_fipe = f.get("preco_fipe", 0.0)
                try: p_val = float(p_fipe)
                except: p_val = 0.0
                preco = st.number_input("Preço de Venda (R$)", value=p_val)
            with v2:
                km = st.number_input("Quilometragem (KM)", min_value=0)

            foto_v = st.file_uploader("📷 Foto Principal do Veículo", type=['jpg','png','jpeg'])

            st.markdown("---")
            st.subheader("👤 Dados do Titular (Opcional)")
            t1, t2 = st.columns(2)
            nome_t = t1.text_input("Nome do Titular")
            cpf_t = t1.text_input("CPF")
            rg_t = t2.text_input("RG")
            end_t = t2.text_input("Endereço")
            doc_t = st.file_uploader("📂 Foto Documento Titular", type=['jpg','png','jpeg'])

            if st.form_submit_button("🚀 SALVAR NO ESTOQUE"):
                if modelo and placa_f and foto_v:
                    with st.spinner("Salvando..."):
                        # Upload Imagens
                        url_foto = cloudinary.uploader.upload(foto_v)['secure_url']
                        url_doc = cloudinary.uploader.upload(doc_t)['secure_url'] if doc_t else ""
                        
                        # Ler planilha
                        try:
                            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                        except:
                            df = pd.DataFrame()

                        # Novo registro
                        novo = pd.DataFrame([{
                            "marca": marca, "modelo": modelo, "placa": placa_f.upper(),
                            "ano_fab": str(ano_f), "ano_mod": str(ano_m), "renavam": renavam,
                            "chassi": chassi.upper(), "cor": cor, "combustivel": comb,
                            "preco": preco, "km": km, "foto": url_foto,
                            "nome_titular": nome_t, "cpf_titular": cpf_t, "rg_titular": rg_t,
                            "endereco_titular": end_t, "doc_titular": url_doc
                        }])
                        
                        conn.update(worksheet="Estoque", data=pd.concat([df, novo], ignore_index=True))
                        st.session_state.dados_fipe = {} # Limpa busca
                        st.success("Cadastrado com sucesso!")
                        st.rerun()
                else: st.warning("Preencha ao menos Modelo, Placa e Foto do Carro.")

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        except:
            df = pd.DataFrame()

        if df.empty:
            st.info("Nenhum veículo em estoque.")
        else:
            for i, r in df.iterrows():
                st.markdown(f"""
                    <div class="car-card">
                        <img src="{r.get('foto', '')}" style="width:100%; border-radius:10px; height:200px; object-fit:cover;">
                        <h3>{r.get('modelo', 'Sem Modelo')}</h3>
                        <p class="preco-destaque">R$ {float(r.get('preco', 0)):,.2f}</p>
                        <p><b>Placa:</b> {r.get('placa', '-')} | <b>KM:</b> {r.get('km', 0)}</p>
                        <p><b>Ano:</b> {r.get('ano_fab', '')}/{r.get('ano_mod', '')} | <b>Cor:</b> {r.get('cor', '')}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🗑️ Excluir {r.get('placa', i)}", key=f"del_{i}"):
                    conn.update(worksheet="Estoque", data=df.drop(i))
                    st.rerun()
                st.markdown("---")
