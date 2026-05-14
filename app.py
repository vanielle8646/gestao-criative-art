import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Arte Criativa - Gestão", layout="wide")

# URL da sua planilha
url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_limpo():
    # ttl=0 garante que ele não use o "cache" e pegue o dado mais atualizado
    df_raw = conn.read(spreadsheet=url, ttl=0)
    if df_raw is not None and not df_raw.empty:
        df_raw.columns = [str(c).strip() for c in df_raw.columns]
        # Remove lixo (linhas sem data)
        return df_raw.dropna(subset=['Data']).copy()
    return pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Valor", "Status"])

df = carregar_limpo()

def para_float(val):
    if pd.isna(val) or val == "": return 0.0
    if isinstance(val, (int, float)): return float(val)
    try:
        return float(str(val).replace('R$', '').replace('.', '').replace(',', '.').strip())
    except: return 0.0

st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle - Arte Criativa</h1>", unsafe_allow_html=True)

# --- CÁLCULOS DO TOPO ---
if 'Valor' in df.columns:
    df['V_num'] = df['Valor'].apply(para_float)
    df['Data_dt'] = pd.to_datetime(df['Data'], errors='coerce')
    
    hoje = datetime.now()
    df_mes = df[(df['Data_dt'].dt.month == hoje.month) & (df['Data_dt'].dt.year == hoje.year)]
    
    # Se o mês estiver vazio, mostramos 0 em vez de erro
    ent = df_mes[df_mes['Tipo'].str.contains('Entrada', case=False, na=False)]['V_num'].sum()
    sai = df_mes[df_mes['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['V_num'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Receitas", f"R$ {ent:,.2f}")
    c2.metric("Despesas", f"R$ {sai:,.2f}")
    c3.metric("Saldo", f"R$ {ent-sai:,.2f}")

st.divider()

# --- FORMULÁRIO COM NOVO MÉTODO DE SALVAMENTO ---
st.subheader("➕ Novo Lançamento")
with st.form("form_v3", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        data_f = st.date_input("Data", datetime.now())
        desc_f = st.text_input("Descrição")
    with col2:
        val_f = st.number_input("Valor", min_value=0.0, format="%.2f")
        tipo_f = st.selectbox("Tipo", ["Entrada", "Saída"])
    
    enviar = st.form_submit_button("Salvar no Sistema")

if enviar:
    if desc_f and val_f > 0:
        try:
            # Criamos a linha nova
            nova_linha = pd.DataFrame([{
                "Data": data_f.strftime("%Y/%m/%d"),
                "Descrição": desc_f,
                "Tipo": tipo_f,
                "Valor": val_f,
                "Status": "Pago"
            }])
            
            # Unimos com o que já existe
            # Usamos as colunas exatas da planilha para não criar colunas novas
            df_final = pd.concat([df[["Data", "Descrição", "Tipo", "Valor", "Status"]], nova_linha], ignore_index=True)
            
            # Método UPDATE reescrevendo tudo (mais seguro para manter a formatação)
            conn.update(spreadsheet=url, data=df_final)
            
            st.success("✅ Lançamento gravado com sucesso!")
            st.cache_data.clear() # Limpa o cache para forçar a leitura do dado novo
            st.rerun()
        except Exception as e:
            st.error(f"Erro técnico: {e}")
            st.info("Tente recarregar a página da planilha no seu navegador e depois tente salvar aqui novamente.")
    else:
        st.warning("Preencha a Descrição e o Valor.")

st.divider()
st.subheader("📝 Histórico Recente")
st.dataframe(df[["Data", "Descrição", "Tipo", "Valor", "Status"]].tail(10), use_container_width=True)
