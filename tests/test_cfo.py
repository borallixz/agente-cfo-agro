from pathlib import Path
import itertools
import re
import math
import unittest
from unittest.mock import patch
import streamlit as st
from streamlit.testing.v1 import AppTest
import calculos as c


class CalculosTest(unittest.TestCase):
    cases = [
        (c.kg_semente_ha, [200000, 150, 80, 100], 37.5),
        (c.sementes_por_metro, [200000, .5, 80, 100], 12.5),
        (c.custo_semente_ha, [40, 280, 40], 280),
        (c.custo_total_ha, [4000, 280, 100], 4380),
        (c.receita_por_ha, [60, 120], 7200),
        (c.margem_por_ha, [7200, 4380], 2820),
        (c.custo_por_saca, [4380, 60], 73),
        (c.ponto_equilibrio, [4380, 120], 36.5),
        (c.folga_sobre_equilibrio, [60, 36.5], 39.1666666667),
        (c.retorno_sobre_custo, [7200, 4380], 64.3835616438),
    ]

    def test_formulas_preservadas(self):
        for fn, args, expected in self.cases:
            with self.subTest(fn=fn.__name__):
                self.assertAlmostEqual(fn(*args), expected)

    def test_rejeita_invalidos_em_todos_os_argumentos(self):
        for fn, args, _ in self.cases:
            for i in range(len(args)):
                for invalid in [-1, math.nan, math.inf, -math.inf, None, True, '10']:
                    with self.subTest(fn=fn.__name__, arg=i, value=invalid):
                        values = args.copy()
                        values[i] = invalid
                        # None é o marcador explícito de equilíbrio indisponível.
                        if fn is c.folga_sobre_equilibrio and i == 1 and invalid is None:
                            self.assertIsNone(fn(*values))
                        else:
                            with self.assertRaises(ValueError):
                                fn(*values)

    def test_parametros_fisicos_e_percentuais(self):
        for fn, args in [(c.kg_semente_ha, [0, 150, 80, 100]),
                         (c.kg_semente_ha, [200000, 0, 80, 100]),
                         (c.kg_semente_ha, [200000, 150, 0, 100]),
                         (c.kg_semente_ha, [200000, 150, 101, 100]),
                         (c.sementes_por_metro, [200000, 0, 80, 100]),
                         (c.sementes_por_metro, [200000, .5, 80, 101]),
                         (c.custo_semente_ha, [40, 280, 0])]:
            with self.subTest(fn=fn.__name__, args=args), self.assertRaises(ValueError):
                fn(*args)

    def test_zeros_e_prejuizo(self):
        self.assertEqual(c.receita_por_ha(0, 120), 0)
        self.assertEqual(c.receita_por_ha(60, 0), 0)
        self.assertEqual(c.margem_por_ha(0, 4000), -4000)
        self.assertEqual(c.custo_total_ha(0, 0, 0), 0)
        self.assertEqual(c.custo_semente_ha(40, 0), 0)
        self.assertEqual(c.custo_por_saca(0, 60), 0)
        self.assertEqual(c.ponto_equilibrio(0, 120), 0)
        for cost in [0, 4000]:
            self.assertIsNone(c.custo_por_saca(cost, 0))
            self.assertIsNone(c.ponto_equilibrio(cost, 0))
            self.assertIsNone(c.retorno_sobre_custo(cost, 0))
        self.assertIsNone(c.folga_sobre_equilibrio(0, 40))
        self.assertIsNone(c.folga_sobre_equilibrio(60, None))

    def test_overflow_e_custo_extremo_finito(self):
        for fn, args in [(c.receita_por_ha, [1e308, 120]),
                         (c.kg_semente_ha, [1e308, 150, 80, 100]),
                         (c.custo_total_ha, [1e308, 1e308, 0])]:
            with self.subTest(fn=fn.__name__), self.assertRaises(ValueError):
                fn(*args)
        self.assertEqual(c.margem_por_ha(7200, 1e12), -999999992800)

    def test_limites_numericos_e_inteiros_enormes(self):
        for fn, args, _ in self.cases:
            for i in range(len(args)):
                for invalid in [10**1000, 1e-200, math.nextafter(c.MAX_ENTRADA, math.inf)]:
                    values = args.copy()
                    values[i] = invalid
                    with self.subTest(fn=fn.__name__, arg=i, value=str(invalid)[:20]):
                        with self.assertRaises(ValueError):
                            fn(*values)
        self.assertEqual(c.validar_numero(c.MIN_ENTRADA, 'Teste'), c.MIN_ENTRADA)
        self.assertEqual(c.validar_numero(c.MAX_ENTRADA, 'Teste'), c.MAX_ENTRADA)
        self.assertEqual(c.receita_por_ha(1e9, 1e9), c.MAX_RESULTADO)
        with self.assertRaises(ValueError):
            c.receita_por_ha(1e10, 1e10)
        with self.assertRaisesRegex(ValueError, 'grande demais'):
            c.validar_numero(10**1000, 'Teste')

    def test_percentuais_fisicos_fronteiras(self):
        for pct in [c.MIN_ENTRADA, math.nextafter(c.MIN_ENTRADA, math.inf), 0.001, 100.]:
            for germ, emerg in [(pct, 100.), (100., pct)]:
                with self.subTest(germ=germ, emerg=emerg):
                    self.assertAlmostEqual(c.kg_semente_ha(1, 1, germ, emerg), 1 / (1e6 * germ/100 * emerg/100))
                    self.assertAlmostEqual(c.sementes_por_metro(1, 1, germ, emerg), 1 / (1e4 * germ/100 * emerg/100))
        for pct in [0., math.nextafter(c.MIN_ENTRADA, 0.), math.nextafter(100., math.inf)]:
            for args in [(1, 1, pct, 100.), (1, 1, 100., pct)]:
                for fn in [c.kg_semente_ha, c.sementes_por_metro]:
                    with self.subTest(fn=fn.__name__, args=args), self.assertRaises(ValueError):
                        fn(*args)


class InterfaceTest(unittest.TestCase):
    def run_case(self, changes):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=30)
        for label, value in changes.items():
            next(n for n in at.number_input if n.label == label).set_value(value)
        at.run(timeout=30)
        self.assertFalse(at.exception)
        return at

    def test_lucro_e_prejuizo(self):
        for price, verdict in [(120., 'Vale a pena nas condições informadas'), (60., 'Não vale a pena')]:
            at = self.run_case({'Preço da saca de soja (R$)': price})
            self.assertTrue(any(verdict in m.value for m in at.markdown))

    def test_zero_economico(self):
        scenarios = [
            {'Preço do saco de 40 kg (R$)': 0., 'Royalties (R$/ha)': 0., 'Outros custos, sem semente (R$/ha)': 0.},
            {'Produtividade esperada (sc/ha)': 0.},
            {'Preço da saca de soja (R$)': 0.},
            {'Produtividade esperada (sc/ha)': 0., 'Preço da saca de soja (R$)': 0., 'Preço do saco de 40 kg (R$)': 0., 'Royalties (R$/ha)': 0., 'Outros custos, sem semente (R$/ha)': 0.},
        ]
        for changes in scenarios:
            with self.subTest(changes=changes):
                at = self.run_case(changes)
                self.assertTrue(at.info)
                for label, value in changes.items():
                    self.assertEqual(next(n.value for n in at.number_input if n.label == label), value)
                if changes.get('Produtividade esperada (sc/ha)') == 0 or changes.get('Preço da saca de soja (R$)') == 0:
                    self.assertFalse(any('Vale a pena nas condições informadas' in m.value for m in at.markdown))

    def test_invalidos_bloqueiam_resultados(self):
        for label, value in [('Outros custos, sem semente (R$/ha)', -5000.),
                             ('População (plantas/ha)', -260000.),
                             ('Espaçamento (m)', 0.), ('Área (ha)', 0.),
                             ('Germinação (%)', 101.), ('Emergência em campo (%)', 0.),
                             ('Peso de mil sementes (g)', 0.),
                             ('População (plantas/ha)', 1e308),
                             ('Área (ha)', 1e308)]:
            with self.subTest(label=label, value=value):
                at = self.run_case({label: value})
                self.assertTrue(at.error)
                self.assertFalse(any('class="verdict"' in m.value or 'class="kpi ' in m.value for m in at.markdown))

    def test_nao_finitos_na_fronteira_da_interface(self):
        # O protocolo dos widgets não transporta NaN/inf de modo fiel.
        # Injete o valor retornado pelo widget para exercitar a validação do app.
        original = st.number_input
        for invalid in [math.nan, math.inf, -math.inf, None]:
            def entrada(label, *args, **kwargs):
                value = original(label, *args, **kwargs)
                return invalid if label == 'Preço da saca de soja (R$)' else value
            with self.subTest(value=invalid), patch('streamlit.number_input', side_effect=entrada):
                at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
                self.assertFalse(at.exception)
                self.assertTrue(at.error)
                self.assertFalse(any('class="verdict"' in m.value for m in at.markdown))

    @staticmethod
    def dinheiro(value):
        return 'R$ ' + f'{value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    def test_oito_combinacoes_e_indicadores(self):
        for cost, q, price in itertools.product([0., 4000.], [0., 60.], [0., 120.]):
            with self.subTest(cost=cost, q=q, price=price):
                at = self.run_case({'Preço do saco de 40 kg (R$)': 0., 'Royalties (R$/ha)': 0.,
                    'Outros custos, sem semente (R$/ha)': cost,
                    'Produtividade esperada (sc/ha)': q, 'Preço da saca de soja (R$)': price})
                self.assertFalse(at.error)
                cards = [m.value for m in at.markdown if 'class="kpi ' in m.value]
                values = [re.search(r'<div class="value">(.*?)</div>', card).group(1) for card in cards]
                revenue, margin = q * price, q * price - cost
                pe = cost / price if price else None
                per_sack = cost / q if q else None
                self.assertEqual(values, [self.dinheiro(cost), self.dinheiro(margin),
                    self.dinheiro(per_sack) if per_sack is not None else 'Indefinido',
                    f'{pe:.1f}'.replace('.', ',') + ' sc/ha' if pe is not None else 'Indefinido',
                    self.dinheiro(cost * 100), self.dinheiro(revenue * 100), self.dinheiro(margin * 100)])
                infos = '\n'.join(info.value for info in at.info)
                self.assertEqual('Retorno percentual sobre custo indefinido' in infos, cost == 0)
                self.assertEqual('Custo por saca indefinido' in infos, q == 0)
                self.assertEqual('Ponto de equilíbrio indefinido' in infos, price == 0)
                self.assertEqual('Folga indefinida' in infos, q == 0 or price == 0)
                if cost:
                    pct = margin / cost * 100
                    self.assertIn(f'{pct:.0f}% sobre o custo', cards[1])
                else:
                    self.assertIn('Retorno sobre custo indefinido', cards[1])
                if q and price:
                    folga = (q - pe) / q * 100
                    self.assertEqual(len(at.progress), 1)
                    expected = 'Não vale a pena' if folga < 0 else ('No limite' if folga < 15 else 'Vale a pena nas condições informadas')
                else:
                    self.assertEqual(len(at.progress), 0)
                    expected = 'Não vale a pena' if margin < 0 else 'Sem veredito pela folga'
                verdict = next(m.value for m in at.markdown if 'class="verdict"' in m.value)
                self.assertIn(expected, verdict)

    def test_limites_do_veredito(self):
        # nextafter exercita os vizinhos representáveis dos custos dos limites.
        for boundary, central in [(0., 10000.), (15., 8500.)]:
            for cost in [math.nextafter(central, math.inf), central, math.nextafter(central, 0.)]:
                with self.subTest(boundary=boundary, cost=cost):
                    folga = c.folga_sobre_equilibrio(100., cost / 100.)
                    if cost == central:
                        self.assertEqual(folga, boundary)
                    elif cost > central:
                        self.assertLess(folga, boundary)
                    else:
                        self.assertGreater(folga, boundary)
                    at = self.run_case({'Preço do saco de 40 kg (R$)': 0., 'Royalties (R$/ha)': 0.,
                        'Outros custos, sem semente (R$/ha)': cost,
                        'Produtividade esperada (sc/ha)': 100., 'Preço da saca de soja (R$)': 100.})
                    self.assertFalse(at.error)
                    verdict = next(m.value for m in at.markdown if 'class="verdict"' in m.value)
                    expected = 'Não vale a pena' if folga < 0 else ('No limite' if folga < 15 else 'Vale a pena nas condições informadas')
                    self.assertIn(expected, verdict)

    def test_recuperacao_do_formulario(self):
        at = self.run_case({'Outros custos, sem semente (R$/ha)': -1.})
        self.assertTrue(at.error)
        next(n for n in at.number_input if n.label == 'Outros custos, sem semente (R$/ha)').set_value(4000.)
        at.run()
        self.assertFalse(at.error)
        self.assertFalse(at.exception)
        self.assertTrue(any('Vale a pena nas condições informadas' in m.value for m in at.markdown))
        self.assertEqual(len([m for m in at.markdown if 'class="kpi ' in m.value]), 7)

    def test_limites_numericos_na_interface(self):
        for value in [1e-200, math.nextafter(c.MAX_ENTRADA, math.inf)]:
            at = self.run_case({'Preço da saca de soja (R$)': value})
            self.assertTrue(at.error)
            self.assertFalse(any('class="verdict"' in m.value for m in at.markdown))
        for value in [c.MIN_ENTRADA, 100.]:
            at = self.run_case({'População (plantas/ha)': 1., 'Peso de mil sementes (g)': 1.,
                'Germinação (%)': value, 'Emergência em campo (%)': 100., 'Preço do saco de 40 kg (R$)': 0.})
            self.assertFalse(at.error)

    def test_totais_tem_limite_proprio(self):
        base = {'Área (ha)': 1e9, 'Preço do saco de 40 kg (R$)': 0.,
                'Royalties (R$/ha)': 0., 'Outros custos, sem semente (R$/ha)': 1e9,
                'Produtividade esperada (sc/ha)': 0., 'Preço da saca de soja (R$)': 0.}
        at = self.run_case(base)
        self.assertFalse(at.error)
        cards = [m.value for m in at.markdown if 'class="kpi ' in m.value]
        self.assertIn(self.dinheiro(1e18), cards[4])
        self.assertIn(self.dinheiro(-1e18), cards[6])
        at = self.run_case(dict(base, **{'Área (ha)': 1e12}))
        self.assertTrue(at.error)
        self.assertFalse(any('class="verdict"' in m.value for m in at.markdown))


if __name__ == '__main__':
    unittest.main()
