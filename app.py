import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests
import time
import re

# --- 1. CONFIGURAÇÕES CLOUDINARY ---
cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

st.set_page_config(page_title="CRM AMG Multimarcas", page_icon="🚗", layout="wide")

# --- 2. FUNÇÕES AUXILIARES ---
def formatar_moeda(valor):
    """Formata para 43.900,00"""
    if not valor or str(valor).lower() in ["nan", "none", ""]: return "0,00"
    try:
        # Remove tudo que não é dígito
        limpo = re.sub(r'\D', '', str(valor))
        # Se o valor vier com centavos (ex: 4390000), divide por 100
        # Mas como a FIPE vem em formato inteiro, vamos tratar o valor bruto
        v = float(limpo) / 100 if len(limpo) > 2 else float(limpo)
        return f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return str(valor)

def limpar_numero(valor):
    """Remove o .0 indesejado e espaços"""
    s = str(valor).strip().split('.')[0]
    if s.lower() in ["nan", "none", ""]: return ""
    return s

# --- 3. CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. LOGIN ---
if "autenticado" not in st.session_state:
    st.markdown("<h1 style='text-align: center;'>🚗 CRM AMG</h1>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ENTRAR"):
            if u == "amgmultimarcas" and p == "amg0031":
                st.session_state["autenticado"] = True
                st.rerun()
            else: st.error("Acesso negado")
else:
    menu = st.sidebar.radio("Navegação", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque"])
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Novo Cadastro")
        
        # API FIPE Simplificada para o Form
        BASE_URL = "https://fipe.parallelum.com.br/api/v2/cars"
        
        @st.cache_data(ttl=3600)
        def carregar_marcas():
            return requests.get(f"{BASE_URL}/brands").json()

        marcas = carregar_marcas()
        dict_marcas = {m['name']: m['code'] for m in marcas}
        marca_n = st.selectbox("1. Marca", options=[""] + sorted(list(dict_marcas.keys())))

        if marca_n:
            modelos = requests.get(f"{BASE_URL}/brands/{dict_marcas[marca_n]}/models").json()
            dict_modelos = {m['name']: m['code'] for m in modelos}
            modelo_n = st.selectbox("2. Modelo", options=[""] + sorted(list(dict_modelos.keys())))

            if modelo_n:
                anos = requests.get(f"{BASE_URL}/brands/{dict_marcas[marca_n]}/models/{dict_modelos[modelo_n]}/years").json()
                dict_anos = {a['name']: a['code'] for a in anos}
                ano_sel = st.selectbox("3. Ano Modelo", options=[""] + list(dict_anos.keys()))

                if ano_sel:
                    dados = requests.get(f"{BASE_URL}/brands/{dict_marcas[marca_n]}/models/{dict_modelos[modelo_n]}/years/{dict_anos[ano_sel]}").json()
                    
                    with st.form("form_cadastro"):
                        c1, c2 = st.columns(2)
                        marca_v = c1.text_input("Marca", value=dados.get('brand'))
                        modelo_v = c1.text_input("Modelo", value=dados.get('model'))
                        placa_v = c1.text_input("Placa").upper()
                        cor_v = c2.text_input("Cor")
                        comb_v = c2.text_input("Combustível", value=dados.get('fuel'))
                        
                        st.markdown("---")
                        c3, c4 = st.columns(2)
                        ren_v = c3.text_input("Renavam")
                        cha_v = c4.text_input("Chassi").upper()
                        pre_v = c3.text_input("Preço de Venda", value=dados.get('price'))
                        km_v = c4.text_input("KM Atual", value="0")
                        
                        f_v = st.file_uploader("📷 Foto do Veículo", type=['jpg','jpeg','png'])
                        tit_v = st.text_input("Nome do Titular")
                        doc_v = st.file_uploader("📂 Documento Titular", type=['jpg','jpeg','png'])

                        if st.form_submit_button("🚀 SALVAR VEÍCULO"):
                            if not placa_v:
                                st.error("A placa é obrigatória!")
                            else:
                                with st.spinner("Enviando dados..."):
                                    # Upload Cloudinary
                                    img_url = cloudinary.uploader.upload(f_v)['secure_url'] if f_v else ""
                                    doc_url = cloudinary.uploader.upload(doc_v)['secure_url'] if doc_v else ""
                                    
                                    try:
                                        df_atual = conn.read(worksheet="Estoque", ttl=0).astype(str)
                                    except:
                                        df_atual = pd.DataFrame()

                                    novo_carro = pd.DataFrame([{
                                        "marca": marca_v, "modelo": modelo_v, "placa": placa_v,
                                        "renavam": limpar_numero(ren_v), "chassi": cha_v.strip(),
                                        "cor": cor_v, "combustivel": comb_v, "preco": pre_v,
                                        "km": limpar_numero(km_v), "foto": img_url,
                                        "nome_titular": tit_v, "doc_titular": doc_url,
                                        "ano_fab": ano_sel.split(" ")[0] # Simplificando ano
                                    }])

                                    df_final = pd.concat([df_atual, novo_carro], ignore_index=True).astype(str)
                                    conn.update(worksheet="Estoque", data=df_final)
                                    st.success("✅ Veículo salvo com sucesso!")
                                    time.sleep(1)
                                    st.rerun()

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all').astype(str)
        except:
            df = pd.DataFrame()

        if df.empty:
            st.warning("Estoque vazio.")
        elif "edit_idx" in st.session_state:
            # Lógica de Edição (Idêntica ao Cadastro)
            idx = st.session_state.edit_idx
            item = df.iloc[idx]
            st.button("⬅️ Voltar", on_click=lambda: st.session_state.pop("edit_idx"))
            
            with st.form("edicao_form"):
                st.subheader(f"Editando {item['placa']}")
                c1, c2 = st.columns(2)
                m_e = c1.text_input("Marca", value=item['marca'])
                mo_e = c1.text_input("Modelo", value=item['modelo'])
                pl_e = c1.text_input("Placa", value=item['placa'])
                pre_e = c2.text_input("Preço", value=item['preco'])
                km_e = c2.text_input("KM", value=item['km'])
                
                f_e = st.file_uploader("Trocar Foto", type=['jpg','png','jpeg'])
                
                if st.form_submit_button("💾 SALVAR ALTERAÇÕES"):
                    if f_e:
                        item['foto'] = cloudinary.uploader.upload(f_e)['secure_url']
                    
                    df.at[idx, 'marca'] = m_e
                    df.at[idx, 'modelo'] = mo_e
                    df.at[idx, 'placa'] = pl_e
                    df.at[idx, 'preco'] = pre_e
                    df.at[idx, 'km'] = limpar_numero(km_e)
                    
                    conn.update(worksheet="Estoque", data=df.astype(str))
                    st.success("Atualizado!")
                    st.session_state.pop("edit_idx")
                    st.rerun()
        else:
            # Lista de Cards
            for i, r in df.iterrows():
                with st.container():
                    col_img, col_txt = st.columns([1, 2])
                    
                    foto_url = r.get('foto')
                    if foto_url and str(foto_url) != "nan":
                        col_img.image(foto_url, use_container_width=True)
                    else:
                        col_img.info("Sem foto")
                        
                    col_txt.subheader(f"{r['marca']} {r['modelo']}")
                    col_txt.write(f"**Preço:** {r['preco']} | **Placa:** {r['placa']}")
                    col_txt.write(f"**KM:** {limpar_numero(r['km'])} | **Cor:** {r['cor']}")
                    
                    b1, b2 = col_txt.columns(2)
                    if b1.button(f"✏️ Editar", key=f"ed_{i}"):
                        st.session_state.edit_idx = i
                        st.rerun()
                    if b2.button(f"🗑️ Excluir", key=f"del_{i}"):
                        new_df = df.drop(i)
                        conn.update(worksheet="Estoque", data=new_df.astype(str))
                        st.rerun()
                st.markdown("---")
