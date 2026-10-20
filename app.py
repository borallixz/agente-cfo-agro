import altair as alt
import pandas as pd
import streamlit as st
from calculos import (kg_semente_ha, sementes_por_metro, custo_semente_ha,
                      custo_total_ha, receita_por_ha, margem_por_ha,
                      custo_por_saca, ponto_equilibrio, folga_sobre_equilibrio)
from estilo import CSS

st.set_page_config(page_title="Agente CFO do Agro", page_icon="🌱", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


def num(v, casas=1):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def brl(v):
    return "R$ " + num(v, 2)


def kpi(label, value, sub="", icone="ic-coin"):
    return (f'<div class="kpi {icone}"><div class="label">{label}</div>'
            f'<div class="value">{value}</div><div class="sub">{sub}</div></div>')


# ---------- painel lateral: entradas ----------
with st.sidebar:
    st.header("🚜 Dados da lavoura")
    cultivar = st.text_input("Cultivar", value="Cultivar exemplo")
    area = st.number_input("Área (ha)", value=100.0, min_value=1.0, step=10.0)

    with st.expander("🌱 Semente", expanded=True):
        populacao = st.number_input("População (plantas/ha)", value=260000.0, step=5000.0, format="%.0f")
        pms = st.number_input("Peso de mil sementes (g)", value=150.0, step=1.0)
        espacamento = st.number_input("Espaçamento (m)", value=0.45, step=0.05)
        germinacao = st.number_input("Germinação (%)", value=92.1, min_value=1.0, max_value=100.0, step=0.1)
        emergencia = st.number_input("Emergência em campo (%)", value=100.0, min_value=1.0, max_value=100.0, step=1.0)
        preco_saco = st.number_input("Preço do saco de 40 kg (R$)", value=280.0, step=10.0)

    with st.expander("💰 Custos", expanded=True):
        royalties = st.number_input("Royalties (R$/ha)", value=100.0, step=10.0)
        outros = st.number_input("Outros custos, sem semente (R$/ha)", value=4000.0, step=100.0)

    with st.expander("🌾 Receita", expanded=True):
        produtividade = st.number_input("Produtividade esperada (sc/ha)", value=60.0, min_value=1.0, step=1.0)
        preco_saca = st.number_input("Preço da saca de soja (R$)", value=120.0, min_value=1.0, step=1.0)

# ---------- cálculos ----------
kg = kg_semente_ha(populacao, pms, germinacao, emergencia)
spm = sementes_por_metro(populacao, espacamento, germinacao, emergencia)
semente = custo_semente_ha(kg, preco_saco)
custo = custo_total_ha(outros, semente, royalties)
receita = receita_por_ha(produtividade, preco_saca)
margem = margem_por_ha(receita, custo)
pe = ponto_equilibrio(custo, preco_saca)
folga = folga_sobre_equilibrio(produtividade, pe)
preco_minimo = custo_por_saca(custo, produtividade)
margem_pct = margem / custo * 100

# ---------- cabeçalho ----------
st.markdown(
    f'<div class="hero"><h1>🌱 Agente CFO do Agro</h1>'
    f'<p>{cultivar} · {num(area, 0)} ha · Custo e ponto de equilíbrio da soja (valores iniciais são de exemplo)</p></div>',
    unsafe_allow_html=True)

# ---------- veredito ----------
if folga < 0:
    cor, fundo, titulo = "#E57373", "#3A1D1D", "Não vale a pena"
    texto = f"O ponto de equilíbrio ({num(pe)} sc/ha) está acima da produtividade esperada ({num(produtividade, 0)} sc/ha)."
elif folga < 15:
    cor, fundo, titulo = "#F4B942", "#3A2F14", "No limite"
    texto = f"Folga de só {num(folga, 0)}% sobre o ponto de equilíbrio. Uma queda pequena de preço ou produtividade pode dar prejuízo."
else:
    cor, fundo, titulo = "#66BB6A", "#14301D", "Vale a pena nas condições informadas"
    texto = f"Folga de {num(folga, 0)}% sobre o ponto de equilíbrio."

st.markdown(
    f'<div class="verdict" style="background:{fundo}; border:1px solid {cor};">'
    f'<h3 style="color:{cor};">{titulo}</h3><p>{texto}</p></div>',
    unsafe_allow_html=True)
st.progress(min(max(folga, 0), 100) / 100, text=f"Folga sobre o ponto de equilíbrio: {num(folga, 0)}%")

# ---------- indicadores por hectare ----------
st.subheader("Por hectare")
k1, k2, k3, k4 = st.columns(4)
k1.markdown(kpi("Custo total", brl(custo), f"Semente: {num(kg)} kg/ha", "ic-coin"), unsafe_allow_html=True)
k2.markdown(kpi("Margem", brl(margem), f"{num(margem_pct, 0)}% sobre o custo", "ic-chart"), unsafe_allow_html=True)
k3.markdown(kpi("Custo por saca", brl(preco_minimo), "Preço mínimo para não ter prejuízo", "ic-pod"), unsafe_allow_html=True)
k4.markdown(kpi("Ponto de equilíbrio", f"{num(pe)} sc/ha", f"{num(spm)} sementes por metro", "ic-scale"), unsafe_allow_html=True)

# ---------- totais da área ----------
st.subheader(f"Na área inteira ({num(area, 0)} ha)")
t1, t2, t3 = st.columns(3)
t1.markdown(kpi("Custo total", brl(custo * area), icone="ic-coin"), unsafe_allow_html=True)
t2.markdown(kpi("Receita total", brl(receita * area), icone="ic-chart"), unsafe_allow_html=True)
t3.markdown(kpi("Margem total", brl(margem * area), icone="ic-tractor"), unsafe_allow_html=True)

# ---------- gráficos ----------
g1, g2 = st.columns(2)

with g1:
    st.subheader("De onde vem o custo")
    df_custo = pd.DataFrame({"Item": ["Semente", "Royalties", "Outros custos"],
                             "Valor": [semente, royalties, outros]})
    rosca = alt.Chart(df_custo).mark_arc(innerRadius=70).encode(
        theta="Valor:Q",
        color=alt.Color("Item:N",
                        scale=alt.Scale(range=["#4CAF50", "#F4B942", "#5B8DEF"]),
                        legend=alt.Legend(orient="bottom", title=None)),
        tooltip=["Item", alt.Tooltip("Valor:Q", format=",.2f")],
    ).properties(height=320)
    st.altair_chart(rosca)

with g2:
    st.subheader("Margem conforme o preço da saca")
    precos = list(range(60, 161, 5))
    df_sens = pd.DataFrame({"Preco": precos,
                            "Margem": [produtividade * p - custo for p in precos]})
    linha = alt.Chart(df_sens).mark_line(color="#4CAF50", strokeWidth=3).encode(
        x=alt.X("Preco:Q", title="Preço da saca (R$)"),
        y=alt.Y("Margem:Q", title="Margem (R$/ha)"))
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(
        color="#E57373", strokeDash=[6, 4]).encode(y="y:Q")
    atual = alt.Chart(pd.DataFrame({"Preco": [preco_saca], "Margem": [margem]})).mark_point(
        size=140, filled=True, color="#F4B942").encode(x="Preco:Q", y="Margem:Q")
    st.altair_chart((linha + zero + atual).properties(height=320))
    st.caption(f"Abaixo de {brl(preco_minimo)} por saca há prejuízo. O ponto amarelo é o preço atual.")

# ---------- transparência ----------
with st.expander("Como o cálculo é feito"):
    st.markdown("""
- **Semente (kg/ha)** = população x peso de mil sementes / (1.000.000 x germinação x emergência)
- **Custo total** = semente + royalties + outros custos
- **Receita** = produtividade x preço da saca
- **Ponto de equilíbrio (sc/ha)** = custo por hectare / preço da saca
- **Veredito:** folga de 15% ou mais = vale a pena; entre 0% e 15% = no limite; abaixo de 0% = não vale a pena. O limite de 15% é um valor de exemplo.
""")

st.caption("Ferramenta de apoio à decisão. Não considera risco climático, custo da terra nem juros. Não substitui a análise de um agrônomo.")