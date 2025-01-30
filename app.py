import streamlit as st
import pandas as pd
import numpy as np
import datetime
import calendar

# 1) Configurações iniciais de página (título, ícone, layout)
st.set_page_config(
    page_title="Controle de Investimentos",
    page_icon=":money_with_wings:",  # ou outro emoji
    layout="centered",               # 'centered' ou 'wide'
    initial_sidebar_state="auto"
)

st.title("Controle de Investimentos")
st.write("""
Esta aplicação demonstra como acompanhar seus investimentos de forma mais visual.
Ela é configurada para ser acessada em diferentes tamanhos de tela, incluindo smartphones.
""")

# --- Definir dados iniciais ---
start_date = datetime.date(2025, 1, 10)
end_date = datetime.date(2025, 12, 31)

# Lista de datas + valores de aporte
data_aportes = []
# Aporte inicial (10/01/2025) de US$200 por bloco
data_aportes.append((start_date, 200, 200, 200))

# Gerar datas mensais (1 a 12) e colocar aporte dia 30 ou último dia se não existir dia 30
for mes in range(1, 13):
    ultimo_dia = calendar.monthrange(2025, mes)[1]
    dia = 30 if 30 <= ultimo_dia else ultimo_dia
    aporte_date = datetime.date(2025, mes, dia)
    if start_date <= aporte_date <= end_date:
        # Aporte mensal de US$30 em cada bloco (Câmbio, Ações, Cripto)
        data_aportes.append((aporte_date, 30, 30, 30))

# Criar DataFrame de aportes
df = pd.DataFrame(data_aportes, columns=["Data", "Câmbio", "Ações", "Cripto"])
df = df.sort_values("Data").reset_index(drop=True)
df["Data"] = pd.to_datetime(df["Data"])

st.subheader("Aportes Programados")
st.dataframe(df)

# --- Simulação de Crescimento ---
st.write("""
### Taxas de Crescimento Anuais (projeção)
Escolha abaixo a taxa de rendimento anual (em %) que você deseja simular 
para cada classe de investimento. A aplicação converterá para juros mensais compostos.
""")

# Sliders para cada classe
taxa_cambio = st.slider("Taxa anual para Câmbio (%)", -10, 50, 5)
taxa_acoes  = st.slider("Taxa anual para Ações (%)", -10, 50, 10)
taxa_cripto = st.slider("Taxa anual para Cripto (%)", -10, 200, 50)

def annual_to_monthly(annual_rate):
    r = annual_rate / 100
    return (1 + r)**(1/12) - 1

m_cambio = annual_to_monthly(taxa_cambio)
m_acoes  = annual_to_monthly(taxa_acoes)
m_cripto = annual_to_monthly(taxa_cripto)

# Cria um índice de datas no último dia de cada mês (freq='M') para a simulação
period_index = pd.date_range(start=start_date, end=end_date, freq='M')

# DataFrame para armazenar saldos
saldo_df = pd.DataFrame(index=period_index, columns=["Câmbio", "Ações", "Cripto"], data=0.0)

# Saldos iniciais no primeiro mês
saldo_df.iloc[0] = [200, 200, 200]

for i in range(1, len(saldo_df)):
    saldo_ant_cambio = saldo_df.iloc[i-1]["Câmbio"]
    saldo_ant_acoes  = saldo_df.iloc[i-1]["Ações"]
    saldo_ant_cripto = saldo_df.iloc[i-1]["Cripto"]
    
    # Aplica rentabilidade mensal
    saldo_cambio = saldo_ant_cambio * (1 + m_cambio)
    saldo_acoes  = saldo_ant_acoes  * (1 + m_acoes)
    saldo_cripto = saldo_ant_cripto * (1 + m_cripto)
    
    # Verifica aportes no mês
    ano_atual = saldo_df.index[i].year
    mes_atual = saldo_df.index[i].month
    
    mes_aportes = df[(df["Data"].dt.year == ano_atual) & (df["Data"].dt.month == mes_atual)]
    if not mes_aportes.empty:
        saldo_cambio += mes_aportes["Câmbio"].sum()
        saldo_acoes  += mes_aportes["Ações"].sum()
        saldo_cripto += mes_aportes["Cripto"].sum()
    
    saldo_df.iloc[i] = [saldo_cambio, saldo_acoes, saldo_cripto]

# Organiza o DataFrame final
saldo_df = saldo_df.reset_index().rename(columns={"index": "Data"})
saldo_df["Total"] = saldo_df["Câmbio"] + saldo_df["Ações"] + saldo_df["Cripto"]

st.subheader("Evolução Mensal Projetada")
st.dataframe(
    saldo_df.style.format(
        subset=["Câmbio", "Ações", "Cripto", "Total"],
        formatter="{:.2f}"
    )
)

# Gráfico
st.write("### Gráfico de evolução ao longo do tempo")
chart_data = saldo_df.set_index("Data")[["Câmbio", "Ações", "Cripto", "Total"]]
st.line_chart(chart_data)

# Valor final em 31/12/2025
valor_final = saldo_df.iloc[-1]["Total"]
st.write(f"### Valor Total Estimado em 31/12/2025: **US$ {valor_final:,.2f}**")

st.write("""
---
<small>Aplicação desenvolvida em Python (Streamlit), demonstrando
como acompanhar e projetar investimentos.</small>
""", unsafe_allow_html=True)
