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

# --- 2. FUNÇÕES DE APOIO ---
def formatar_para_br(valor):
    """Garante o formato 43.900,00 sem adicionar zeros extras"""
    if not valor or str(valor).lower() in ["nan", "none", ""]: return "0,00"
    try:
        texto = str(valor).replace('R$', '').strip()
        apenas_numeros = re.sub(r'[^\d]', '', texto.split(',')[0].split('.')[0])
        v = float(apenas_numeros)
        return f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return str(valor)

def limpar_id(valor):
    """Remove .0 de campos como Renavam e KM"""
    s = str(valor).strip()
    return s.split('.')[0] if '.' in s else s

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
    menu = st.sidebar.radio("Navegação", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque", "👤 Cadastro de Clientes"])
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR VEÍCULO ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Novo Cadastro de Veículo")
        
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
                        preco_fipe = formatar_para_br(dados.get('price'))
                        preco_v = c2.text_input("Preço", value=preco_fipe)
                        km_v = c2.text_input("Quilometragem", value="0")
                        
                        st.markdown("---")
                        c3, c4 = st.columns(2)
                        ren_v = c3.text_input("Renavam")
                        cha_v = c4.text_input("Chassi").upper()
                        cor_v = c3.text_input("Cor")
                        comb_v = c4.text_input("Combustível", value=dados.get('fuel'))

                        foto_v = st.file_uploader("📷 Foto do Veículo", type=['jpg','jpeg','png'])
                        tit_v = st.text_input("Nome do Titular (Atual)")
                        doc_v = st.file_uploader("📂 Documento do Titular", type=['jpg','jpeg','png'])

                        if st.form_submit_button("🚀 SALVAR NO ESTOQUE"):
                            if not placa_v: st.error("Placa obrigatória!"); st.stop()
                            aviso = st.info("⏳ Salvando dados...")
                            url_img = cloudinary.uploader.upload(foto_v)['secure_url'] if foto_v else ""
                            url_doc = cloudinary.uploader.upload(doc_v)['secure_url'] if doc_v else ""
                            try: df_atual = conn.read(worksheet="Estoque", ttl=0).astype(str)
                            except: df_atual = pd.DataFrame()
                            novo = pd.DataFrame([{"marca": marca_v, "modelo": modelo_v, "placa": placa_v, "renavam": limpar_id(ren_v), "chassi": cha_v.strip(), "cor": cor_v, "combustivel": comb_v, "preco": formatar_para_br(preco_v), "km": limpar_id(km_v), "foto": url_img, "nome_titular": tit_v, "doc_titular": url_doc, "ano": ano_sel}])
                            conn.update(worksheet="Estoque", data=pd.concat([df_atual, novo], ignore_index=True).astype(str))
                            aviso.empty(); st.success("✅ Salvo com sucesso!"); time.sleep(1); st.rerun()

    # --- ABA: GERENCIAR ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all').astype(str)
        except:
            df = pd.DataFrame()

        if df.empty:
            st.info("Estoque vazio.")
        elif "edit_idx" in st.session_state:
            idx = st.session_state.edit_idx
            item = df.iloc[idx]
            st.markdown(f"### ✏️ Editando: {item['placa']}")
            with st.form("form_edicao"):
                c1, c2 = st.columns(2)
                m_e = c1.text_input("Marca", value=item['marca'])
                mo_e = c1.text_input("Modelo", value=item['modelo'])
                pl_e = c1.text_input("Placa", value=item['placa']).upper()
                pr_e = c2.text_input("Preço", value=formatar_para_br(item['preco']))
                km_e = c2.text_input("KM", value=limpar_id(item['km']))
                st.markdown("---")
                c3, c4 = st.columns(2)
                ren_e = c3.text_input("Renavam", value=limpar_id(item.get('renavam','')))
                cha_e = c4.text_input("Chassi", value=item.get('chassi','')).upper()
                cor_e = c3.text_input("Cor", value=item.get('cor',''))
                comb_e = c4.text_input("Combustível", value=item.get('combustivel',''))
                f_v_e = st.file_uploader("Trocar Foto do Veículo")
                tit_e = st.text_input("Nome do Titular", value=item.get('nome_titular',''))
                f_d_e = st.file_uploader("Trocar Documento Titular")
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.form_submit_button("💾 SALVAR ALTERAÇÕES"):
                    aviso_ed = st.info("⏳ Atualizando...")
                    url_v = cloudinary.uploader.upload(f_v_e)['secure_url'] if f_v_e else item['foto']
                    url_d = cloudinary.uploader.upload(f_d_e)['secure_url'] if f_d_e else item.get('doc_titular','')
                    df.at[idx, 'marca'] = m_e; df.at[idx, 'modelo'] = mo_e; df.at[idx, 'placa'] = pl_e; df.at[idx, 'preco'] = formatar_para_br(pr_e)
                    df.at[idx, 'km'] = limpar_id(km_e); df.at[idx, 'renavam'] = limpar_id(ren_e); df.at[idx, 'chassi'] = cha_e; df.at[idx, 'cor'] = cor_e
                    df.at[idx, 'combustivel'] = comb_e; df.at[idx, 'nome_titular'] = tit_e; df.at[idx, 'foto'] = url_v; df.at[idx, 'doc_titular'] = url_d
                    conn.update(worksheet="Estoque", data=df.astype(str))
                    aviso_ed.empty(); st.success("✅ Atualizado!"); del st.session_state.edit_idx; time.sleep(1); st.rerun()
                if col_btn2.form_submit_button("❌ CANCELAR"):
                    del st.session_state.edit_idx; st.rerun()
        else:
            for i, r in df.iterrows():
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    f_url = str(r.get('foto', ''))
                    if f_url and "http" in f_url: col1.image(f_url, use_container_width=True)
                    else: col1.info("Sem foto")
                    col2.subheader(f"{r['marca']} {r['modelo']}")
                    col2.markdown(f"### R$ {formatar_para_br(r['preco'])}")
                    col2.write(f"Placa: {r['placa']} | KM: {limpar_id(r['km'])}")
                    btn_col1, btn_col2 = col2.columns(2)
                    if btn_col1.button(f"✏️ Editar", key=f"e{i}"):
                        st.session_state.edit_idx = i; st.rerun()
                    if btn_col2.button(f"🗑️ Excluir", key=f"d{i}"):
                        df_novo = df.drop(i)
                        conn.update(worksheet="Estoque", data=df_novo.astype(str))
                        st.rerun()
                st.markdown("---")

    # --- ABA: CADASTRO DE CLIENTES (NOVA) ---
    elif menu == "👤 Cadastro de Clientes":
        st.markdown("## 👤 Cadastro de Clientes para Documentos")
        st.write("Preencha os dados abaixo para gerar futuramente Procurações, Arras e ATPV.")
        
        with st.form("form_cliente"):
            st.subheader("🚗 Dados do Veículo Negociado")
            c1, c2, c3 = st.columns(3)
            c_chassi = c1.text_input("Chassi").upper()
            c_placa = c2.text_input("Placa").upper()
            c_cor = c3.text_input("Cor")
            
            st.markdown("---")
            st.subheader("👤 Dados Pessoais do Cliente")
            c_nome = st.text_input("Nome Completo")
            c4, c5 = st.columns(2)
            c_rg = c4.text_input("RG")
            c_cpf = c5.text_input("CPF")
            
            st.markdown("---")
            st.subheader("🏠 Endereço Completo")
            c_rua = st.text_input("Nome da Rua / Logradouro")
            c6, c7 = st.columns([1, 2])
            c_num = c6.text_input("Número")
            c_comp = c7.text_input("Complemento (Apto, Bloco, etc.)")
            c8, c9 = st.columns(2)
            c_cid = c8.text_input("Cidade")
            c_est = c9.selectbox("Estado", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])

            if st.form_submit_button("💾 SALVAR CADASTRO DO CLIENTE"):
                if not c_nome or not c_cpf:
                    st.error("Nome e CPF são obrigatórios!")
                else:
                    aviso_c = st.info("⏳ Gravando dados do cliente...")
                    try:
                        df_clientes = conn.read(worksheet="Clientes", ttl=0).astype(str)
                    except:
                        df_clientes = pd.DataFrame()
                    
                    novo_cliente = pd.DataFrame([{
                        "chassi": c_chassi, "placa": c_placa, "cor": c_cor,
                        "nome": c_nome, "rg": c_rg, "cpf": c_cpf,
                        "rua": c_rua, "numero": c_num, "complemento": c_comp,
                        "cidade": c_cid, "estado": c_est,
                        "data_cadastro": time.strftime("%d/%m/%Y")
                    }])
                    
                    conn.update(worksheet="Clientes", data=pd.concat([df_clientes, novo_cliente], ignore_index=True).astype(str))
                    aviso_c.empty()
                    st.success(f"✅ Cliente {c_nome} cadastrado com sucesso!")
                    time.sleep(1)
