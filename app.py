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

# --- 2. FUNÇÕES DE FORMATAÇÃO (CRUCIAL) ---
def formatar_para_br(valor):
    """Transforma 43900.0 em 43.900,00"""
    try:
        # Remove caracteres indesejados e trata como float
        limpo = re.sub(r'[^\d]', '', str(valor).split('.')[0])
        v = float(limpo)
        return f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "0,00"

def limpar_id(valor):
    """Remove o .0 de Renavam, KM e Chassi"""
    s = str(valor).strip()
    return s.split('.')[0] if '.' in s else s

# --- 3. CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. INTERFACE ---
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
        
        # Busca simples de marcas (FIPE)
        try:
            marcas = requests.get("https://fipe.parallelum.com.br/api/v2/cars/brands").json()
            dict_marcas = {m['name']: m['code'] for m in marcas}
            marca_n = st.selectbox("1. Marca", options=[""] + sorted(list(dict_marcas.keys())))
        except: marca_n = None

        if marca_n:
            modelos = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{dict_marcas[marca_n]}/models").json()
            dict_modelos = {m['name']: m['code'] for m in modelos}
            modelo_n = st.selectbox("2. Modelo", options=[""] + sorted(list(dict_modelos.keys())))

            if modelo_n:
                anos = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{dict_marcas[marca_n]}/models/{dict_modelos[modelo_n]}/years").json()
                dict_anos = {a['name']: a['code'] for a in anos}
                ano_sel = st.selectbox("3. Ano Modelo", options=[""] + list(dict_anos.keys()))

                if ano_sel:
                    dados = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{dict_marcas[marca_n]}/models/{dict_modelos[modelo_n]}/years/{dict_anos[ano_sel]}").json()
                    
                    with st.form("form_cadastro"):
                        c1, c2 = st.columns(2)
                        marca_v = c1.text_input("Marca", value=dados.get('brand'))
                        modelo_v = c1.text_input("Modelo", value=dados.get('model'))
                        placa_v = c1.text_input("Placa").upper()
                        
                        # Preço já formatado no padrão 43.900,00
                        preco_fipe = formatar_para_br(dados.get('price'))
                        preco_v = c2.text_input("Preço de Venda", value=preco_fipe)
                        km_v = c2.text_input("KM Atual", value="0")
                        
                        st.markdown("---")
                        c3, c4 = st.columns(2)
                        ren_v = c3.text_input("Renavam")
                        cha_v = c4.text_input("Chassi").upper()
                        cor_v = c3.text_input("Cor")
                        comb_v = c4.text_input("Combustível", value=dados.get('fuel'))

                        foto_v = st.file_uploader("📷 Foto do Veículo", type=['jpg','jpeg','png'])
                        tit_v = st.text_input("Nome do Titular")
                        doc_v = st.file_uploader("📂 Documento Titular", type=['jpg','jpeg','png'])

                        if st.form_submit_button("🚀 SALVAR VEÍCULO"):
                            if not placa_v: st.error("Placa obrigatória!"); st.stop()
                            
                            with st.spinner("Salvando e processando imagens..."):
                                url_img = cloudinary.uploader.upload(foto_v)['secure_url'] if foto_v else ""
                                url_doc = cloudinary.uploader.upload(doc_v)['secure_url'] if doc_v else ""
                                
                                try: df_atual = conn.read(worksheet="Estoque", ttl=0).astype(str)
                                except: df_atual = pd.DataFrame()

                                novo = pd.DataFrame([{
                                    "marca": marca_v, "modelo": modelo_v, "placa": placa_v,
                                    "renavam": limpar_id(ren_v), "chassi": cha_v.strip(),
                                    "cor": cor_v, "combustivel": comb_v, "preco": preco_v,
                                    "km": limpar_id(km_v), "foto": url_img,
                                    "nome_titular": tit_v, "doc_titular": url_doc,
                                    "ano": ano_sel
                                }])

                                df_final = pd.concat([df_atual, novo], ignore_index=True).astype(str)
                                conn.update(worksheet="Estoque", data=df_final)
                                st.success("✅ Concluído com sucesso!")
                                time.sleep(1); st.rerun()

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all').astype(str)
        except:
            df = pd.DataFrame()

        if df.empty:
            st.info("Estoque vazio.")
        elif "edit_idx" in st.session_state:
            # TELA DE EDIÇÃO
            idx = st.session_state.edit_idx
            item = df.iloc[idx]
            if st.button("⬅️ Voltar"): st.session_state.pop("edit_idx"); st.rerun()
            
            with st.form("edicao"):
                c1, c2 = st.columns(2)
                m_e = c1.text_input("Marca", value=item['marca'])
                mo_e = c1.text_input("Modelo", value=item['modelo'])
                pl_e = c1.text_input("Placa", value=item['placa'])
                # Garante que na edição o preço também esteja formatado
                pr_e = c2.text_input("Preço", value=formatar_para_br(item['preco']))
                km_e = c2.text_input("KM", value=limpar_id(item['km']))
                
                f_e = st.file_uploader("Trocar Foto")
                
                if st.form_submit_button("💾 SALVAR"):
                    if f_e: item['foto'] = cloudinary.uploader.upload(f_e)['secure_url']
                    df.at[idx, 'marca'] = m_e; df.at[idx, 'modelo'] = mo_e
                    df.at[idx, 'placa'] = pl_e; df.at[idx, 'preco'] = pr_e
                    df.at[idx, 'km'] = limpar_id(km_e)
                    
                    conn.update(worksheet="Estoque", data=df.astype(str))
                    st.success("Atualizado!"); st.session_state.pop("edit_idx"); time.sleep(1); st.rerun()
        else:
            # EXIBIÇÃO DOS CARDS
            for i, r in df.iterrows():
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    
                    # CORREÇÃO DA IMAGEM
                    img = r.get('foto')
                    if img and "http" in str(img):
                        col1.image(img, use_container_width=True)
                    else:
                        col1.warning("Sem Foto")

                    # EXIBIÇÃO DO PREÇO FORMATADO
                    col2.subheader(f"{r['marca']} {r['modelo']}")
                    preco_show = formatar_para_br(r['preco'])
                    col2.markdown(f"### **R$ {preco_show}**")
                    col2.write(f"**Placa:** {r['placa']} | **KM:** {limpar_id(r['km'])}")
                    
                    c_ed, c_ex = col2.columns(2)
                    if c_ed.button(f"✏️ Editar", key=f"ed{i}"):
                        st.session_state.edit_idx = i; st.rerun()
                    if c_ex.button(f"🗑️ Excluir", key=f"del{i}"):
                        conn.update(worksheet="Estoque", data=df.drop(i).astype(str))
                        st.rerun()
                st.markdown("---")
