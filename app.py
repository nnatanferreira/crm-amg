import streamlit as st
import pandas as pd

# 1. Configuração da Identidade Visual (Aba do Navegador)
st.set_page_config(page_title="CRM Amg Multimarcas", page_icon="🚗", layout="wide")

# Estilização para as "Tags" de características
st.markdown("""
    <style>
    .car-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        background-color: #f9f9f9;
        margin-bottom: 20px;
    }
    .tag {
        background-color: #e1e1e1;
        padding: 4px 8px;
        border-radius: 5px;
        font-size: 12px;
        margin-right: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚗 CRM Amg Multimarcas")

# Banco de dados temporário
if 'meu_estoque' not in st.session_state:
    st.session_state.meu_estoque = []

# Menu Lateral (Filtro igual ao do site)
st.sidebar.header("Navegação")
aba = st.sidebar.radio("Ir para:", ["Estoque / Cadastro", "Leads", "Anúncios Meta"])

if aba == "Estoque / Cadastro":
    st.subheader("📋 Cadastrar Novo Veículo")
    
    with st.form("novo_carro", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            modelo = st.text_input("Modelo (Ex: Onix 1.0 Turbo)")
            marca = st.selectbox("Marca", ["Chevrolet", "Volkswagen", "Fiat", "Ford", "Hyundai", "Toyota", "Honda", "Nissan", "Renault", "Outros"])
            ano = st.text_input("Ano (Ex: 2021/2022)")

        with col2:
            km = st.number_input("Quilometragem (KM)", min_value=0)
            cambio = st.selectbox("Câmbio", ["Automático", "Manual"])
            combustivel = st.selectbox("Combustível", ["Flex", "Gasolina", "Diesel", "Híbrido/Elétrico"])

        with col3:
            valor = st.number_input("Preço (R$)", min_value=0)
            cor = st.text_input("Cor")
            foto = st.file_uploader("Foto Principal", type=['png', 'jpg', 'jpeg'])
        
        botao = st.form_submit_button("Adicionar ao Site/CRM")
        
        if botao and modelo:
            st.session_state.meu_estoque.append({
                "Modelo": modelo, "Marca": marca, "Ano": ano, "KM": km,
                "Cambio": cambio, "Combustivel": combustivel,
                "Preço": valor, "Cor": cor, "Foto": foto
            })
            st.success(f"{modelo} adicionado com sucesso!")

    # Exibição do Estoque Estilo "Card" do Site
    if st.session_state.meu_estoque:
        st.divider()
        st.subheader("🚘 Estoque Atual")
        
        for idx, carro in enumerate(st.session_state.meu_estoque):
            with st.container():
                col_img, col_txt = st.columns([1, 2])
                
                with col_img:
                    if carro["Foto"]:
                        st.image(carro["Foto"], use_container_width=True)
                    else:
                        st.info("Sem imagem")
                
                with col_txt:
                    st.markdown(f"### {carro['Marca']} {carro['Modelo']}")
                    st.markdown(f"**Preço:** <span style='color:green; font-size:20px'>R$ {carro['Preço']:,.2f}</span>", unsafe_allow_html=True)
                    
                    # Tags de características igual ao site
                    st.markdown(f"""
                        <span class="tag">📅 {carro['Ano']}</span>
                        <span class="tag">🛣️ {carro['KM']:,} KM</span>
                        <span class="tag">⚙️ {carro['Cambio']}</span>
                        <span class="tag">⛽ {carro['Combustivel']}</span>
                        <span class="tag">🎨 {carro['Cor']}</span>
                    """, unsafe_allow_html=True)
                    
                    st.write("") # Espaço
                    if st.button(f"Criar Anúncio Facebook", key=f"ads_{idx}"):
                        st.toast(f"Gerando criativo para o {carro['Modelo']}...")

                st.divider()

elif aba == "Anúncios Meta":
    st.subheader("🚀 Impulsionar Estoque")
    st.write("Selecione o veículo para criar a campanha baseada nos dados do site.")