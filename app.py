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

# --- CONFIGURAÇÕES CLOUDINARY ---
cloudinary.config( 
  cloud_name = "dybos073q", 
  api_key = "332571224149431", 
  api_secret = "bVdxjWZBAQ4_iGlaJAg0Kze3ZRU",
  secure = True
)

st.set_page_config(page_title="CRM AMG Multimarcas", page_icon="🚗", layout="wide")

# --- FUNÇÃO PARA PREENCHER O WORD ---
def preencher_procuracao(dados_carro, dados_procurador):
    caminho_modelo = "modelo_procuracao.docx"
    
    if not os.path.exists(caminho_modelo):
        st.error(f"⚠️ O arquivo '{caminho_modelo}' não foi encontrado no GitHub. Por favor, faça o upload dele.")
        return None

    try:
        doc = Document(caminho_modelo)
        
        # Mapeamento conforme sua imagem da procuração e nomes da planilha
        substituicoes = {
            # Dados do Cliente (Aba Estoque)
            "{{NOME_TITULAR}}": str(dados_carro.get('nome_titular', '')),
            "{{CPF}}": str(dados_carro.get('cpf_titular', '')),
            "{{RG}}": str(dados_carro.get('rg_titular', '')),
            "{{RUA}}": str(dados_carro.get('endereco_titular', '')),
            "{{NRUA}}": str(dados_carro.get('tit_num', '')),
            "{{BAIRRO}}": str(dados_carro.get('tit_bairro', '')),
            "{{CIDADE}}": str(dados_carro.get('tit_cid', 'Gravataí')),
            "{{UF}}": str(dados_carro.get('tit_est', 'RS')),
            "{{PLACA}}": str(dados_carro.get('placa', '')),
            "{{CHASSI}}": str(dados_carro.get('chassi', '')),
            "{{RENAVAM}}": str(dados_carro.get('renavam', '')),
            "{{MARCAMODELO}}": f"{dados_carro.get('marca', '')} {dados_carro.get('modelo', '')}",
            "{{COR}}": str(dados_carro.get('cor', '')),
            "{{ANO}}": str(dados_carro.get('ano', '')),
            "{{TIPO}}": "VEÍCULO AUTOMOTOR",
            "{{DATA}}": time.strftime("%d/%m/%Y"),
            
            # Dados do Procurador Escolhido (Aba Procuradores)
            "{{NNOME}}": str(dados_procurador.get('nome', '')), 
            "{{NCPF}}": str(dados_procurador.get('cpf', '')),
            "{{NRG}}": str(dados_procurador.get('rg', ''))
        }

        # Substituição em parágrafos e tabelas
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
    except Exception as e:
        st.error(f"Erro ao processar o Word: {e}")
        return None

# --- CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN (Simplificado para o exemplo) ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = True # Remova para produção

# --- MENU LATERAL ---
menu = st.sidebar.radio("Navegação", ["➕ Cadastrar Veículo", "📑 Gerenciar Estoque", "👥 Cadastrar Procurador"])

# --- ABA: CADASTRAR PROCURADOR ---
if menu == "👥 Cadastrar Procurador":
    st.subheader("👥 Cadastro de Procuradores")
    with st.form("form_proc"):
        n_p = st.text_input("Nome Completo")
        c_p = st.text_input("CPF")
        r_p = st.text_input("RG")
        if st.form_submit_button("Salvar"):
            df_p = conn.read(worksheet="Procuradores", ttl=0).astype(str)
            novo_p = pd.DataFrame([{"nome": n_p, "cpf": c_p, "rg": r_p}])
            conn.update(worksheet="Procuradores", data=pd.concat([df_p, novo_p], ignore_index=True))
            st.success("Cadastrado!"); st.rerun()

# --- ABA: GERENCIAR ESTOQUE ---
elif menu == "📑 Gerenciar Estoque":
    st.header("📑 Estoque Atual")
    
    try:
        df_estoque = conn.read(worksheet="Estoque", ttl=0).astype(str)
        df_procs = conn.read(worksheet="Procuradores", ttl=0).astype(str)
        lista_procs = df_procs['nome'].tolist()
    except:
        st.error("Certifique-se de que as abas 'Estoque' e 'Procuradores' existem na planilha.")
        st.stop()

    for i, r in df_estoque.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([1, 3])
            
            if r.get('foto'): c1.image(r['foto'], use_container_width=True)
            
            c2.subheader(f"{r['marca']} {r['modelo']} ({r['placa']})")
            c2.write(f"Dono: {r['nome_titular']}")
            
            # BOTÃO COM OPÇÃO DE PROCURADOR
            st.markdown("---")
            col_proc, col_btn = c2.columns([2, 1])
            
            if lista_procs:
                proc_selecionado = col_proc.selectbox(
                    "Quem será o procurador?", 
                    options=lista_procs, 
                    key=f"sel_{i}"
                )
                
                # Ao clicar, gera o arquivo
                dados_p = df_procs[df_procs['nome'] == proc_selecionado].iloc[0].to_dict()
                doc_file = preencher_procuracao(r, dados_p)
                
                if doc_file:
                    col_btn.download_button(
                        label="📥 Baixar Procuração",
                        data=doc_file,
                        file_name=f"Procuracao_{r['placa']}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"btn_{i}"
                    )
            else:
                col_proc.warning("⚠️ Cadastre um procurador primeiro!")

            if c2.button("🗑️ Excluir", key=f"del_{i}"):
                conn.update(worksheet="Estoque", data=df_estoque.drop(i).astype(str))
                st.rerun()
