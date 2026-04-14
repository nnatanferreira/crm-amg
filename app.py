import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd

# --- 1. CONFIGURAÇÃO DO CLOUDINARY ---
cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

# Configuração da Página
st.set_page_config(
    page_title="CRM AMG Multimarcas", 
    page_icon="🚗", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ESTILO VISUAL ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #f8f9fa !important; color: #1a1a1a !important; }
    h1 { font-size: 3.5rem !important; font-weight: 800 !important; }
    h2 { font-size: 2.2rem !important; font-weight: 700 !important; color: #1e7e34 !important; }
    
    [data-testid="stSidebar"] { min-width: 350px !important; background-color: #ffffff !important; border-right: 1px solid #ddd; }
    
    [data-testid="stWidgetLabel"] p { font-size: 1.3rem !important; font-weight: 600 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 1.3rem !important; height: 60px !important; border-radius: 10px !important; border: 2px solid #ccc !important;
    }

    .stButton button {
        font-size: 1.7rem !important; font-weight: 800 !important; height: 75px !important;
        border-radius: 15px !important; background-color: #1e7e34 !important; color: white !important;
    }

    .car-card { 
        border: 2px solid #eee; border-radius: 20px; padding: 25px; 
        background-color: #ffffff; box-shadow: 0px 6px 20px rgba(0,0,0,0.1);
    }
    .preco-destaque { color: #1e7e34 !important; font-size: 2.2rem !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. LOGIN ---
if "autenticado" not in st.session_state:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🚗 AMG Multimarcas</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA", use_container_width=True):
                if u == "amgmultimarcas" and p == "amg0031":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else: st.error("Dados incorretos.")
else:
    menu = st.sidebar.radio("Navegar:", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR VEÍCULO ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Cadastro de Veículo e Titularidade")
        
        with st.form("form_veiculo", clear_on_submit=True):
            
            # SEÇÃO 1: DADOS E DOCUMENTO DO TITULAR
            st.subheader("👤 Proprietário (Conforme CRV)")
            t1, t2 = st.columns(2)
            with t1:
                nome_titular = st.text_input("Nome Completo do Titular")
                cpf_titular = st.text_input("CPF do Titular")
                rg_titular = st.text_input("RG do Titular")
            with t2:
                endereco_titular = st.text_input("Endereço Completo")
                doc_titular_file = st.file_uploader("📂 Foto do Documento do Titular (RG/CNH)", type=['jpg', 'jpeg', 'png'])
            
            st.markdown("---")
            
            # SEÇÃO 2: DADOS TÉCNICOS DO VEÍCULO
            st.subheader("🚗 Dados do Veículo")
            c1, c2, c3 = st.columns([1, 1.5, 1])
            with c1:
                marca = st.selectbox("Marca", ["Nissan", "Ford", "Chevrolet", "VW", "Fiat", "Toyota", "Honda", "Mitsubishi", "Renault", "Hyundai", "Jeep", "BMW", "Mercedes", "Outra"])
            with c2:
                modelo = st.text_input("Modelo e Versão")
            with c3:
                placa = st.text_input("Placa")

            d1, d2, d3 = st.columns(3)
            with d1:
                ano_fab = st.text_input("Ano Fabricação")
                renavam = st.text_input("Renavam")
            with d2:
                ano_mod = st.text_input("Ano Modelo")
                chassi = st.text_input("Chassi")
            with d3:
                cor = st.text_input("Cor")
                combustivel = st.selectbox("Combustível", ["Flex", "Diesel", "Gasolina", "Híbrido", "Elétrico"])

            st.markdown("---")
            
            # SEÇÃO 3: COMERCIAL
            v1, v2 = st.columns(2)
            with v1:
                preco = st.number_input("Preço de Venda (R$)", min_value=0.0, step=500.0)
                km = st.number_input("Quilometragem", min_value=0)
            with v2:
                foto_v_file = st.file_uploader("📷 Foto Principal do Carro", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("🚀 SALVAR CADASTRO NO ESTOQUE", use_container_width=True):
                if modelo and placa and nome_titular and foto_v_file:
                    with st.spinner('Fazendo upload e salvando...'):
                        # Upload da foto do carro
                        res_carro = cloudinary.uploader.upload(foto_v_file)
                        
                        # Upload do documento do titular (se houver)
                        url_doc_titular = ""
                        if doc_titular_file:
                            res_doc = cloudinary.uploader.upload(doc_titular_file)
                            url_doc_titular = res_doc['secure_url']

                        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
                        
                        novo = pd.DataFrame([{
                            "nome_titular": nome_titular,
                            "cpf_titular": cpf_titular,
                            "rg_titular": rg_titular,
                            "endereco_titular": endereco_titular,
                            "doc_titular": url_doc_titular,
                            "marca": marca, "modelo": modelo, "placa": placa.upper(),
                            "ano_fab": str(ano_fab), "ano_mod": str(ano_mod),
                            "renavam": renavam, "chassi": chassi.upper(),
                            "cor": cor, "combustivel": combustivel,
                            "preco": preco, "km": km, "foto": res_carro['secure_url']
                        }])
                        
                        conn.update(worksheet="Estoque", data=pd.concat([df, novo], ignore_index=True))
                        st.success(f"Veículo {modelo} cadastrado com documento do titular!")
                else:
                    st.warning("Preencha Modelo, Placa, Nome do Titular e Foto do Carro.")

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all')
        if df.empty:
            st.info("Estoque vazio.")
        else:
            st.markdown(f"## 🚘 Estoque Atual ({len(df)})")
            cols = st.columns(3)
            for i, r in df.iterrows():
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="car-card">
                            <img src="{r['foto']}" style="width:100%; border-radius:15px; margin-bottom:15px;">
                            <h3>{r['modelo']}</h3>
                            <p class="preco-destaque">R$ {r['preco']:,.2f}</p>
                            <p style='font-size:1.1rem'>
                                <b>Titular:</b> {r['nome_titular']}<br>
                                <b>Placa:</b> {r['placa']}<br>
                                <b>Ano:</b> {str(r['ano_fab']).replace('.0','')}/{str(r['ano_mod']).replace('.0','')}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Botão para ver documento do dono
                    if r['doc_titular']:
                        st.link_button("📂 Ver Documento Titular", r['doc_titular'], use_container_width=True)
                    
                    if st.button(f"🗑️ Excluir", key=f"del_{i}", use_container_width=True):
                        conn.update(worksheet="Estoque", data=df.drop(i))
                        st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)
