import streamlit as st
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests
import time
import re
import os
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

# --- 2. FUNÇÃO MESTRE: PREENCHER PROCURAÇÃO ---
def preencher_procuracao(dados_carro, dados_procurador):
    caminho_modelo = "modelo_procuracao.docx" # PRECISA SER .DOCX
    
    if not os.path.exists(caminho_modelo):
        return None

    try:
        doc = Document(caminho_modelo)
        
        # Mapeamento Completo
        substituicoes = {
            "{{NOME_TITULAR}}": str(dados_carro.get('nome_titular', '')),
            "{{CPF}}": str(dados_carro.get('cpf_titular', '')),
            "{{RG}}": str(dados_carro.get('rg_titular', '')),
            "{{RUA}}": str(dados_carro.get('endereco_titular', '')),
            "{{NRUA}}": str(dados_carro.get('tit_num', '')),
            "{{BAIRRO}}": str(dados_carro.get('tit_bairro', '')),
            "{{CIDADE}}": str(dados_carro.get('tit_cid', 'Gravataí')),
            "{{UF}}": str(dados_carro.get('tit_est', 'RS')),
            "{{COMPLEMENTO}}": str(dados_carro.get('tit_comp', '')),
            "{{PLACA}}": str(dados_carro.get('placa', '')),
            "{{CHASSI}}": str(dados_carro.get('chassi', '')),
            "{{RENAVAM}}": str(dados_carro.get('renavam', '')),
            "{{MARCAMODELO}}": f"{dados_carro.get('marca', '')} {dados_carro.get('modelo', '')}",
            "{{COR}}": str(dados_carro.get('cor', '')),
            "{{ANO}}": str(dados_carro.get('ano', '')),
            "{{DATA}}": time.strftime("%d/%m/%Y"),
            # Dados do Procurador selecionado no CRM
            "{{NNOME}}": str(dados_procurador.get('nome', '')), 
            "{{NCPF}}": str(dados_procurador.get('cpf', '')),
            "{{NRG}}": str(dados_procurador.get('rg', ''))
        }

        for p in doc.paragraphs:
            for k, v in substituicoes.items():
                if k in p.text:
                    p.text = p.text.replace(k, v)
        
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
    except:
        return None

# --- 3. CONEXÃO E LOGIN ---
conn = st.connection("gsheets", type=GSheetsConnection)

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
        st.subheader("👥 Cadastro de Vendedores / Procuradores")
        with st.form("form_proc"):
            n_p = st.text_input("Nome Completo")
            c_p = st.text_input("CPF")
            r_p = st.text_input("RG")
            if st.form_submit_button("💾 Salvar na Planilha"):
                df_p = conn.read(worksheet="Procuradores", ttl=0).astype(str)
                novo_p = pd.DataFrame([{"nome": n_p, "cpf": c_p, "rg": r_p}])
                conn.update(worksheet="Procuradores", data=pd.concat([df_p, novo_p], ignore_index=True))
                st.success("✅ Procurador cadastrado!"); time.sleep(1); st.rerun()

    # --- ABA: GERENCIAR ESTOQUE ---
    elif menu == "📑 Gerenciar Estoque":
        try:
            df_est = conn.read(worksheet="Estoque", ttl=0).dropna(how='all').astype(str)
            df_procs = conn.read(worksheet="Procuradores", ttl=0).astype(str)
            lista_procs = df_procs['nome'].tolist()
        except:
            st.warning("⚠️ Verifique se as abas 'Estoque' e 'Procuradores' existem na sua planilha.")
            st.stop()

        if df_est.empty:
            st.info("Estoque vazio.")
        else:
            for i, r in df_est.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2])
                    if r.get('foto'): col1.image(r['foto'], use_container_width=True)
                    
                    col2.subheader(f"{r['marca']} {r['modelo']} - {r['placa']}")
                    col2.write(f"Titular: {r['nome_titular']} | CPF: {r['cpf_titular']}")
                    
                    st.write("---")
                    # Selecionar procurador e baixar
                    if lista_procs:
                        c_sel, c_btn = col2.columns([2, 1])
                        proc_escolhido = c_sel.selectbox(f"Selecione quem assina:", options=lista_procs, key=f"s_{i}")
                        
                        dados_p = df_procs[df_procs['nome'] == proc_escolhido].iloc[0].to_dict()
                        arquivo = preencher_procuracao(r, dados_p)
                        
                        if arquivo:
                            c_btn.download_button(
                                label="📜 Baixar Doc",
                                data=arquivo,
                                file_name=f"Procuracao_{r['placa']}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"dl_{i}"
                            )
                        else:
                            c_btn.error("Erro no Word")
                    else:
                        col2.warning("Cadastre um procurador no menu ao lado.")
                    
                    if col2.button("🗑️ Excluir Veículo", key=f"del_{i}"):
                        conn.update(worksheet="Estoque", data=df_est.drop(i).astype(str))
                        st.rerun()

    # --- ABA: CADASTRAR VEÍCULO --- (Mantida Lógica Anterior)
    elif menu == "➕ Cadastrar Veículo":
        st.subheader("📝 Novo Cadastro")
        # Aqui você mantém o código de cadastro de veículo que já tínhamos (FIPE, Cloudinary, etc)
