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

def preencher_procuracao(dados_carro, dados_procurador):
    """Lê o modelo Word e preenche com dados do cliente e do procurador selecionado"""
    try:
        doc = Document("modelo_procuracao.docx")
        
        # Mapeamento de chaves conforme a estrutura da tua planilha e Word
        substituicoes = {
            # DADOS DO CLIENTE / CARRO (Vêm da aba Estoque)
            "{{NOME_TITULAR}}": str(dados_carro.get('nome_titular', '')),
            "{{CPF}}": str(dados_carro.get('cpf_titular', '')),
            "{{RG}}": str(dados_carro.get('rg_titular', '')),
            "{{RUA}}": str(dados_carro.get('endereco_titular', '')),
            "{{NRUA}}": str(dados_carro.get('tit_num', '')),
            "{{BAIRRO}}": str(dados_carro.get('tit_bairro', '')),
            "{{CIDADE}}": str(dados_carro.get('tit_cid', '')),
            "{{UF}}": str(dados_carro.get('tit_est', '')),
            "{{COMPLEMENTO}}": str(dados_carro.get('tit_comp', '')),
            "{{PLACA}}": str(dados_carro.get('placa', '')),
            "{{CHASSI}}": str(dados_carro.get('chassi', '')),
            "{{RENAVAM}}": str(dados_carro.get('renavam', '')),
            "{{MARCAMODELO}}": f"{dados_carro.get('marca', '')}/{dados_carro.get('modelo', '')}",
            "{{COR}}": str(dados_carro.get('cor', '')),
            "{{ANO}}": str(dados_carro.get('ano', '')),
            "{{DATA}}": time.strftime("%d/%m/%Y"),
            
            # DADOS DO PROCURADOR (Vêm da aba Procuradores)
            "{{NNOME}}": str(dados_procurador.get('nome', '')), 
            "{{NCPF}}": str(dados_procurador.get('cpf', '')),
            "{{NRG}}": str(dados_procurador.get('rg', ''))
        }

        # Substituição no corpo do texto
        for p in doc.paragraphs:
            for k, v in substituicoes.items():
                if k in p.text:
                    p.text = p.text.replace(k, v)
        
        # Substituição em tabelas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for k, v in substituicoes.items():
                        if k in cell.text:
                            cell.text = cell.text.replace(k, v)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Erro ao gerar Word: {e}")
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
    menu = st.sidebar.radio("Navegação", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque", "👥 Cadastrar Procurador"])
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    # --- ABA: CADASTRAR PROCURADOR ---
    if menu == "👥 Cadastrar Procurador":
        st.markdown("## 👥 Cadastro de Procuradores / Vendedores")
        with st.form("form_vendedor"):
            nome_p = st.text_input("Nome Completo do Procurador")
            cpf_p = st.text_input("CPF")
            rg_p = st.text_input("RG")
            if st.form_submit_button("💾 Salvar Procurador"):
                try: df_p = conn.read(worksheet="Procuradores", ttl=0).astype(str)
                except: df_p = pd.DataFrame(columns=["nome", "cpf", "rg"])
                
                novo_p = pd.DataFrame([{"nome": nome_p, "cpf": cpf_p, "rg": rg_p}])
                conn.update(worksheet="Procuradores", data=pd.concat([df_p, novo_p], ignore_index=True))
                st.success("✅ Procurador guardado com sucesso!")
                time.sleep(1); st.rerun()

    # --- ABA: CADASTRAR VEÍCULO ---
    elif menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Novo Cadastro de Veículo")
        # Busca marcas FIPE
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
                        cor_v = c2.text_input("Cor")
                        comb_v = c2.text_input("Combustível", value=dfipe.get('fuel'))

                        st.markdown("---")
                        st.subheader("📑 Dados do Titular (CRLV)")
                        nome_v = st.text_input("Nome Completo do Titular")
                        cc1, cc2 = st.columns(2)
                        cpf_v = cc1.text_input("CPF do Titular")
                        rg_v = cc2.text_input("RG do Titular")
                        
                        st.write("**Endereço:**")
                        rua_v = st.text_input("Rua/Logradouro")
                        bairro_v = st.text_input("Bairro")
                        cc3, cc4, cc5 = st.columns([1, 2, 2])
                        num_v = cc3.text_input("Nº")
                        comp_v = cc4.text_input("Comp.")
                        cid_v = cc5.text_input("Cidade", value="Gravataí")
                        est_v = st.selectbox("UF", ["RS", "SC", "PR", "SP"])

                        if st.form_submit_button("🚀 SALVAR NO ESTOQUE"):
                            if not placa_v: st.error("Placa obrigatória!"); st.stop()
                            url_img = cloudinary.uploader.upload(foto_v)['secure_url'] if foto_v else ""
                            try: df_est = conn.read(worksheet="Estoque", ttl=0).astype(str)
                            except: df_est = pd.DataFrame()
                            
                            novo_carro = pd.DataFrame([{
                                "marca": marca_v, "modelo": modelo_v, "placa": placa_v, "preco": preco_v,
                                "foto": url_img, "nome_titular": nome_v, "cpf_titular": cpf_v, "rg_titular": rg_v,
                                "endereco_titular": rua_v, "tit_bairro": bairro_v, "tit_num": num_v,
                                "tit_comp": comp_v, "tit_cid": cid_v, "tit_est": est_v, "ano": ano_sel,
                                "km": km_v, "cor": cor_v, "combustivel": comb_v, "renavam": "", "chassi": ""
                            }])
                            conn.update(worksheet="Estoque", data=pd.concat([df_est, novo_carro], ignore_index=True).astype(str))
                            st.success("✅ Veículo Cadastrado!"); time.sleep(1); st.rerun()

    # --- ABA: GERENCIAR ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df = conn.read(worksheet="Estoque", ttl=0).dropna(how='all').astype(str)
            df_procs = conn.read(worksheet="Procuradores", ttl=0).astype(str)
            lista_procs = df_procs['nome'].tolist()
        except:
            df = pd.DataFrame()
            lista_procs = []

        if df.empty:
            st.info("O estoque está vazio.")
        else:
            for i, r in df.iterrows():
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    if r.get('foto') and "http" in r['foto']: col1.image(r['foto'], use_container_width=True)
                    
                    col2.subheader(f"{r['marca']} {r['modelo']} - {r['placa']}")
                    col2.write(f"Titular: {r['nome_titular']} | Preço: R$ {r['preco']}")
                    
                    # ÁREA DA PROCURAÇÃO
                    if lista_procs:
                        st.write("---")
                        c_sel, c_btn = col2.columns([2, 1])
                        proc_nome = c_sel.selectbox("Assinado por:", options=lista_procs, key=f"s_{i}")
                        
                        # Pega os dados do procurador selecionado
                        dados_p = df_procs[df_procs['nome'] == proc_nome].iloc[0].to_dict()
                        
                        # Gera o ficheiro
                        doc_gerado = preencher_procuracao(r, dados_p)
                        if doc_gerado:
                            c_btn.download_button(
                                label="📜 Procuração",
                                data=doc_gerado,
                                file_name=f"Procuracao_{r['placa']}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"btn_{i}"
                            )
                    else:
                        col2.warning("⚠️ Cadastra um Procurador primeiro para gerar documentos.")

                    if col2.button("🗑️ Remover Veículo", key=f"del_{i}"):
                        conn.update(worksheet="Estoque", data=df.drop(i).astype(str))
                        st.rerun()
                st.markdown("---")
