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

# valores de exemplo (só para testar)
cultivar = {
    "nome": "Cultivar exemplo",
    "produtividade": 60,
    "populacao_ha": 260_000,
    "pms_g": 150,
    "germinacao_pct": 70,
    "emergencia_pct": 100,
    "espacamento_m": 0.45,
    "preco_saco": 280,
    "royalties_ha": 100,
}
outros_custos_ha = 4000
preco_saca = 120

kg = kg_semente_ha(cultivar["populacao_ha"], cultivar["pms_g"],
                   cultivar["germinacao_pct"], cultivar["emergencia_pct"])
spm = sementes_por_metro(cultivar["populacao_ha"], cultivar["espacamento_m"],
                         cultivar["germinacao_pct"], cultivar["emergencia_pct"])
semente = custo_semente_ha(kg, cultivar["preco_saco"])
custo = custo_total_ha(outros_custos_ha, semente, cultivar["royalties_ha"])
receita = receita_por_ha(cultivar["produtividade"], preco_saca)

print("Cultivar:", cultivar["nome"])
print(f"Semente necessária: {kg:.1f} kg/ha")
print(f"Sementes por metro: {spm:.1f}")
print(f"Custo da semente: R$ {semente:.2f}/ha")
print(f"Custo total: R$ {custo:.2f}/ha")
print(f"Receita: R$ {receita:.2f}/ha")
print(f"Margem: R$ {margem_por_ha(receita, custo):.2f}/ha")
print(f"Custo por saca: R$ {custo_por_saca(custo, cultivar['produtividade']):.2f}")
print(f"Ponto de equilíbrio: {ponto_equilibrio(custo, preco_saca):.1f} sc/ha")