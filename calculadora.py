from calculos import (kg_semente_ha, sementes_por_metro, custo_semente_ha,
                      custo_total_ha, receita_por_ha, margem_por_ha,
                      custo_por_saca, ponto_equilibrio)

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