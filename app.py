import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd

# --- 1. CONFIGURAÇÃO DO CLOUDINARY (MEMORIZADO) ---
cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

# Configuração da Página
st.set_page_config(page_title="CRM AMG Multimarcas", page_icon="🚗", layout="wide")

# --- 2. SUPER LAYOUT (CLARO, FONTE GRANDE E OTIMIZADO) ---
st.markdown("""
    <style>
    /* Forçar tema claro e fontes grandes */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa !important;
        color: #1a1a1a !important;
    }
    
    /* Ajuste de fontes gerais */
    html { font-size: 18px !important; }
    
    /* Títulos e textos */
    h1 { font-size: 2.5rem !important; font-weight: 800 !important; color: #000000 !important; }
    h2 { font-size: 1.8rem !important; color: #333333 !important; }
    h3 { font-size: 1.5rem !important; color: #000000 !important; }
    p, label, span { font-size: 1.1rem !important; color: #1a1a1a !important; font-weight: 500 !important; }

    /* Estilo dos Inputs (campos de texto) */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        font-size: 1.1rem !important;
        padding: 12px !important;
        border-radius: 8px !important;
    }

    /* Estilo do Cartão do Carro */
    .car-card { 
        border: 1px solid #dddddd; 
        border-radius: 15px; 
        padding: 15px; 
        margin-bottom: 20px; 
        background-color: #ffffff;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    }
    
    .preco-destaque { 
        color: #1e7e34 !important; 
        font-size: 1.6rem !important; 
        font-weight: 900 !important;
        margin: 5px 0px;
    }

    /* Botão Salvar e Excluir */
    .stButton button {
        width: 100% !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        padding: 10px !important;
        font-size: 1.1rem !important;
    }
    
    /* Ajuste para formulários */
    [data-testid="stForm"] { background-color: #ffffff !important; border-radius: 15px; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXÃO COM GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    conexao_ok = True
except Exception as e:
    conexao_ok = False
    erro_conexao = e

# --- 4. SISTEMA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.markdown("<h1 style='text-align: center; margin-top: 40px;'>🚗 AMG Multimarcas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Painel de Gestão de Estoque</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if u == "amgmultimarcas" and p == "amg0031":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Dados incorretos.")
else:
    # Barra Lateral Otimizada
    st.sidebar.markdown("### ⚙️ Menu AMG")
    menu = st.sidebar.radio("Escolha uma opção:", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Novo Cadastro")
        with st.form("form_cadastro", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                marca = st.selectbox("Marca", ["Nissan", "Ford", "Chevrolet", "VW", "Fiat", "Toyota", "Honda", "Mitsubishi", "Renault", "Hyundai", "Jeep", "BMW", "Mercedes", "Outra"])
                modelo = st.text_input("Modelo e Versão")
                ano = st.text_input("Ano (ex: 2018/2019)")
            with c2:
                preco = st.number_input("Preço (R$)", min_value=0.0, step=1000.0)
                km = st.number_input("Quilometragem (KM)", min_value=0)
            
            foto_arquivo = st.file_uploader("📷 Carregar Foto do Veículo", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("🚀 PUBLICAR NO ESTOQUE"):
                if modelo and foto_arquivo:
                    with st.spinner('Processando imagem e salvando dados...'):
                        try:
                            # Upload Cloudinary
                            res = cloudinary.uploader.upload(foto_arquivo)
                            url_foto = res['secure_url']
                            
                            # Atualizar Planilha
                            df_atual = conn.read(ttl=0).dropna(how='all')
                            novo_veiculo = pd.DataFrame([{
                                "marca": marca, "modelo": modelo, "ano": ano,
                                "preco": preco, "km": km, "foto": url_foto
                            }])
                            df_final = pd.concat([df_atual, novo_veiculo], ignore_index=True)
                            conn.update(data=df_final)
                            
                            st.success(f"Veículo {modelo} cadastrado com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")
                else:
                    st.warning("Preencha todos os campos e adicione uma foto.")

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read(ttl=0).dropna(how='all')
            
            if df.empty:
                st.info("Nenhum veículo em estoque.")
            else:
                st.markdown(f"## 🚘 Veículos em Estoque ({len(df)})")
                
                for index, row in df.iterrows():
                    p_f = f"R$ {row['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    k_f = f"{int(row['km']):,}".replace(",", ".")

                    # Card Estilizado
                    st.markdown(f"""
                        <div class="car-card">
                            <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                                <div style="flex: 1; min-width: 280px;">
                                    <img src="{row['foto']}" style="width: 100%; border-radius: 10px; object-fit: cover; max-height: 280px;">
                                </div>
                                <div style="flex: 1.5; min-width: 250px;">
                                    <h3 style="margin: 0; color: #000;">{row['marca']} {row['modelo']}</h3>
                                    <p class="preco-destaque">{p_f}</p>
                                    <p style="margin: 5px 0;">📅 <b>Ano:</b> {row['ano']}</p>
                                    <p style="margin: 5px 0;">🛣️ <b>KM:</b> {k_f}</p>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🗑️ Excluir {row['modelo']}", key=f"btn_{index}"):
                        df_novo = df.drop(index)
                        conn.update(data=df_novo)
                        st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
