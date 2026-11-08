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
