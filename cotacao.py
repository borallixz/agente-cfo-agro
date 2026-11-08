"""Busca a cotação da soja (Bolsa de Chicago) e do dólar e converte para R$ por saca.

Cada informação tenta uma fonte e, se ela falhar, passa para a próxima.
Se todas falharem, a função devolve ok=False e o app usa o preço digitado.
"""
from datetime import datetime, timedelta, timezone

import requests

from calculos import preco_saca_da_bolsa

BRASILIA = timezone(timedelta(hours=-3))   # o Brasil não tem mais horário de verão
TIMEOUT = 6                                # segundos de espera por fonte
CABECALHO = {"User-Agent": "Mozilla/5.0 (compatible; AgenteCFOAgro/1.0)"}


def _yahoo(simbolo):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"
    resposta = requests.get(url, params={"range": "1d", "interval": "5m"},
                            headers=CABECALHO, timeout=TIMEOUT)
    resposta.raise_for_status()
    meta = resposta.json()["chart"]["result"][0]["meta"]
    preco = float(meta["regularMarketPrice"])
    hora = datetime.fromtimestamp(meta["regularMarketTime"], tz=BRASILIA)
    return preco, f"{hora:%d/%m %H:%M} Brasília", "Yahoo Finance"


def _soja_yahoo():
    preco, hora, fonte = _yahoo("ZS=F")
    if preco < 100:          # veio em dólares por bushel: converte para centavos
        preco *= 100
    return preco, hora, fonte


def _soja_stooq():
    url = "https://stooq.com/q/l/?s=zs.f&f=sd2t2c&h&e=csv"
    resposta = requests.get(url, headers=CABECALHO, timeout=TIMEOUT)
    resposta.raise_for_status()
    linhas = resposta.text.strip().splitlines()
    simbolo, data, hora, fechamento = linhas[1].split(",")[:4]
    preco = float(fechamento)
    dia = datetime.strptime(data, "%Y-%m-%d")
    return preco, f"{dia:%d/%m} {hora[:5]} (horário da fonte)", "Stooq"


def _dolar_yahoo():
    return _yahoo("BRL=X")


def _dolar_bcb():
    hoje = datetime.now(BRASILIA).date()
    inicio = hoje - timedelta(days=10)
    url = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
           "CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)")
    params = {
        "@dataInicial": f"'{inicio:%m-%d-%Y}'",
        "@dataFinalCotacao": f"'{hoje:%m-%d-%Y}'",
        "$top": "1",
        "$orderby": "dataHoraCotacao desc",
        "$select": "cotacaoVenda,dataHoraCotacao",
        "$format": "json",
    }
    resposta = requests.get(url, params=params, headers=CABECALHO, timeout=TIMEOUT)
    resposta.raise_for_status()
    item = resposta.json()["value"][0]
    preco = float(item["cotacaoVenda"])
    momento = datetime.strptime(item["dataHoraCotacao"][:19], "%Y-%m-%d %H:%M:%S")
    return preco, f"PTAX de {momento:%d/%m %H:%M}", "Banco Central"


def _primeira_que_funciona(tentativas, minimo, maximo, nome):
    erros = []
    for fonte, buscar in tentativas:
        try:
            preco, hora, nome_fonte = buscar()
            if minimo <= preco <= maximo:
                return preco, hora, nome_fonte
            erros.append(f"{fonte}: valor fora do esperado ({preco})")
        except Exception as erro:
            erros.append(f"{fonte}: {type(erro).__name__}")
    raise RuntimeError(f"{nome} indisponível ({'; '.join(erros)})")


def buscar_cotacao_soja():
    try:
        centavos, hora_soja, fonte_soja = _primeira_que_funciona(
            [("Yahoo Finance", _soja_yahoo), ("Stooq", _soja_stooq)],
            400, 3000, "Soja em Chicago")
        dolar, hora_dolar, fonte_dolar = _primeira_que_funciona(
            [("Yahoo Finance", _dolar_yahoo), ("Banco Central", _dolar_bcb)],
            2, 15, "Dólar")
    except Exception as erro:
        return {"ok": False, "erro": str(erro)}
    return {
        "ok": True,
        "preco_saca": preco_saca_da_bolsa(centavos, dolar),
        "centavos_bushel": centavos,
        "dolar": dolar,
        "fonte_soja": fonte_soja,
        "hora_soja": hora_soja,
        "fonte_dolar": fonte_dolar,
        "hora_dolar": hora_dolar,
    }
