"""Testes da camada de dados. Executar: python -m unittest discover -s app -p 'test_*.py'."""

import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from data import producao_por_hectare


class ProducaoPorHectareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raiz = Path(__file__).resolve().parent.parent
        cls.pam = pd.read_csv(
            raiz / "dados" / "processed" / "pam_tratado.csv",
            dtype={"territorio_codigo": "string", "variavel_codigo": "string", "produto_codigo": "string"},
        )
        # A coluna `variavel` (slug) é criada por load_pam; reproduzimos aqui para o teste isolado.
        mapa = {"8331": "area_plantada", "216": "area_colhida", "214": "quantidade", "112": "rendimento", "215": "valor_producao"}
        cls.pam["variavel"] = cls.pam["variavel_codigo"].map(mapa)

    def test_referencias_e_lider(self):
        base = producao_por_hectare(self.pam)
        self.assertEqual(len(base), 22 * 7)
        idx = base.set_index(["ano_codigo", "produto_nome"])
        for chave, esperado, tol in [
            ((2003, "Melão"), 12217, 1),
            ((2024, "Melão"), 44098, 1),
            ((2024, "Banana (cacho)"), 24092, 1),
            ((2024, "Milho (em grão)"), 799, 1),
        ]:
            self.assertAlmostEqual(idx.loc[chave, "valor_por_ha_rs"], esperado, delta=tol)
        lideres = base.loc[base.groupby("ano_codigo").valor_por_ha_rs.idxmax(), "produto_nome"]
        self.assertEqual(set(lideres), {"Melão"})

    def test_isolamento_territorial_e_invalidos(self):
        esperado = producao_por_hectare(self.pam)
        dados = self.pam.copy()
        fora = ~(dados["territorio_codigo"] == "23")
        dados.loc[fora, "valor"] = 999_999_999
        pd.testing.assert_frame_equal(producao_por_hectare(dados), esperado)
        estado_melao = dados["territorio_codigo"].eq("23") & dados["produto_nome"].eq("Melão")
        dados.loc[estado_melao & dados["ano_codigo"].eq(2003) & dados["variavel"].eq("area_colhida"), "valor"] = 0
        resultado = producao_por_hectare(dados).set_index(["ano_codigo", "produto_nome"])
        self.assertTrue(pd.isna(resultado.loc[(2003, "Melão"), "valor_por_ha_rs"]))
        self.assertFalse(np.isinf(resultado["valor_por_ha_rs"]).any())


if __name__ == "__main__":
    unittest.main()
