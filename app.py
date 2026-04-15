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
        v = float(re.sub(r'[^\d]', '', str(valor).split(',')[0]))
        return f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except: return str(valor)

def limpar_id(valor):
    s = str(valor).strip()
    return s.split('.')[0] if '.' in s else s

def gerar_procuracao(r):
    """Preenche o DOCX com base no modelo da imagem"""
    try:
        doc = Document("modelo_procuracao.docx")
        
        # Dados que serão substituídos (conforme sua imagem)
        # Se quiser fixar os seus dados (Procurador), altere o NOME, CPF e RG abaixo
        substituicoes = {
            "{{NOME_TITULAR}}": r.get('nome_titular', ''),
            "{{CPF}}": r.get('tit_cpf', ''),
            "{{RG}}": r.get('tit_rg', ''),
            "{{RUA}}": r.get('tit_rua', ''),
            "{{NRUA}}": r.get('tit_num', ''),
            "{{BAIRRO}}": r.get('tit_bairro', ''),
            "{{CIDADE}}": r.get('tit_cid', ''),
            "{{UF}}": r.get('tit_est', ''),
            "{{COMPLEMENTO}}": r.get('tit_comp', ''),
            "{{PLACA}}": r.get('placa', ''),
            "{{CHASSI}}": r.get('chassi', ''),
            "{{RENAVAM}}": r.get('renavam', ''),
            "{{MARCAMODELO}}": f"{r.get('marca', '')}/{r.get('modelo', '')}",
            "{{ANO}}": r.get('ano', ''),
            "{{COR}}": r.get('cor', ''),
            "{{TIPO}}": "VEÍCULO AUTOMOTOR",
            "{{DATA}}": time.strftime("%d de %B de %Y"), # Data por extenso
            # Dados do Procurador (Preencha os seus aqui para ficarem fixos)
            "{{NNOME}}": "NOME DO PROCURADOR AMG", 
            "{{NCPF}}": "000.000.000-00",
            "{{NRG}}": "0000000000"
        }

        # Substitui no corpo do texto
        for p in doc.paragraphs:
            for chave, valor in substituicoes.items():
                if chave in p.text:
                    p.text = p.text.replace(chave, str(valor))
        
        # Substitui em tabelas (se houver)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for chave, valor in substituicoes.items():
                        if chave in cell.text:
                            cell.text = cell.text.replace(chave, str(valor))

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Erro ao ler modelo_procuracao.docx: {e}")
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
    
    # --- ABA: CADASTRAR ---
    if menu == "➕ Cadastrar Veículo":
        st.markdown("## 📝 Novo Cadastro")
        # Lógica de busca FIPE (Marca/Modelo/Ano) omitida aqui para brevidade, mas mantida no seu app
        
        # Simulação do Form após selecionar Ano FIPE:
        with st.form("form_cadastro"):
            st.subheader("🚗 Dados do Veículo")
            c1, c2 = st.columns(2)
            placa_v = c1.text_input("Placa").upper()
            foto_v = c1.file_uploader("📷 Foto Principal", type=['jpg','jpeg','png'])
            marca_v = c2.text_input("Marca")
            modelo_v = c2.text_input("Modelo")
            preco_v = c2.text_input("Preço de Venda")
            
            st.markdown("---")
            st.subheader("📑 Dados do CRLV")
            tit_v = st.text_input("Nome Completo do Titular")
            cc1, cc2, cc3 = st.columns(3)
            ren_v = cc1.text_input("Renavam")
            cha_v = cc2.text_input("Chassi").upper()
            cor_v = cc3.text_input("Cor")
            
            cc4, cc5 = st.columns(2)
            tit_rg = cc4.text_input("RG do Titular")
            tit_cpf = cc5.text_input("CPF do Titular")
            
            st.write("**Endereço do Titular:**")
            rua_v = st.text_input("Rua/Logradouro")
            bairro_v = st.text_input("Bairro") # Campo necessário para sua procuração
            
            cc6, cc7, cc8 = st.columns([1, 2, 1])
            num_v = cc6.text_input("Número")
            comp_v = cc7.text_input("Complemento")
            cid_v = cc8.text_input("Cidade")
            uf_v = st.selectbox("UF", ["RS", "SC", "PR", "SP", "RJ", "MG", "outros"])
            
            doc_v = st.file_uploader("📂 Anexar CRLV/Documentos (PDF/JPG)", type=['pdf','jpg','png'])

            if st.form_submit_button("🚀 SALVAR"):
                # Lógica de upload Cloudinary e Conn.Update igual ao anterior...
                st.success("Veículo salvo no estoque!")

    # --- ABA: ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        df = conn.read(worksheet="Estoque", ttl=0).astype(str)
        
        for i, r in df.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 2])
                if r['foto']: col1.image(r['foto'], use_container_width=True)
                
                col2.subheader(f"{r['marca']} {r['modelo']} - {r['placa']}")
                col2.write(f"Titular: {r['nome_titular']}")
                
                b1, b2, b3 = col2.columns(3)
                if b1.button("✏️ Editar", key=f"ed{i}"):
                    st.session_state.edit_idx = i; st.rerun()
                
                # BOTÃO DE DOWNLOAD DA PROCURAÇÃO
                doc_file = gerar_procuracao(r)
                if doc_file:
                    b2.download_button(
                        label="📜 Gerar Procuração",
                        data=doc_file,
                        file_name=f"Procuracao_{r['placa']}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"proc{i}"
                    )
                
                if b3.button("🗑️ Excluir", key=f"exc{i}"):
                    # Lógica de exclusão...
                    st.rerun()
            st.markdown("---")
