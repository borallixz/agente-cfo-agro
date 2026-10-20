def kg_semente_ha(populacao_ha, pms_g, germinacao_pct, emergencia_pct):
    germinacao = germinacao_pct / 100
    emergencia = emergencia_pct / 100
    return (populacao_ha * pms_g) / (1_000_000 * germinacao * emergencia)

def sementes_por_metro(populacao_ha, espacamento_m, germinacao_pct, emergencia_pct=100):
    plantas_por_m = populacao_ha * espacamento_m / 10_000
    return plantas_por_m / ((germinacao_pct / 100) * (emergencia_pct / 100))

def custo_semente_ha(kg_ha, preco_saco, kg_saco=40):
    return kg_ha * (preco_saco / kg_saco)

def custo_total_ha(outros_custos_ha, semente_ha, royalties_ha):
    return outros_custos_ha + semente_ha + royalties_ha

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