import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd

# --- 1. CONFIGURAÇÕES (PREENCHA AQUI) ---
# Seus dados do Cloudinary:
cloudinary.config( 
  cloud_name = "dybos073qE", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

# O Link da sua Planilha (Já configurado com o seu link)
URL_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/1rM3BqGXbt5sevuy0p1C6K1asj8vumCzHiACreRHnjPE/edit?usp=sharing"

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CRM AMG Multimarcas", page_icon="🚗", layout="wide")

# Conexão direta com a sua Planilha do Google
conn = st.connection("gsheets", type=GSheetsConnection, spreadsheet=URL_DA_PLANILHA)

# CSS para visual limpo
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2, h3, p, label { color: #1a1a1a !important; }
    .car-card { border: 1px solid #eee; border-radius: 12px; padding: 15px; margin-bottom: 20px; background-color: #fff; }
    .preco-destaque { color: #28a745 !important; font-size: 22px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN ---
if "autenticado" not in st.session_state:
    st.markdown("<h2 style='text-align: center; padding-top: 50px;'>CRM AMG Multimarcas</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Acessar Painel", use_container_width=True):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")
else:
    st.markdown("<h1 style='text-align: center;'>AMG MULTIMARCAS</h1>", unsafe_allow_html=True)
    menu = st.sidebar.radio("Navegação", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])

    # --- ABA: CADASTRAR ---
    if menu == "➕ Cadastrar Veículo":
        st.subheader("📝 Novo Cadastro (Permanente)")
        with st.form("cadastro_amg", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                marca = st.selectbox("Marca", ["Nissan", "Ford", "Chevrolet", "VW", "Fiat", "Toyota", "Honda", "Mitsubishi", "Outra"])
                modelo = st.text_input("Modelo e Versão")
                ano = st.text_input("Ano/Modelo")
            with c2:
                preco = st.number_input("Preço de Venda (R$)", min_value=0)
                km = st.number_input("Quilometragem (KM)", min_value=0)
            
            foto_arquivo = st.file_uploader("📷 Foto do Veículo", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("🚀 PUBLICAR NO SISTEMA", use_container_width=True):
                if modelo and foto_arquivo:
                    with st.spinner('Salvando dados e hospedando imagem...'):
                        # 1. Envia foto para o Cloudinary
                        res = cloudinary.uploader.upload(foto_arquivo)
                        url_foto = res['secure_url']
                        
                        # 2. Busca o que já existe na planilha
                        df_existente = conn.read()
                        
                        # 3. Cria a nova linha
                        novo_item = pd.DataFrame([{
                            "marca": marca, "modelo": modelo, "ano": ano,
                            "preco": preco, "km": km, "foto": url_foto
                        }])
                        
                        # 4. Atualiza a planilha
                        df_atualizado = pd.concat([df_existente, novo_item], ignore_index=True)
                        conn.update(data=df_atualizado)
                        
                        st.success(f"Veículo {modelo} salvo com sucesso!")
                else:
                    st.warning("Preencha o modelo e anexe uma foto.")

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read()
            st.subheader(f"🚘 Veículos no Pátio ({len(df)})")
            
            for index, row in df.iterrows():
                # Formatação de valores
                p_f = f"R$ {row['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                k_f = f"{row['km']:,}".replace(",", ".")

                with st.container():
                    st.markdown('<div class="car-card">', unsafe_allow_html=True)
                    col_img, col_txt = st.columns([1, 1.8])
                    with col_img:
                        st.image(row['foto'], use_container_width=True)
                    with col_txt:
                        st.markdown(f"### {row['marca']} {row['modelo']}")
                        st.markdown(f"<p class='preco-destaque'>{p_f}</p>", unsafe_allow_html=True)
                        st.write(f"📅 Ano: {row['ano']} | 🛣️ KM: {k_f}")
                        
                        if st.button(f"Remover item {index}", key=f"del_{index}"):
                            df_novo = df.drop(index)
                            conn.update(data=df_novo)
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        except:
            st.info("O estoque está vazio ou a planilha está a ser configurada.")

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()
