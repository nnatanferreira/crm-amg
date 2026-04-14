import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests

# --- 1. CONFIGURAÇÕES (API FIPE & CLOUDINARY) ---
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
        # Verificação simples para não consultar placas inválidas
        if len(placa_limpa) != 7: return None
        
        url = f"https://api.fipe.online/v1/veiculos/{placa_limpa}"
        headers = {"Authorization": f"Bearer {API_FIPE_KEY}", "Content-Type": "application/json"}
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# --- 3. ESTILO VISUAL CORRIGIDO (Visibilidade de Uploads) ---
st.markdown("""
    <style>
    /* 1. Cores Gerais e Fundo */
    html, body, [data-testid="stAppViewContainer"] { 
        background-color: #f0f2f6 !important; 
        color: #000000 !important; 
    }
    
    /* 2. Sidebar e Rádios */
    [data-testid="stSidebar"] { 
        background-color: #ffffff !important; 
        border-right: 1px solid #ddd; 
    }
    [data-testid="stSidebar"] * { 
        color: #000000 !important; 
        font-weight: 600 !important; 
    }

    /* 3. Títulos */
    h1 { color: #000000 !important; font-weight: 800 !important; }
    h2 { color: #1e7e34 !important; font-weight: 700 !important; }
    h3 { color: #000000 !important; font-weight: 600 !important; }

    /* 4. Labels dos Campos (Nomes acima dos inputs) */
    [data-testid="stWidgetLabel"] p { 
        font-size: 1.1rem !important; 
        font-weight: 700 !important; 
        color: #000000 !important; 
    }

    /* 5. Campos de Entrada (Inputs normais) */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 1.1rem !important; 
        height: 50px !important; 
        border: 2px solid #000000 !important; 
        background-color: #ffffff !important; 
        color: #000000 !important;
    }

    /* 6. CORREÇÃO ESPECÍFICA: Botões de Upload (File Uploader) */
    [data-testid="stFileUploader"] {
        border: 2px dashed #000000 !important; /* Borda tracejada preta visível */
        padding: 10px !important;
        background-color: #ffffff !important;
        border-radius: 10px !important;
    }
    
    /* Garante que o texto "Browse files" ou o nome do arquivo fiquem visíveis */
    [data-testid="stFileUploader"] button {
        background-color: #ffffff !important;
        border: 1px solid #000000 !important;
        color: #000000 !important;
        height: 40px !important;
        width: auto !important;
        font-size: 1rem !important;
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] * {
        color: #333333 !important; /* Texto de ajuda (Arraste arquivos) visível */
    }

    /* 7. Botões Principais (Verdes) */
    .stButton button {
        font-size: 1.2rem !important; 
        font-weight: 800 !important; 
        height: 60px !important;
        background-color: #1e7e34 !important; 
        color: #ffffff !important; 
        border-radius: 10px !important;
        border: none !important; 
        width: 100% !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1) !important;
    }
    .stButton button:active { background-color: #1a6e2d !important; }

    /* 8. Cards Estoque */
    .car-card { 
        border: 2px solid #000000; 
        border-radius: 15px; 
        padding: 15px; 
        background-color: #ffffff; 
        margin-bottom: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05) !important;
    }
    .preco-destaque { 
        color: #1e7e34 !important; 
        font-size: 1.6rem !important; 
        font-weight: 900 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CONEXÃO E LOGIN ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erro ao conectar com a planilha. Verifique as credenciais.")

if "autenticado" not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: black;'>🚗 AMG Multimarcas</h1>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR SISTEMA", use_container_width=True):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
            else: st.error("Dados de acesso incorretos.")
else:
    menu = st.sidebar.radio("Navegar:", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    st.sidebar.markdown("---")
    if st.sidebar.button("Portas Fechadas (Sair)", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("<h2 style='color:black;'>📝 Cadastro de Veículo</h2>", unsafe_allow_html=True)
        
        c_busca1, c_busca2 = st.columns([2, 1])
        placa_in = c_busca1.text_input("🔍 Placa para Busca Automática:", placeholder="ABC1D23").upper()
        
        if "dados_fipe" not in st.session_state: st.session_state.dados_fipe = {}

        if c_busca2.button("🔍 PUXAR DADOS", use_container_width=True):
            if placa_in:
                with st.spinner("Consultando base da FIPE..."):
                    res = consultar_dados_veiculo(placa_in)
                    if res:
                        st.session_state.dados_fipe = res.get("data", res)
                        st.success("Dados preenchidos!")
                    else: st.error("Não encontrado ou erro na API.")
            else: st.warning("Digite uma placa primeiro.")

        with st.form("form_veiculo", clear_on_submit=True):
            f = st.session_state.dados_fipe
            st.subheader("Informações do Carro")
            
            marca = st.text_input("Marca", value=f.get("marca", ""))
            modelo = st.text_input("Modelo e Versão", value=f.get("modelo", ""))
            placa = st.text_input("Placa Final", value=f.get("placa", placa_in))
            
            c1, c2 = st.columns(2)
            with c1:
                ano_fab = st.text_input("Ano Fabricação", value=str(f.get("ano_fabricacao", "")))
                renavam = st.text_input("Renavam", value=f.get("renavam", ""))
                cor = st.text_input("Cor (do documento)", value=f.get("cor", ""))
            with c2:
                ano_mod = st.text_input("Ano Modelo", value=str(f.get("ano_modelo", "")))
                chassi = st.text_input("Chassi", value=f.get("chassi", ""))
                comb = st.text_input("Combustível", value=f.get("combustivel", ""))

            # Valor e KM
            preco_sug = f.get("preco_fipe", 0.0)
            try: p_val = float(preco_sug)
            except: p_val = 0.0
            
            v1, v2 = st.columns(2)
            with v1:
                preco = st.number_input("Preço de Venda (R$)", value=p_val, step=500.0)
            with v2:
                km = st.number_input("Quilometragem Atual", min_value=0)
            
            st.markdown("---")
            foto_v = st.file_uploader("📷 Foto Principal do Carro", type=['jpg','png','jpeg'])

            st.markdown("---")
            st.subheader("👤 Proprietário / Titular (Opcional)")
            nome_t = st.text_input("Nome Completo Titular")
            cpf_t = st.text_input("CPF do Titular")
            rg_t = st.text_input("RG do Titular")
            end_t = st.text_input("Endereço Completo")
            doc_t = st.file_uploader("📂 Foto Documento do Titular", type=['jpg','png','jpeg'])

            if st.form_submit_button("🚀 SALVAR NO ESTOQUE AMG", use_container_width=True):
                if modelo and placa and foto_v:
                    with st.spinner('Salvando no banco de dados...'):
                        # Upload Foto Carro
                        img_car = cloudinary.uploader.upload(foto_v)
                        # Upload Doc Titular
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
                        st.session_state.dados_fipe = {} # Limpa após salvar
                        st.success("Veículo Cadastrado!")
                        st.rerun()
                else: st.warning("Obrigatório: Modelo, Placa e Foto do Carro.")

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        if df.empty: st.info("O estoque está vazio.")
        else:
            for i, r in df.iterrows():
                # Formatação dos anos e quilometragem
                anos_formatado = f"{str(r['ano_fab']).replace('.0','')}/{str(r['ano_mod']).replace('.0','')}"
                km_formatado = f"{int(r['km']):,}"
                
                st.markdown(f"""
                    <div class="car-card">
                        <img src="{r['foto']}" style="width:100%; border-radius:10px; height:220px; object-fit:cover; border:1px solid #ddd;">
                        <h3 style='color:black; margin: 10px 0px 5px 0px;'>{r['modelo']}</h3>
                        <p class="preco-destaque">R$ {r['preco']:,.2f}</p>
                        <p style='color:black; font-size: 1rem;'>
                            <b>💳 Placa:</b> {r['placa']} | <b>📅 Ano:</b> {anos_formatado} | <b>🛣️ KM:</b> {km_formatado}<br>
                            {"<b>👤 Titular:</b> " + str(r['nome_titular']) if r['nome_titular'] else ""}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Se houver documento do titular, mostra o botão
                if 'doc_titular' in r and r['doc_titular']:
                    st.link_button("📂 Ver Documento do Dono", r['doc_titular'], use_container_width=True)
                
                # Botão Excluir
                if st.button(f"🗑️ Excluir {r['placa']}", key=f"del_{i}", use_container_width=True):
                    conn.update(worksheet="Estoque", data=df.drop(i))
                    st.rerun()
                st.markdown("---")
