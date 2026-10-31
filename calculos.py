"""Cálculos por hectare. Indicadores sem denominador econômico retornam None."""
import math
from numbers import Real


# Envelope operacional: rejeição explícita, nunca truncamento ou substituição.
MIN_ENTRADA = 1e-9
MAX_ENTRADA = 1e12
MAX_RESULTADO = 1e18


def validar_numero(valor, nome, *, positivo=False, percentual=False,
                   minimo=MIN_ENTRADA, maximo=MAX_ENTRADA):
    try:
        finito = isinstance(valor, Real) and not isinstance(valor, bool) and math.isfinite(valor)
    except OverflowError:
        raise ValueError(f"{nome}: número grande demais para o intervalo suportado.") from None
    if not finito:
        raise ValueError(f"{nome}: informe um número finito.")
    if valor < 0 or (positivo and valor == 0):
        limite = "maior que zero" if positivo else "maior ou igual a zero"
        raise ValueError(f"{nome}: o valor deve ser {limite}.")
    if percentual and valor > 100:
        raise ValueError(f"{nome}: o percentual não pode ultrapassar 100%.")
    if valor > maximo or (valor != 0 and abs(valor) < minimo):
        raise ValueError(f"{nome}: use zero quando permitido ou valores entre {minimo:g} e {maximo:g}.")
    return valor


def _resultado(valor):
    if not math.isfinite(valor) or abs(valor) > MAX_RESULTADO:
        raise ValueError("Resultado fora do intervalo numérico suportado; revise os valores informados.")
    return valor


def kg_semente_ha(populacao_ha, pms_g, germinacao_pct, emergencia_pct):
    for nome, valor in (("População", populacao_ha), ("PMS", pms_g)):
        validar_numero(valor, nome, positivo=True)
    for nome, valor in (("Germinação", germinacao_pct), ("Emergência", emergencia_pct)):
        validar_numero(valor, nome, positivo=True, percentual=True)
    denominador = 1_000_000 * (germinacao_pct / 100) * (emergencia_pct / 100)
    if denominador == 0:
        raise ValueError("Percentuais pequenos demais para o intervalo numérico suportado.")
    return _resultado((populacao_ha * pms_g) / denominador)


def sementes_por_metro(populacao_ha, espacamento_m, germinacao_pct, emergencia_pct=100):
    validar_numero(populacao_ha, "População", positivo=True)
    validar_numero(espacamento_m, "Espaçamento", positivo=True)
    validar_numero(germinacao_pct, "Germinação", positivo=True, percentual=True)
    validar_numero(emergencia_pct, "Emergência", positivo=True, percentual=True)
    denominador = (germinacao_pct / 100) * (emergencia_pct / 100)
    if denominador == 0:
        raise ValueError("Percentuais pequenos demais para o intervalo numérico suportado.")
    return _resultado((populacao_ha * espacamento_m / 10_000) / denominador)


def custo_semente_ha(kg_ha, preco_saco, kg_saco=40):
    validar_numero(kg_ha, "Semente (kg/ha)")
    validar_numero(preco_saco, "Preço do saco")
    validar_numero(kg_saco, "Peso do saco", positivo=True)
    return _resultado(kg_ha * (preco_saco / kg_saco))


def custo_total_ha(outros_custos_ha, semente_ha, royalties_ha):
    for nome, valor in (("Outros custos", outros_custos_ha), ("Semente", semente_ha), ("Royalties", royalties_ha)):
        validar_numero(valor, nome)
    return _resultado(outros_custos_ha + semente_ha + royalties_ha)


def receita_por_ha(produtividade_sc_ha, preco_saca):
    validar_numero(produtividade_sc_ha, "Produtividade")
    validar_numero(preco_saca, "Preço da saca")
    return _resultado(produtividade_sc_ha * preco_saca)


def margem_por_ha(receita_ha, custo_ha):
    validar_numero(receita_ha, "Receita")
    validar_numero(custo_ha, "Custo")
    return _resultado(receita_ha - custo_ha)


def custo_por_saca(custo_ha, produtividade_sc_ha):
    validar_numero(custo_ha, "Custo")
    validar_numero(produtividade_sc_ha, "Produtividade")
    return None if produtividade_sc_ha == 0 else _resultado(custo_ha / produtividade_sc_ha)


def ponto_equilibrio(custo_ha, preco_saca):
    """Preço zero não permite determinar equilíbrio por divisão, inclusive com custo zero."""
    validar_numero(custo_ha, "Custo")
    validar_numero(preco_saca, "Preço da saca")
    return None if preco_saca == 0 else _resultado(custo_ha / preco_saca)


def folga_sobre_equilibrio(produtividade_sc_ha, ponto_eq):
    validar_numero(produtividade_sc_ha, "Produtividade")
    if ponto_eq is None:
        return None  # Ausência explícita de um ponto de equilíbrio calculável.
    validar_numero(ponto_eq, "Ponto de equilíbrio")
    return None if produtividade_sc_ha == 0 else _resultado((produtividade_sc_ha - ponto_eq) / produtividade_sc_ha * 100)


def retorno_sobre_custo(receita_ha, custo_ha):
    margem = margem_por_ha(receita_ha, custo_ha)
    return None if custo_ha == 0 else _resultado(margem / custo_ha * 100)
