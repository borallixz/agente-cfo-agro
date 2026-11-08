# ---------- semente ----------
def kg_semente_ha(populacao_ha, pms_g, germinacao_pct, emergencia_pct):
    # PMS = peso de mil sementes (g). Resultado em kg/ha.
    germinacao = germinacao_pct / 100
    emergencia = emergencia_pct / 100
    return (populacao_ha * pms_g) / (1_000_000 * germinacao * emergencia)


def sementes_por_metro(populacao_ha, espacamento_m, germinacao_pct, emergencia_pct=100):
    plantas_por_m = populacao_ha * espacamento_m / 10_000
    return plantas_por_m / ((germinacao_pct / 100) * (emergencia_pct / 100))


def custo_semente_ha(kg_ha, preco_saco, kg_saco=40):
    return kg_ha * (preco_saco / kg_saco)


# ---------- adubo ----------
def custo_adubo_ha(kg_ha, preco_tonelada):
    # o adubo é vendido por tonelada (1 t = 1000 kg)
    return kg_ha * preco_tonelada / 1000


# ---------- máquinas ----------
def custo_maquina_propria_ha(valor_compra, vida_util_anos, uso_anual_ha,
                             residual_pct, juros_aa_pct, operacao_ha):
    # depreciação linear: quanto a máquina perde de valor por hectare trabalhado
    depreciacao = valor_compra * (1 - residual_pct / 100) / (vida_util_anos * uso_anual_ha)
    # juros sobre o capital médio parado na máquina (valor de compra e valor final, em média)
    capital_medio = valor_compra * (1 + residual_pct / 100) / 2
    juros = capital_medio * (juros_aa_pct / 100) / uso_anual_ha
    # operação = combustível, manutenção e operador, informados por hectare
    return depreciacao + juros + operacao_ha


# ---------- totais e indicadores ----------
def custo_total_ha(itens):
    # itens: dicionário {nome do grupo: R$/ha}
    return sum(itens.values())


def receita_por_ha(produtividade_sc_ha, preco_saca):
    return produtividade_sc_ha * preco_saca


def margem_por_ha(receita_ha, custo_ha):
    return receita_ha - custo_ha


def custo_por_saca(custo_ha, produtividade_sc_ha):
    return custo_ha / produtividade_sc_ha


def ponto_equilibrio(custo_ha, preco_saca):
    return custo_ha / preco_saca


def folga_sobre_equilibrio(produtividade_sc_ha, ponto_eq):
    # % que a produtividade esperada está acima do ponto de equilíbrio
    return (produtividade_sc_ha - ponto_eq) / produtividade_sc_ha * 100


# ---------- preço da soja ----------
KG_POR_BUSHEL_SOJA = 27.2155   # 1 bushel de soja = 27,2155 kg
KG_POR_SACA = 60


def preco_saca_da_bolsa(centavos_por_bushel, dolar_em_reais):
    # Cotação de Chicago (US$ cents por bushel) convertida para R$ por saca de 60 kg
    dolares_por_bushel = centavos_por_bushel / 100
    bushels_por_saca = KG_POR_SACA / KG_POR_BUSHEL_SOJA
    return dolares_por_bushel * bushels_por_saca * dolar_em_reais


# ---------- preço de equilíbrio, risco e câmbio ----------
def preco_equilibrio(custo_ha, produtividade_sc_ha):
    # preço mínimo da saca para empatar com a produtividade esperada
    return custo_ha / produtividade_sc_ha


def distribuicao_produtividade(media_sc_ha, cv_pct):
    # desvio padrão a partir do coeficiente de variação (CV = desvio / média)
    from statistics import NormalDist
    return NormalDist(media_sc_ha, media_sc_ha * cv_pct / 100)


def prob_abaixo_do_equilibrio(media_sc_ha, cv_pct, ponto_eq):
    # chance de a safra render menos que o ponto de equilíbrio (distribuição normal)
    if cv_pct <= 0:
        return 100.0 if media_sc_ha < ponto_eq else 0.0
    return distribuicao_produtividade(media_sc_ha, cv_pct).cdf(ponto_eq) * 100


def produtividade_percentil(media_sc_ha, cv_pct, percentil):
    # ex.: percentil 10 = produtividade que só é superada em 90% das safras
    if cv_pct <= 0:
        return media_sc_ha
    return max(0.0, distribuicao_produtividade(media_sc_ha, cv_pct).inv_cdf(percentil / 100))


def custo_com_cambio(custo_ha, parte_em_dolar_pct, variacao_dolar_pct):
    # parte do custo (adubo, defensivos, semente...) acompanha o dólar
    return custo_ha * (1 + parte_em_dolar_pct / 100 * variacao_dolar_pct / 100)
