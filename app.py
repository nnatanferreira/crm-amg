import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd

# --- 1. CONFIGURAÇÃO DO CLOUDINARY ---
# Preencha com seus dados do painel do Cloudinary
cloudinary.config( 
  cloud_name = "dybos073qE", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

# Configuração visual da página
st.set_page_config(page_title="CRM AMG Multimarcas", page_icon="🚗", layout="wide")

# --- 2. ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2, h3, p, label { color: #1a1a1a !important; }
    .car-card { 
        border: 1px solid #eee; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 20px; 
        background-color: #fdfdfd;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.02);
    }
    .preco-destaque { color: #28a745 !important; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXÃO COM GOOGLE SHEETS ---
try:
    # Conexão usa as credenciais que você colou nos SECRETS do Streamlit
    conn = st.connection("gsheets", type=GSheetsConnection)
    conexao_ok = True
except Exception as e:
    conexao_ok = False
    erro_conexao = e

# --- 4. SISTEMA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.markdown("<h2 style='text-align: center; padding-top: 50px;'>Painel Administrativo AMG</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")
else:
    # Cabeçalho após Login
    st.markdown("<h1 style='text-align: center;'>AMG MULTIMARCAS</h1>", unsafe_allow_html=True)
    
    if not conexao_ok:
        st.error(f"Erro de conexão com a planilha: {erro_conexao}")
        st.stop()

    menu = st.sidebar.radio("Menu Principal", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])

    # --- ABA: CADASTRAR ---
    if menu == "➕ Cadastrar Veículo":
        st.subheader("📝 Cadastrar Novo Veículo")
        with st.form("form_cadastro", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                marca = st.selectbox("Marca", ["Nissan", "Ford", "Chevrolet", "VW", "Fiat", "Toyota", "Honda", "Mitsubishi", "Outra"])
                modelo = st.text_input("Modelo e Versão")
                ano = st.text_input("Ano (ex: 2013/2014)")
            with c2:
                preco = st.number_input("Preço de Venda (R$)", min_value=0.0, step=500.0)
                km = st.number_input("Quilometragem", min_value=0)
            
            foto_arquivo = st.file_uploader("📷 Selecione a Foto", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("🚀 SALVAR NO ESTOQUE", use_container_width=True):
                if modelo and foto_arquivo:
                    with st.spinner('Enviando foto e salvando dados...'):
                        try:
                            # 1. Upload para Cloudinary
                            res = cloudinary.uploader.upload(foto_arquivo)
                            url_foto = res['secure_url']
                            
                            # 2. Ler dados atuais (ttl=0 para não ter atraso)
                            df_atual = conn.read(ttl=0).dropna(how='all')
                            
                            # 3. Criar nova linha
                            novo_veiculo = pd.DataFrame([{
                                "marca": marca, "modelo": modelo, "ano": ano,
                                "preco": preco, "km": km, "foto": url_foto
                            }])
                            
                            # 4. Concatenar e Atualizar Planilha
                            df_final = pd.concat([df_atual, novo_veiculo], ignore_index=True)
                            conn.update(data=df_final)
                            
                            st.success(f"Sucesso! {modelo} já está no sistema.")
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")
                else:
                    st.warning("Por favor, preencha o modelo e adicione uma foto.")

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            # ttl=0 garante que o carro cadastrado agora apareça agora
            df = conn.read(ttl=0).dropna(how='all')
            
            if df.empty:
                st.info("O estoque está vazio. Use a aba de cadastro!")
            else:
                st.subheader(f"🚘 Veículos em Exposição ({len(df)})")
                
                for index, row in df.iterrows():
                    # Formatação de Moeda Brasileira
                    preco_formatado = f"R$ {row['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    km_formatado = f"{int(row['km']):,}".replace(",", ".")

                    with st.container():
                        st.markdown('<div class="car-card">', unsafe_allow_html=True)
                        col_img, col_txt = st.columns([1, 2])
                        
                        with col_img:
                            st.image(row['foto'], use_container_width=True)
                        
                        with col_txt:
                            st.markdown(f"### {row['marca']} {row['modelo']}")
                            st.markdown(f"<p class='preco-destaque'>{preco_formatado}</p>", unsafe_allow_html=True)
                            st.write(f"📅 **Ano:** {row['ano']} | 🛣️ **KM:** {km_formatado}")
                            
                            # Botão para remover veículo
                            if st.button(f"🗑️ Excluir {row['modelo']}", key=f"btn_{index}"):
                                df_novo = df.drop(index)
                                conn.update(data=df_novo)
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Não foi possível carregar o estoque: {e}")

    # Botão Sair na Barra Lateral
    if st.sidebar.button("Sair do Sistema"):
        st.session_state.clear()
        st.rerun()
