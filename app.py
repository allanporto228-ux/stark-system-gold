import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO DE INTERFACE E DESIGN GOLD ---
st.set_page_config(
    page_title="Stark System Enterprise - Gold Edition", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilização CSS para o Tema Ouro
st.markdown("""
    <style>
    /* Fundo principal e Sidebar */
    .stApp {
        background-color: #0e1117;
    }
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 2px solid #d4af37;
    }
    
    /* Títulos e Textos */
    h1, h2, h3 {
        color: #d4af37 !important;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
    }
    p, span, label {
        color: #e0e0e0 !important;
    }

    /* Botões Customizados em Ouro */
    div.stButton > button {
        background-color: #d4af37 !important;
        color: #000 !important;
        border-radius: 5px;
        border: none;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #f9d71c !important;
        transform: scale(1.02);
        box-shadow: 0px 0px 15px rgba(212, 175, 55, 0.4);
    }

    /* Inputs e Caixas de Seleção */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1c2128 !important;
        color: #d4af37 !important;
        border: 1px solid #d4af37 !important;
    }

    /* Estilo dos Cards (Métricas) */
    [data-testid="stMetricValue"] {
        color: #d4af37 !important;
        font-size: 2rem !important;
    }
    [data-testid="stMetricDelta"] {
        color: #f9d71c !important;
    }
    
    /* Divisores Ouro */
    hr {
        border: 0;
        height: 1px;
        background: linear-gradient(to right, transparent, #d4af37, transparent);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE BANCO DE DADOS ---
def carregar_dados(arquivo, colunas):
    if not os.path.exists(arquivo):
        df = pd.DataFrame(columns=colunas)
        df.to_csv(arquivo, index=False)
        return df
    try:
        df = pd.read_csv(arquivo)
        if list(df.columns) != colunas:
            df = pd.DataFrame(columns=colunas)
            df.to_csv(arquivo, index=False)
        return df
    except:
        df = pd.DataFrame(columns=colunas)
        df.to_csv(arquivo, index=False)
        return df

def salvar_dados(df, arquivo):
    df.to_csv(arquivo, index=False)

# --- 3. ESTRUTURAS ---
c_per = ['Nome_Empresa', 'CNPJ', 'Telefone', 'Endereco', 'Segmento', 'Qtd_Funcionarios']
c_est = ['Produto', 'Qtd_Atual', 'Unidade', 'Preco_Custo']
c_rec = ['Servico', 'Insumo', 'Quantidade']
c_age = ['Data', 'Cliente', 'Telefone', 'Servico', 'Valor']
c_fin = ['Data', 'Tipo', 'Categoria', 'Descricao', 'Valor']
c_usu = ['Usuario', 'Senha', 'Nome_Empresa']

# Carregamento
df_perfil = carregar_dados('perfil.csv', c_per)
df_estoque = carregar_dados('estoque.csv', c_est)
df_receitas = carregar_dados('receitas.csv', c_rec)
df_agenda = carregar_dados('agenda.csv', c_age)
df_financeiro = carregar_dados('financeiro.csv', c_fin)
df_usuarios = carregar_dados('usuarios.csv', c_usu)

# --- 4. LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>👑 STARK ENTERPRISE GOLD</h1>", unsafe_allow_html=True)
    tab_l, tab_c = st.tabs(["🔑 Acesso VIP", "📝 Nova Conta Master"])
    with tab_l:
        with st.form("login"):
            u, p = st.text_input("Usuário"), st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Sistema"):
                match = df_usuarios[(df_usuarios['Usuario'] == u) & (df_usuarios['Senha'] == p)]
                if not match.empty:
                    st.session_state.autenticado = True
                    st.session_state.empresa = match.iloc[0]['Nome_Empresa']
                    st.rerun()
    with tab_c:
        with st.form("cad"):
            nu, np, ne = st.text_input("Usuário"), st.text_input("Senha"), st.text_input("Empresa")
            if st.form_submit_button("Criar Acesso"):
                salvar_dados(pd.concat([df_usuarios, pd.DataFrame([[nu, np, ne]], columns=c_usu)]), 'usuarios.csv')
                st.success("Conta Criada!")
    st.stop()

# --- 5. MENU ---
with st.sidebar:
    st.markdown(f"<h2 style='text-align:center;'>{st.session_state.empresa}</h2>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("NAVEGAÇÃO PREMIUM", [
        "🏆 Dashboard Executivo", 
        "🏢 Cadastro Unidade",
        "🧪 Ficha Técnica",
        "📦 Insumos & Estoque",
        "📅 Agenda de Atendimentos",
        "💰 Gestão Financeira"
    ])
    st.divider()
    if st.button("🚪 Encerrar Sessão"):
        st.session_state.autenticado = False
        st.rerun()

# --- 🏠 HOME (BI) ---
if menu == "🏆 Dashboard Executivo":
    st.title("🏆 Inteligência de Negócio Stark")
    total_ent = pd.to_numeric(df_financeiro[df_financeiro['Tipo'] == 'Entrada']['Valor']).sum()
    total_sai = pd.to_numeric(df_financeiro[df_financeiro['Tipo'] == 'Saída']['Valor']).sum()
    invest_mkt = pd.to_numeric(df_financeiro[df_financeiro['Categoria'] == 'Marketing']['Valor']).sum()
    
    roi = ((total_ent - invest_mkt) / invest_mkt * 100) if invest_mkt > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 FATURAMENTO BRUTO", f"R$ {total_ent:,.2f}")
    c2.metric("📈 ROI MARKETING", f"{roi:.1f}%")
    c3.metric("👥 TOTAL CLIENTES", len(df_agenda))

    st.divider()
    col_ia, col_chart = st.columns([1, 2])
    with col_ia:
        st.subheader("🤖 FRAN IA")
        st.write("Análise Gold: Seu ROI está acima da média. Recomendo aumentar o investimento em Social Media para o próximo mês.")
    with col_chart:
        if not df_financeiro.empty:
            fig = px.bar(df_financeiro[df_financeiro['Tipo'] == 'Saída'], x='Categoria', y='Valor', color_discrete_sequence=['#d4af37'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#d4af37")
            st.plotly_chart(fig, use_container_width=True)

# --- 🧪 FICHA TÉCNICA ---
elif menu == "🧪 Ficha Técnica":
    st.title("🧪 Engenharia de Serviços")
    with st.form("f_rec"):
        s = st.text_input("Serviço")
        i = st.selectbox("Insumo", df_estoque['Produto'].tolist() if not df_estoque.empty else ["Vazio"])
        q = st.number_input("Consumo (g/ml/un)", min_value=0.0)
        if st.form_submit_button("Vincular Insumo"):
            salvar_dados(pd.concat([df_receitas, pd.DataFrame([[s, i, q]], columns=c_rec)]), 'receitas.csv')
            st.rerun()
    st.dataframe(df_receitas, use_container_width=True)

# --- 📅 AGENDA ---
elif menu == "📅 Agenda de Atendimentos":
    st.title("📅 Agenda VIP")
    with st.form("f_ag"):
        c1, c2 = st.columns(2)
        cli, fone = c1.text_input("Cliente"), c2.text_input("Telefone")
        srv = st.selectbox("Serviço", list(set(df_receitas['Servico'].tolist())) if not df_receitas.empty else ["Crie a Ficha Técnica"])
        vlr = st.number_input("Valor R$", min_value=0.0)
        if st.form_submit_button("Concluir e Baixar Estoque"):
            # Salva Agenda
            salvar_dados(pd.concat([df_agenda, pd.DataFrame([[str(datetime.now().date()), cli, fone, srv, vlr]], columns=c_age)]), 'agenda.csv')
            # Financeiro
            salvar_dados(pd.concat([df_financeiro, pd.DataFrame([[str(datetime.now().date()), 'Entrada', 'Vendas', cli, vlr]], columns=c_fin)]), 'financeiro.csv')
            # Baixa
            consumo = df_receitas[df_receitas['Servico'] == srv]
            for _, item in consumo.iterrows():
                df_estoque.loc[df_estoque['Produto'] == item['Insumo'], 'Qtd_Atual'] -= item['Quantidade']
            salvar_dados(df_estoque, 'estoque.csv')
            st.success("Serviço Concluído!")
    st.dataframe(df_agenda, use_container_width=True)

# --- 💰 FINANCEIRO ---
elif menu == "💰 Gestão Financeira":
    st.title("💰 Fluxo de Caixa Real")
    with st.form("f_fin"):
        tipo = st.selectbox("Tipo", ["Saída", "Entrada"])
        cat = st.selectbox("Categoria", ["Aluguel", "Água/Luz", "Funcionário", "Estoque/Insumos", "Marketing", "Social Mídia"])
        desc = st.text_input("Descrição")
        vlr = st.number_input("Valor R$", min_value=0.0)
        if st.form_submit_button("Lançar no Sistema"):
            salvar_dados(pd.concat([df_financeiro, pd.DataFrame([[str(datetime.now().date()), tipo, cat, desc, vlr]], columns=c_fin)]), 'financeiro.csv')
            st.rerun()
    st.dataframe(df_financeiro, use_container_width=True)

# --- 🏢 CADASTRO UNIDADE ---
elif menu == "🏢 Cadastro Unidade":
    st.title("🏢 Perfil da Empresa")
    with st.form("f_per"):
        n = st.text_input("Nome Fantasia", value=df_perfil.iloc[0]['Nome_Empresa'] if not df_perfil.empty else "")
        c, t = st.text_input("CNPJ"), st.text_input("Telefone")
        e, s = st.text_input("Endereço"), st.text_input("Segmento")
        f = st.number_input("Qtd Funcionários", min_value=1)
        if st.form_submit_button("💾 Salvar Perfil"):
            salvar_dados(pd.DataFrame([[n, c, t, e, s, f]], columns=c_per), 'perfil.csv')
            st.success("Perfil Atualizado!")

# --- 📦 ESTOQUE ---
elif menu == "📦 Insumos & Estoque":
    st.title("📦 Controle de Insumos")
    with st.form("f_est"):
        p, q, u = st.text_input("Insumo"), st.number_input("Qtd"), st.selectbox("Un", ["g", "ml", "un"])
        if st.form_submit_button("📦 Adicionar"):
            salvar_dados(pd.concat([df_estoque, pd.DataFrame([[p, q, u, 0.0]], columns=c_est)]), 'estoque.csv')
            st.rerun()
    st.dataframe(df_estoque, use_container_width=True)