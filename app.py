import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests
import time
import re
from docx import Document
from io import BytesIO

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
    if not valor or str(valor).lower() in ["nan", "none", ""]: return "0,00"
    try:
        if "R$" in str(valor): return str(valor).replace("R$", "").strip()
        texto = str(valor).replace('R$', '').strip()
        apenas_numeros = re.sub(r'[^\d]', '', texto.split(',')[0].split('.')[0])
        v = float(apenas_numeros)
        return f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except: return str(valor)

def limpar_id(valor):
    s = str(valor).strip()
    return s.split('.')[0] if '.' in s else s

def gerar_procuracao(dados_veiculo):
    """Lê o modelo docx e substitui as chaves pelos dados da planilha"""
    try:
        # Você deve subir o arquivo modelo.docx no mesmo diretório do Github
        doc = Document("modelo_procuracao.docx")
        
        # Mapeamento de chaves no Word para colunas na Planilha
        substituicoes = {
            "{{NOME_TITULAR}}": str(dados_veiculo.get('nome_titular', '')),
            "{{RG}}": str(dados_veiculo.get('tit_rg', '')),
            "{{CPF}}": str(dados_veiculo.get('tit_cpf', '')),
            "{{RUA}}": str(dados_veiculo.get('tit_rua', '')),
            "{{NUMERO}}": str(dados_veiculo.get('tit_num', '')),
            "{{CIDADE}}": str(dados_veiculo.get('tit_cid', '')),
            "{{ESTADO}}": str(dados_veiculo.get('tit_est', '')),
            "{{PLACA}}": str(dados_veiculo.get('placa', '')),
            "{{CHASSI}}": str(dados_veiculo.get('chassi', '')),
            "{{RENAVAM}}": str(dados_veiculo.get('renavam', '')),
            "{{MODELO}}": str(dados_veiculo.get('modelo', '')),
            "{{MARCA}}": str(dados_veiculo.get('marca', '')),
            "{{COR}}": str(dados_veiculo.get('cor', '')),
            "{{DATA_HOJE}}": time.strftime("%d/%m/%Y")
        }

        for p in doc.paragraphs:
            for codigo, valor in substituicoes.items():
                if codigo in p.text:
                    p.text = p.text.replace(codigo, valor)
        
        # Salva o arquivo em memória para download
        conteudo_puro = BytesIO()
        doc.save(conteudo_puro)
        conteudo_puro.seek(0)
        return conteudo_puro
    except Exception as e:
        st.error(f"Erro ao gerar documento: Verifique se o arquivo 'modelo_procuracao.docx' está no Github. Erro: {e}")
        return None

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

    # --- ABA: CADASTRAR --- (Mantida sem alterações)
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
                    dfipe = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{dict_marcas[marca_n]}/models/{dict_modelos[modelo_n]}/years/{dict_anos[ano_sel]}").json()
                    
                    with st.form("form_cadastro"):
                        st.subheader("🚗 Informações do Veículo")
                        c1, c2 = st.columns(2)
                        marca_v = c1.text_input("Marca", value=dfipe.get('brand'))
                        modelo_v = c1.text_input("Modelo", value=dfipe.get('model'))
                        placa_v = c1.text_input("Placa").upper()
                        foto_v = c1.file_uploader("📷 Foto Principal", type=['jpg','jpeg','png'])
                        
                        preco_v = c2.text_input("Preço de Venda", value=formatar_para_br(dfipe.get('price')))
                        km_v = c2.text_input("Quilometragem", value="0")
                        comb_v = c2.text_input("Combustível", value=dfipe.get('fuel'))
                        cor_v = c2.text_input("Cor")

                        st.markdown("---")
                        st.subheader("📑 Dados do CRLV")
                        tit_v = st.text_input("Nome Completo do Titular")
                        cc1, cc2 = st.columns(2)
                        ren_v = cc1.text_input("Renavam")
                        cha_v = cc2.text_input("Chassi").upper()
                        cc3, cc4 = st.columns(2)
                        tit_rg = cc3.text_input("RG do Titular")
                        tit_cpf = cc4.text_input("CPF do Titular")
                        
                        st.write("**Endereço do Titular:**")
                        tit_rua = st.text_input("Rua/Logradouro")
                        cc5, cc6 = st.columns([1, 2])
                        tit_num = cc5.text_input("Número")
                        tit_comp = cc6.text_input("Complemento")
                        cc7, cc8 = st.columns(2)
                        tit_cid = cc7.text_input("Cidade")
                        tit_est = cc8.selectbox("UF", ["SP", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SE", "TO"])
                        doc_v = st.file_uploader("📂 Documento (CRLV/RG)", type=['pdf','jpg','jpeg','png'])

                        if st.form_submit_button("🚀 SALVAR NO ESTOQUE"):
                            if not placa_v: st.error("Placa obrigatória!"); st.stop()
                            url_img = cloudinary.uploader.upload(foto_v)['secure_url'] if foto_v else ""
                            url_doc = cloudinary.uploader.upload(doc_v)['secure_url'] if doc_v else ""
                            try: df_atual = conn.read(worksheet="Estoque", ttl=0).astype(str)
                            except: df_atual = pd.DataFrame()
                            novo = pd.DataFrame([{
                                "marca": marca_v, "modelo": modelo_v, "placa": placa_v, "renavam": limpar_id(ren_v), "chassi": cha_v.strip(),
                                "cor": cor_v, "combustivel": comb_v, "preco": formatar_para_br(preco_v), "km": limpar_id(km_v), "foto": url_img,
                                "nome_titular": tit_v, "tit_rg": tit_rg, "tit_cpf": tit_cpf, "tit_rua": tit_rua, "tit_num": tit_num, 
                                "tit_comp": tit_comp, "tit_cid": tit_cid, "tit_est": tit_est, "doc_titular": url_doc, "ano": ano_sel
                            }])
                            conn.update(worksheet="Estoque", data=pd.concat([df_atual, novo], ignore_index=True).astype(str))
                            st.success("✅ Cadastrado!"); time.sleep(1); st.rerun()

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all').astype(str)
        except:
            df = pd.DataFrame()

        if df.empty:
            st.info("Estoque vazio.")
        elif "edit_idx" in st.session_state:
            # (Seção de edição permanece igual...)
            idx = st.session_state.edit_idx
            item = df.iloc[idx]
            st.markdown(f"### ✏️ Editando: {item['placa']}")
            with st.form("form_edicao"):
                st.subheader("🚗 Informações do Veículo")
                c1, c2 = st.columns(2)
                m_e = c1.text_input("Marca", value=item['marca'])
                mo_e = c1.text_input("Modelo", value=item['modelo'])
                pl_e = c1.text_input("Placa", value=item['placa']).upper()
                f_v_e = c1.file_uploader("Trocar Foto")
                pr_e = c2.text_input("Preço", value=formatar_para_br(item['preco']))
                km_e = c2.text_input("KM", value=limpar_id(item['km']))
                comb_e = c2.text_input("Combustível", value=item.get('combustivel',''))
                cor_e = c2.text_input("Cor", value=item.get('cor',''))
                st.markdown("---")
                st.subheader("📑 Dados do CRLV")
                tit_e = st.text_input("Nome do Titular", value=item.get('nome_titular',''))
                cc1e, cc2e = st.columns(2)
                ren_e = cc1e.text_input("Renavam", value=limpar_id(item.get('renavam','')))
                cha_e = cc2e.text_input("Chassi", value=item.get('chassi','')).upper()
                cc3e, cc4e = st.columns(2)
                rg_e = cc3e.text_input("RG", value=item.get('tit_rg',''))
                cpf_e = cc4e.text_input("CPF", value=item.get('tit_cpf',''))
                rua_e = st.text_input("Rua", value=item.get('tit_rua',''))
                cc5e, cc6e = st.columns([1, 2])
                num_e = cc5e.text_input("Nº", value=item.get('tit_num',''))
                comp_e = cc6e.text_input("Compl.", value=item.get('tit_comp',''))
                cc7e, cc8e = st.columns(2)
                cid_e = cc7e.text_input("Cidade", value=item.get('tit_cid',''))
                est_e = cc8e.text_input("UF", value=item.get('tit_est','SP'))
                f_d_e = st.file_uploader("Trocar Documento")
                
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.form_submit_button("💾 SALVAR"):
                    url_v = cloudinary.uploader.upload(f_v_e)['secure_url'] if f_v_e else item['foto']
                    url_d = cloudinary.uploader.upload(f_d_e)['secure_url'] if f_d_e else item.get('doc_titular','')
                    df.at[idx, 'marca'] = m_e; df.at[idx, 'modelo'] = mo_e; df.at[idx, 'placa'] = pl_e; df.at[idx, 'preco'] = formatar_para_br(pr_e)
                    df.at[idx, 'km'] = limpar_id(km_e); df.at[idx, 'renavam'] = limpar_id(ren_e); df.at[idx, 'chassi'] = cha_e; df.at[idx, 'cor'] = cor_e
                    df.at[idx, 'combustivel'] = comb_e; df.at[idx, 'nome_titular'] = tit_e; df.at[idx, 'foto'] = url_v; df.at[idx, 'doc_titular'] = url_d
                    df.at[idx, 'tit_rg'] = rg_e; df.at[idx, 'tit_cpf'] = cpf_e; df.at[idx, 'tit_rua'] = rua_e
                    df.at[idx, 'tit_num'] = num_e; df.at[idx, 'tit_comp'] = comp_e; df.at[idx, 'tit_cid'] = cid_e; df.at[idx, 'tit_est'] = est_e
                    conn.update(worksheet="Estoque", data=df.astype(str))
                    st.success("✅ Atualizado!"); del st.session_state.edit_idx; time.sleep(1); st.rerun()
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
                    col2.write(f"Placa: {r['placa']} | Titular: {r.get('nome_titular', '-')}")
                    
                    btn_c1, btn_c2, btn_c3 = col2.columns(3)
                    if btn_c1.button(f"✏️ Editar", key=f"e{i}"):
                        st.session_state.edit_idx = i; st.rerun()
                    
                    # --- NOVO BOTÃO DE PROCURAÇÃO ---
                    doc_pronto = gerar_procuracao(r)
                    if doc_pronto:
                        btn_c2.download_button(
                            label="📜 Procuração",
                            data=doc_pronto,
                            file_name=f"Procuracao_{r['placa']}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"doc{i}"
                        )
                    
                    if btn_c3.button(f"🗑️ Excluir", key=f"d{i}"):
                        df_novo = df.drop(i)
                        conn.update(worksheet="Estoque", data=df_novo.astype(str))
                        st.rerun()
                st.markdown("---")
