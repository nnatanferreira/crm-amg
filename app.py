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

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #f0f2f6 !important; color: #000000 !important; }
    button, .stButton>button, div.stFormSubmitButton>button {
        background-color: #1e7e34 !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        border-radius: 10px !important;
        height: 55px !important;
        width: 100% !important;
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
        if st.form_submit_button("ENTRAR"):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
            else: st.error("Erro.")
else:
    menu = st.sidebar.radio("Menu", ["➕ Cadastrar", "📑 Estoque"])
    
    # --- FUNÇÃO PARA LER PLANILHA COM SEGURANÇA ---
    def carregar_dados():
        try:
            # Tenta ler a aba Estoque
            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
            # Se a planilha existir mas não tiver a coluna 'placa', força a criação
            if "placa" not in df.columns:
                return pd.DataFrame(columns=["marca","modelo","placa","ano_fab","ano_mod","renavam","chassi","cor","combustivel","preco","km","foto","nome_titular","doc_titular"])
            return df
        except:
            # Se a aba nem existir ou der erro de conexão
            return pd.DataFrame(columns=["marca","modelo","placa","ano_fab","ano_mod","renavam","chassi","cor","combustivel","preco","km","foto","nome_titular","doc_titular"])

    if menu == "➕ Cadastrar":
        st.subheader("📝 Novo Veículo")
        placa_busca = st.text_input("Placa:").upper()
        
        if "f" not in st.session_state: st.session_state.f = {}

        if st.button("🔍 BUSCAR DADOS"):
            if placa_busca:
                res = consultar_dados_veiculo(placa_busca)
                if res:
                    st.session_state.f = res.get("data", res)
                    st.success("Dados preenchidos!")

        with st.form("f_car", clear_on_submit=True):
            d = st.session_state.f
            marca = st.text_input("marca", value=d.get("marca", ""))
            modelo = st.text_input("modelo", value=d.get("modelo", ""))
            placa = st.text_input("placa", value=d.get("placa", placa_busca))
            af = st.text_input("ano_fab", value=str(d.get("ano_fabricacao", "")))
            am = st.text_input("ano_mod", value=str(d.get("ano_modelo", "")))
            ren = st.text_input("renavam", value=d.get("renavam", ""))
            cha = st.text_input("chassi", value=d.get("chassi", ""))
            cor = st.text_input("cor", value=d.get("cor", ""))
            com = st.text_input("combustivel", value=d.get("combustivel", ""))
            km = st.number_input("km", min_value=0)
            pre = st.number_input("preco", value=float(d.get("preco_fipe", 0.0)))
            
            f_car = st.file_uploader("Foto Carro", type=['jpg','jpeg','png'])
            
            if st.form_submit_button("🚀 SALVAR NO ESTOQUE"):
                if modelo and placa and f_car:
                    with st.spinner("Salvando..."):
                        url_img = cloudinary.uploader.upload(f_car)['secure_url']
                        df_atual = carregar_dados()
                        
                        novo = pd.DataFrame([{
                            "marca": marca, "modelo": modelo, "placa": placa.upper(),
                            "ano_fab": af, "ano_mod": am, "renavam": ren, "chassi": cha,
                            "cor": cor, "combustivel": com, "preco": pre, "km": km,
                            "foto": url_img
                        }])
                        
                        # Concatena o novo dado com o que já existe (ou com as colunas vazias)
                        df_final = pd.concat([df_atual, novo], ignore_index=True)
                        conn.update(worksheet="Estoque", data=df_final)
                        
                        st.session_state.f = {}
                        st.success("Veículo salvo!")
                        st.rerun()

    elif menu == "📑 Estoque":
        df = carregar_dados()
        if df.empty or "placa" not in df.columns:
            st.info("O estoque está vazio no momento.")
        else:
            for i, r in df.iterrows():
                # .get evita o erro se a coluna estiver faltando por algum motivo
                st.markdown(f"""
                    <div class="car-card">
                        <img src="{r.get('foto', '')}" style="width:100%; height:200px; object-fit:cover; border-radius:10px;">
                        <h3>{r.get('modelo', 'Sem nome')}</h3>
                        <p><b>Placa:</b> {r.get('placa', '-')} | <b>Preço:</b> R$ {r.get('preco', 0)}</p>
                        <p><b>Cor:</b> {r.get('cor', '-')} | <b>KM:</b> {r.get('km', 0)}</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ Excluir {r.get('placa', i)}", key=f"btn_{i}"):
                    conn.update(worksheet="Estoque", data=df.drop(i))
                    st.rerun()
