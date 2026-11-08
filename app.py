import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

import calculos as c
from cotacao import buscar_cotacao_soja
from estilo import CSS

st.set_page_config(page_title="Agente CFO do Agro", page_icon="🌱", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

# estilos próprios dos blocos novos (não dependem do estilo.py)
st.markdown("""
<style>
.cfo-hero{padding:18px 4px 6px 4px}
.cfo-hero h1{margin:0;font-size:2rem}
.cfo-hero p{margin:4px 0 0 0;opacity:.75}
.cfo-card{background:#17271E;border:1px solid #2a4033;border-radius:14px;padding:14px 16px}
.cfo-card .t{font-size:.8rem;opacity:.7}
.cfo-card .v{font-size:1.5rem;font-weight:700}
.cfo-card .s{font-size:.75rem;opacity:.6}
.cfo-ver{border-radius:14px;padding:16px 18px;margin:12px 0;font-size:1.05rem;border:1px solid}
.cfo-ver.ok{background:#12301c;border-color:#4CAF50}
.cfo-ver.mid{background:#33290f;border-color:#E0B040}
.cfo-ver.bad{background:#35171a;border-color:#E05A5A}
.cfo-tick{display:flex;gap:18px;flex-wrap:wrap;align-items:center;background:#17271E;
 border:1px solid #2a4033;border-radius:14px;padding:12px 16px;margin:8px 0}
.cfo-tick .main{font-size:1.6rem;font-weight:700}
.cfo-tick .detail{font-size:.8rem;opacity:.7}
.cfo-tick .live{color:#4CAF50;font-weight:700}
.cfo-tick .off{color:#E0B040;font-weight:700}
</style>
""", unsafe_allow_html=True)

VERDE, AMARELO, VERMELHO = "#4CAF50", "#E0B040", "#E05A5A"
MARGEM_SEGURANCA = 15  # % — valor de exemplo, ajustar depois com dados reais


def _carregar_referencia():
    try:
        return json.loads((Path(__file__).parent / "custos_referencia.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


REF = _carregar_referencia()


def ref(chave, padrao):
    """Valor de referência do arquivo custos_referencia.json (ou o padrão, se faltar)."""
    item = REF.get(chave)
    return float(item["valor"]) if isinstance(item, dict) and "valor" in item else padrao


def reais(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def num(v, casas=1):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_data(ttl=300)
def cotacao_ao_vivo():
    return buscar_cotacao_soja()


def bloco_maquina(nome, chave, area_ha, exemplo):
    """Máquina própria (compra) ou alugada. Retorna R$/ha."""
    modo = st.radio(nome, ["Alugada", "Própria (comprada)"], key=f"{chave}_modo", horizontal=True)
    if modo == "Alugada":
        return st.number_input("Valor pago pelo aluguel (R$/ha)", 0.0, value=exemplo["aluguel"],
                               step=5.0, key=f"{chave}_aluguel")
    valor = st.number_input("Valor gasto na compra (R$)", 0.0, value=exemplo["valor"],
                            step=10000.0, key=f"{chave}_valor")
    vida = st.number_input("Vida útil (anos)", 1, 40, exemplo["vida"], key=f"{chave}_vida")
    uso = st.number_input("Área trabalhada por ano (ha)", 1.0, value=float(max(area_ha, 1.0)),
                          step=50.0, key=f"{chave}_uso")
    resid = st.number_input("Valor de revenda no fim (% da compra)", 0.0, 100.0, 20.0,
                            key=f"{chave}_resid")
    juros = st.number_input("Juros (% ao ano)", 0.0, 60.0, 10.0, key=f"{chave}_juros")
    oper = st.number_input("Combustível, manutenção e operador (R$/ha)", 0.0,
                           value=exemplo["oper"], step=5.0, key=f"{chave}_oper")
    return c.custo_maquina_propria_ha(valor, vida, uso, resid, juros, oper)


# ---------------- cabeçalho ----------------
st.markdown('<div class="cfo-hero"><h1>🌱 Agente CFO do Agro</h1>'
            '<p>Custo de produção e ponto de equilíbrio da soja, por hectare.</p></div>',
            unsafe_allow_html=True)

# ---------------- barra lateral ----------------
sb = st.sidebar
sb.header("Dados da lavoura")
area = sb.number_input("Área (ha)", 1.0, value=100.0, step=10.0)
prod = sb.number_input("Produtividade esperada (sc/ha)", 1.0, value=60.0, step=1.0)

with sb.expander("🌱 Semente", expanded=False):
    pop = st.number_input("População desejada (plantas/ha)", 100000, 600000, 280000, step=10000)
    pms = st.number_input("PMS – peso de mil sementes (g)", 80.0, 300.0, 160.0)
    germ = st.number_input("Germinação (%)", 40.0, 100.0, 85.0)
    emerg = st.number_input("Emergência em campo (%)", 40.0, 100.0, 85.0)
    esp = st.number_input("Espaçamento entre linhas (m)", 0.2, 1.0, 0.5)
    preco_saco = st.number_input("Preço do saco de 40 kg (R$)", 0.0, value=ref("preco_saco_semente", 480.0), step=10.0)
    royalties = st.number_input("Royalties / tecnologia (R$/ha)", 0.0, value=0.0, step=5.0)
    kg_ha = c.kg_semente_ha(pop, pms, germ, emerg)
    custo_sem = c.custo_semente_ha(kg_ha, preco_saco) + royalties
    st.caption(f"{num(kg_ha)} kg/ha · {num(c.sementes_por_metro(pop, esp, germ, emerg))} sementes/m")

with sb.expander("🧪 Adubo", expanded=False):
    n_fert = st.number_input("Quantidade de adubo (kg/ha)", 0.0, value=ref("adubo_kg_ha", 350.0), step=10.0)
    preco_t = st.number_input("Preço do adubo (R$/tonelada)", 0.0, value=ref("adubo_preco_t", 3200.0), step=100.0)
    calcario = st.number_input("Calcário / gesso (R$/ha)", 0.0, value=0.0, step=10.0)
    custo_adubo = c.custo_adubo_ha(n_fert, preco_t) + calcario

with sb.expander("🛡️ Defensivos", expanded=False):
    herb = st.number_input("Herbicidas (R$/ha)", 0.0, value=ref("herbicida", 180.0), step=10.0)
    inset = st.number_input("Inseticidas (R$/ha)", 0.0, value=ref("inseticida", 120.0), step=10.0)
    fung = st.number_input("Fungicidas (R$/ha)", 0.0, value=ref("fungicida", 300.0), step=10.0)
    outros_def = st.number_input("Outros (acaricida, adjuvante, tratamento de semente...) (R$/ha)",
                                 0.0, value=ref("outros_defensivos", 60.0), step=10.0)
    custo_def = herb + inset + fung + outros_def

with sb.expander("🚜 Máquinas", expanded=False):
    st.markdown("**Plantadeira**")
    maq_plant = bloco_maquina("Plantadeira", "plant", area,
                              {"aluguel": ref("aluguel_plantadeira", 120.0), "valor": 400000.0, "vida": 10, "oper": 60.0})
    st.markdown("**Pulverizador**")
    maq_pulv = bloco_maquina("Pulverizador", "pulv", area,
                             {"aluguel": ref("aluguel_pulverizador", 40.0), "valor": 600000.0, "vida": 10, "oper": 25.0})
    st.markdown("**Colhedora**")
    maq_colh = bloco_maquina("Colhedora", "colh", area,
                             {"aluguel": ref("aluguel_colhedora", 330.0), "valor": 1500000.0, "vida": 12, "oper": 120.0})
    custo_maq = maq_plant + maq_pulv + maq_colh

with sb.expander("🪨 Preparo do solo", expanded=False):
    dessec = st.number_input("Dessecação / manejo pré-plantio (R$/ha)", 0.0, value=ref("dessecacao", 60.0), step=5.0)
    operacoes = st.number_input("Operações de preparo (aração, gradagem, subsolagem) (R$/ha)",
                                0.0, value=0.0, step=10.0,
                                help="Em plantio direto pode ficar em zero.")
    custo_solo = dessec + operacoes

with sb.expander("💰 Outros custos", expanded=False):
    mao = st.number_input("Mão de obra (R$/ha)", 0.0, value=ref("mao_de_obra", 60.0), step=5.0)
    transp = st.number_input("Frete, armazenagem e secagem (R$/ha)", 0.0, value=ref("frete_armazenagem", 120.0), step=5.0)
    seguro = st.number_input("Seguro, assistência técnica e impostos (R$/ha)", 0.0, value=ref("seguro_assist_imp", 150.0), step=5.0)
    admin = st.number_input("Arrendamento e administração (R$/ha)", 0.0, value=0.0, step=10.0)
    custo_outros = mao + transp + seguro + admin

with sb.expander("⚠️ Risco e câmbio", expanded=False):
    cv = st.number_input("Variação da produtividade entre safras (CV, %)", 0.0, 60.0,
                         ref("cv_produtividade_pct", 15.0), step=1.0,
                         help="Coeficiente de variação = desvio padrão ÷ média das safras da sua região. "
                              "Ideal: calcular com a série histórica do IBGE (PAM) do seu município.")
    parte_dolar = st.number_input("Parte do custo ligada ao dólar (%)", 0.0, 100.0, 60.0, step=5.0,
                                  help="Adubo, defensivos e parte da semente e das máquinas "
                                       "costumam acompanhar o câmbio. Valor de exemplo.")

# ---------------- preço da soja ----------------
with sb.expander("🌾 Preço da soja", expanded=True):
    ao_vivo = st.toggle("Usar cotação em tempo real", value=True)
    cot = cotacao_ao_vivo() if ao_vivo else None
    preco_manual = st.number_input("Preço manual da saca (R$)", 0.0, value=130.0, step=1.0)
    ajuste = st.number_input("Prêmio/desconto da sua praça (R$/saca)", value=-15.0, step=1.0,
                             help="Chicago não é o preço da sua cidade. Use o prêmio/desconto para "
                                  "aproximar do preço pago na sua região (frete, porto, câmbio).")
    if st.button("Atualizar cotação agora"):
        cotacao_ao_vivo.clear()
        st.rerun()

if cot and cot["ok"]:
    preco = cot["preco_saca"] + ajuste
    fonte_txt = (f'<span class="live">● AO VIVO</span> · Chicago {num(cot["centavos_bushel"])} US¢/bu '
                 f'· dólar {num(cot["dolar"], 4)}')
    detalhe = (f'Soja: {cot["fonte_soja"]}, {cot["hora_soja"]} · Dólar: {cot["fonte_dolar"]}, '
               f'{cot["hora_dolar"]} · Chicago convertido: {reais(cot["preco_saca"])} '
               f'{"+" if ajuste >= 0 else "−"} {reais(abs(ajuste))} de ajuste')
else:
    preco = preco_manual
    if ao_vivo:
        fonte_txt = '<span class="off">● SEM COTAÇÃO — usando preço manual</span>'
        detalhe = (cot or {}).get("erro", "")
    else:
        fonte_txt = '<span class="off">● PREÇO MANUAL</span>'
        detalhe = "Cotação em tempo real desligada."

st.markdown(f'<div class="cfo-tick"><div><div class="detail">Preço usado no cálculo</div>'
            f'<div class="main">{reais(preco)} / saca</div></div>'
            f'<div><div>{fonte_txt}</div><div class="detail">{detalhe}</div></div></div>',
            unsafe_allow_html=True)

if preco <= 0:
    st.error("O preço da saca precisa ser maior que zero.")
    st.stop()

# ---------------- cálculos ----------------
grupos = {
    "Semente": custo_sem,
    "Adubo": custo_adubo,
    "Defensivos": custo_def,
    "Máquinas": custo_maq,
    "Preparo do solo": custo_solo,
    "Outros": custo_outros,
}
custo_ha = c.custo_total_ha(grupos)
receita = c.receita_por_ha(prod, preco)
margem = c.margem_por_ha(receita, custo_ha)
pe = c.ponto_equilibrio(custo_ha, preco)
folga = c.folga_sobre_equilibrio(prod, pe)
cps = c.custo_por_saca(custo_ha, prod)

if folga >= MARGEM_SEGURANCA:
    cls, msg = "ok", f"✅ Vale a pena: a produtividade esperada está {num(folga)}% acima do ponto de equilíbrio."
elif folga >= 0:
    cls, msg = "mid", f"⚠️ No limite: folga de só {num(folga)}% sobre o ponto de equilíbrio (referência: {MARGEM_SEGURANCA}%)."
else:
    cls, msg = "bad", f"❌ Não vale a pena: a produtividade esperada está {num(abs(folga))}% abaixo do ponto de equilíbrio."
st.markdown(f'<div class="cfo-ver {cls}">{msg}</div>', unsafe_allow_html=True)


def card(col, titulo, valor, sub=""):
    col.markdown(f'<div class="cfo-card"><div class="t">{titulo}</div>'
                 f'<div class="v">{valor}</div><div class="s">{sub}</div></div>',
                 unsafe_allow_html=True)


k = st.columns(5)
card(k[0], "Custo total", reais(custo_ha) + "/ha", f"{reais(custo_ha * area)} na área")
card(k[1], "Ponto de equilíbrio", f"{num(pe)} sc/ha", f"produtividade esperada: {num(prod)} sc/ha")
card(k[2], "Custo por saca", reais(cps), f"preço: {reais(preco)}")
card(k[3], "Preço de equilíbrio", reais(c.preco_equilibrio(custo_ha, prod)) + "/sc",
     f"com {num(prod)} sc/ha")
card(k[4], "Margem", reais(margem) + "/ha", f"{reais(margem * area)} na área")

# ---------------- gráfico do ponto de equilíbrio ----------------
st.subheader("Gráfico do ponto de equilíbrio")
x_max = max(prod, pe) * 1.4
pontos = pd.DataFrame({"prod": [0.0, x_max]})
pontos["Receita"] = pontos["prod"] * preco
pontos["Custo total"] = custo_ha
linhas = pontos.melt("prod", var_name="Linha", value_name="R$/ha")
cores = alt.Scale(domain=["Receita", "Custo total"], range=[VERDE, VERMELHO])

linhas_chart = alt.Chart(linhas).mark_line(strokeWidth=3).encode(
    x=alt.X("prod:Q", title="Produtividade (sc/ha)"),
    y=alt.Y("R$/ha:Q", title="R$ por hectare"),
    color=alt.Color("Linha:N", scale=cores, legend=alt.Legend(title=None, orient="top")),
)
ponto_pe = pd.DataFrame({"prod": [pe], "y": [custo_ha], "rotulo": [f"Equilíbrio: {num(pe)} sc/ha"]})
ponto_prod = pd.DataFrame({"prod": [prod], "y": [receita], "rotulo": [f"Esperado: {num(prod)} sc/ha"]})
marca_pe = alt.Chart(ponto_pe).mark_point(size=160, filled=True, color=AMARELO).encode(x="prod:Q", y="y:Q")
txt_pe = alt.Chart(ponto_pe).mark_text(dy=-16, color=AMARELO, fontWeight="bold").encode(
    x="prod:Q", y="y:Q", text="rotulo:N")
marca_pr = alt.Chart(ponto_prod).mark_point(size=160, filled=True, color="#FFFFFF").encode(x="prod:Q", y="y:Q")
txt_pr = alt.Chart(ponto_prod).mark_text(dy=-16, color="#FFFFFF").encode(
    x="prod:Q", y="y:Q", text="rotulo:N")
regra = alt.Chart(ponto_pe).mark_rule(strokeDash=[4, 4], color=AMARELO).encode(x="prod:Q")
st.altair_chart((linhas_chart + regra + marca_pe + txt_pe + marca_pr + txt_pr)
                .properties(height=360).configure_view(strokeWidth=0), use_container_width=True)
st.caption("Onde a linha verde (receita) cruza a vermelha (custo) é o ponto de equilíbrio: "
           "abaixo dessa produtividade, há prejuízo.")

# ---------------- mapa de calor produtividade x preço ----------------
st.subheader("Lucro ou prejuízo: produtividade × preço")
passos_prod = [prod * f for f in (0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2)]
passos_preco = [preco * f for f in (0.8, 0.9, 1.0, 1.1, 1.2)]
mapa = pd.DataFrame([
    {"Produtividade (sc/ha)": f"{p:.0f}", "Preço (R$/sc)": f"{q:.0f}",
     "Margem (R$/ha)": p * q - custo_ha, "_p": p, "_q": q}
    for p in passos_prod for q in passos_preco])
ordem_p = [f"{p:.0f}" for p in passos_prod]
ordem_q = [f"{q:.0f}" for q in reversed(passos_preco)]
teto = max(abs(mapa["Margem (R$/ha)"]).max(), 1)
base = alt.Chart(mapa).encode(
    x=alt.X("Produtividade (sc/ha):N", sort=ordem_p),
    y=alt.Y("Preço (R$/sc):N", sort=ordem_q))
calor = base.mark_rect().encode(
    color=alt.Color("Margem (R$/ha):Q", scale=alt.Scale(domain=[-teto, 0, teto],
                    range=[VERMELHO, "#2a3a30", VERDE]), legend=None),
    tooltip=["Produtividade (sc/ha)", "Preço (R$/sc)", alt.Tooltip("Margem (R$/ha):Q", format=",.0f")])
numeros = base.mark_text(color="white", fontSize=11).encode(
    text=alt.Text("Margem (R$/ha):Q", format=",.0f"))
st.altair_chart((calor + numeros).properties(height=260), use_container_width=True)
st.caption("Margem em R$/ha. Verde = lucro, vermelho = prejuízo. A coluna central e a linha "
           "central são os seus valores atuais.")

# ---------------- risco ----------------
st.subheader("Risco da safra")
p_abaixo = c.prob_abaixo_do_equilibrio(prod, cv, pe)
p10 = c.produtividade_percentil(prod, cv, 10)
p90 = c.produtividade_percentil(prod, cv, 90)
r = st.columns(3)
card(r[0], "Chance de ficar abaixo do equilíbrio", f"{num(p_abaixo)}%",
     f"com variação de {num(cv)}% entre safras")
card(r[1], "Safra ruim (1 a cada 10)", f"{num(p10)} sc/ha",
     f"margem: {reais(c.margem_por_ha(c.receita_por_ha(p10, preco), custo_ha))}/ha")
card(r[2], "Safra boa (1 a cada 10)", f"{num(p90)} sc/ha",
     f"margem: {reais(c.margem_por_ha(c.receita_por_ha(p90, preco), custo_ha))}/ha")
st.caption("Cálculo simplificado com distribuição normal. O CV padrão é um valor de exemplo: "
           "o ideal é usar a série histórica de produtividade do seu município.")

st.markdown("**E se o dólar mudar?** (afeta só a parte do custo ligada ao dólar; preço da soja mantido)")
linhas_cambio = []
for v in (-10, 0, 10, 20, 30):
    cc = c.custo_com_cambio(custo_ha, parte_dolar, v)
    linhas_cambio.append({"Dólar": f"{v:+d}%", "Custo (R$/ha)": round(cc, 2),
                          "Ponto de equilíbrio (sc/ha)": round(c.ponto_equilibrio(cc, preco), 1),
                          "Margem (R$/ha)": round(receita - cc, 2)})
st.dataframe(pd.DataFrame(linhas_cambio), hide_index=True, use_container_width=True)

# ---------------- composição e sensibilidade ----------------
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Para onde vai o custo")
    comp = pd.DataFrame({"Grupo": list(grupos), "R$/ha": list(grupos.values())})
    comp["%"] = comp["R$/ha"] / custo_ha * 100
    barras = alt.Chart(comp).mark_bar(color=VERDE).encode(
        y=alt.Y("Grupo:N", sort="-x", title=None),
        x=alt.X("R$/ha:Q", title="R$ por hectare"),
        tooltip=["Grupo", alt.Tooltip("R$/ha:Q", format=",.2f"), alt.Tooltip("%:Q", format=".1f")])
    st.altair_chart(barras.properties(height=300), use_container_width=True)

with col_b:
    st.subheader("E se o preço mudar?")
    variacoes = [-30, -20, -10, 0, 10, 20, 30]
    sens = pd.DataFrame({
        "Variação do preço": [f"{v:+d}%" for v in variacoes],
        "Margem (R$/ha)": [prod * preco * (1 + v / 100) - custo_ha for v in variacoes],
    })
    sens["Resultado"] = sens["Margem (R$/ha)"].apply(lambda m: "Lucro" if m >= 0 else "Prejuízo")
    graf = alt.Chart(sens).mark_bar().encode(
        x=alt.X("Variação do preço:N", sort=[f"{v:+d}%" for v in variacoes], title=None),
        y=alt.Y("Margem (R$/ha):Q"),
        color=alt.Color("Resultado:N", scale=alt.Scale(domain=["Lucro", "Prejuízo"],
                                                       range=[VERDE, VERMELHO]), legend=None),
        tooltip=["Variação do preço", alt.Tooltip("Margem (R$/ha):Q", format=",.2f")])
    st.altair_chart(graf.properties(height=300), use_container_width=True)

# ---------------- tabela e explicação ----------------
st.subheader("Detalhamento dos custos")
tabela = comp.copy()
tabela["Total na área (R$)"] = tabela["R$/ha"] * area
tabela["R$/ha"] = tabela["R$/ha"].round(2)
tabela["%"] = tabela["%"].round(1)
tabela["Total na área (R$)"] = tabela["Total na área (R$)"].round(2)
st.dataframe(tabela, hide_index=True, use_container_width=True)

with st.expander("📐 Como cada número é calculado"):
    st.markdown(f"""
- **Semente (kg/ha)** = população × PMS ÷ (1.000.000 × germinação × emergência) → {num(kg_ha)} kg/ha
- **Adubo (R$/ha)** = kg/ha × preço da tonelada ÷ 1000
- **Máquina própria (R$/ha)** = depreciação (compra × (1 − revenda) ÷ (vida útil × ha/ano))
  + juros sobre o capital médio ÷ ha/ano + operação. **Alugada** = valor pago por hectare.
- **Preço da saca (tempo real)** = US¢/bushel ÷ 100 × (60 ÷ 27,2155) × dólar + ajuste da praça
- **Ponto de equilíbrio (sc/ha)** = custo total/ha ÷ preço da saca → {num(pe)} sc/ha
- **Preço de equilíbrio** = custo total/ha ÷ produtividade esperada → {reais(c.preco_equilibrio(custo_ha, prod))}/sc
- **Chance abaixo do equilíbrio** = probabilidade de a safra render menos que o equilíbrio, supondo
  distribuição normal com desvio = CV × produtividade → {num(p_abaixo)}%
- **Folga** = (produtividade − equilíbrio) ÷ produtividade → {num(folga)}%
- **Veredito**: ≥ {MARGEM_SEGURANCA}% vale a pena · 0 a {MARGEM_SEGURANCA}% no limite · abaixo de 0 não vale
  (os {MARGEM_SEGURANCA}% são um valor de exemplo).

Os valores iniciais vêm do arquivo `custos_referencia.json` (exemplos, não oficiais): troque pelos da sua propriedade e registre a fonte.
A cotação ao vivo é de **Chicago**, não da sua praça; use o campo de prêmio/desconto para aproximar.
""")
