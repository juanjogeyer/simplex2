import unittest
from services import resolver_simplex_tabular 
from fastapi.testclient import TestClient
from routers.simplex import router

class TestSimplexTabular(unittest.TestCase):

    def test_basico_correcto(self):
        """
        Caso básico 
            Max Z = 3x1 + 5x2
            1x1 <= 4
            2x2 <= 12
            3x1 + 2x2 <= 18
            Solución: x1=2, x2=6, Z=36
        """
        res = resolver_simplex_tabular(
            "maximization",
            [3, 5],
            [[1, 0], [0, 2], [3, 2]],
            [4, 12, 18],
            ["<=", "<=", "<="]
        )
        self.assertEqual(res["status"], "optimo")
        self.assertAlmostEqual(res["solucion"]["valor_optimo"], 36, places=3)
        self.assertAlmostEqual(res["solucion"]["variables"]["x1"], 2, places=3)
        self.assertAlmostEqual(res["solucion"]["variables"]["x2"], 6, places=3)

    def test_sin_solucion_infactible(self):

        """
        Caso sin solución factible
            Max Z = 2x1 + 3x2
            1x1 + 1x2 <= 2  (x1+x2 no puede ser <= 2 y >= 5)
            1x1 + 1x2 >= 5
        """
        res = resolver_simplex_tabular(
            "maximization",
            [2, 3],
            [[1, 1], [1, 1]],
            [2, 5],
            ["<=", ">="]
        )
        self.assertEqual(res["status"], "infactible")
        self.assertIsNone(res["solucion"])

    def test_no_acotado(self):
        """
        Caso no acotado
            Max Z = 2x1 + 3x2
            1x1 - 1x2 <= 2  (x2 puede crecer infinitamente)
        """
        res = resolver_simplex_tabular(
            "maximization",
            [2, 3],
            [[1, -1]],
            [2],
            ["<="]
        )
        self.assertEqual(res["status"], "no acotado")
        self.assertIsNone(res["solucion"])

    def test_degenerado(self):
        """
        Caso degenerado (restricciones redundantes)
            Max Z = 10x1 + 20x2
            1x1 + 2x2 <= 8
            2x1 + 4x2 <= 16  (Redundante)
            Z = 10 * (x1 + 2x2). Max Z = 10 * 8 = 80
        """
        res = resolver_simplex_tabular(
            "maximization",
            [10, 20],
            [[1, 2], [2, 4]],
            [8, 16],
            ["<=", "<="]
        )
        self.assertEqual(res["status"], "optimo")
        self.assertAlmostEqual(res["solucion"]["valor_optimo"], 80, places=3)

    def test_minimizacion_dos_fases(self):
        """
        Caso de minimización con dos fases
            Min Z = 4x1 + 1x2
            3x1 + 1x2 = 3
            4x1 + 3x2 >= 6
            1x1 + 2x2 <= 4
            Solución: x1=0.4, x2=1.8, Z=3.4
        """
        res = resolver_simplex_tabular(
            "minimization",
            [4, 1],
            [[3, 1], [4, 3], [1, 2]],
            [3, 6, 4],
            ["=", ">=", "<="]
        )
        self.assertEqual(res["status"], "optimo")
        self.assertAlmostEqual(res["solucion"]["valor_optimo"], 3.4, places=3)
        self.assertAlmostEqual(res["solucion"]["variables"]["x1"], 0.4, places=3)
        self.assertAlmostEqual(res["solucion"]["variables"]["x2"], 1.8, places=3)

    def test_con_igualdad(self):
        """
        Caso de restricciones con igualdad
            Max Z = 3x1 + 2x2
            2x1 + 1x2 = 8
            1x1 + 3x2 <= 9
            Solución: x1=3, x2=2, Z=13
        """
        res = resolver_simplex_tabular(
            "maximization",
            [3, 2],
            [[2, 1], [1, 3]],
            [8, 9],
            ["=", "<="]
        )
        self.assertEqual(res["status"], "optimo")
        self.assertAlmostEqual(res["solucion"]["valor_optimo"], 13, places=3)
        self.assertAlmostEqual(res["solucion"]["variables"]["x1"], 3, places=3)
        self.assertAlmostEqual(res["solucion"]["variables"]["x2"], 2, places=3)

    def test_con_artificiales(self):
        """
        Caso con variables artificiales (>=)
            Min Z = 2x1 + 3x2
            1x1 - 1x2 >= 2
            3x1 + 2x2 <= 12
            Solución: x1=2, x2=0, Z=4
        """
        res = resolver_simplex_tabular(
            "minimization",
            [2, 3],
            [[1, -1], [3, 2]],
            [2, 12],
            [">=", "<="]
        )

        self.assertEqual(res["status"], "optimo")
        self.assertAlmostEqual(res["solucion"]["valor_optimo"], 4, places=3)
        self.assertAlmostEqual(res["solucion"]["variables"]["x1"], 2, places=3)
        self.assertAlmostEqual(res["solucion"]["variables"]["x2"], 0, places=3)

    def test_coeficientes_grandes(self):
        """
        Caso con coeficientes grandes
            Max Z = 10000x1 + 20000x2
            5000x1 + 3000x2 <= 30000
            2000x1 + 4000x2 <= 40000
            Solución: x1=0, x2=10, Z=200000
        """
        res = resolver_simplex_tabular(
            "maximization",
            [10000, 20000],
            [[5000, 3000], [2000, 4000]],
            [30000, 40000],
            ["<=", "<="]
        )
        self.assertEqual(res["status"], "optimo")
        self.assertAlmostEqual(res["solucion"]["valor_optimo"], 200000, places=3)

    def test_dependencia_lineal(self):
        """
        Caso con restricciones linealmente dependientes
            Max Z = 2x1 + 3x2
            1x1 + 1x2 <= 4
            2x1 + 2x2 <= 8 (Redundante)
            Solución: x1=0, x2=4, Z=12
        """
        res = resolver_simplex_tabular(
            "maximization",
            [2, 3],
            [[1, 1], [2, 2]],
            [4, 8],
            ["<=", "<="]
        )
        self.assertEqual(res["status"], "optimo")
        self.assertAlmostEqual(res["solucion"]["valor_optimo"], 12, places=3)
        self.assertAlmostEqual(res["solucion"]["variables"]["x1"], 0, places=3)
        self.assertAlmostEqual(res["solucion"]["variables"]["x2"], 4, places=3)

    def test_problema_acotado_con_obj_negativo(self):
        """
            Max Z = 1x1 - 1x2
            1x1 + 1x2 <= 2
            Solución (con x>=0): x1=2, x2=0, Z=2
        """
        res = resolver_simplex_tabular(
            "maximization",
            [1, -1],
            [[1, 1]],
            [2],
            ["<="]
        )
        self.assertEqual(res["status"], "optimo")
        self.assertAlmostEqual(res["solucion"]["valor_optimo"], 2, places=3)
        self.assertAlmostEqual(res["solucion"]["variables"]["x1"], 2, places=3)
        self.assertAlmostEqual(res["solucion"]["variables"]["x2"], 0, places=3)

class TestSimplexRoutes(unittest.TestCase):

    def setUp(self):
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    def test_solve_tabular(self):
        payload = {
            "problem_type": "maximization",
            "C": [3, 5],
            "LI": [[1, 0], [0, 2], [3, 2]],
            "LD": [4, 12, 18],
            "O": ["<=", "<=", "<="]
        }

        response = self.client.post("/simplex/solve-tabular", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "optimo")
        self.assertAlmostEqual(data["solucion"]["valor_optimo"], 36, places=3)
        self.assertAlmostEqual(data["solucion"]["variables"]["x1"], 2, places=3)
        self.assertAlmostEqual(data["solucion"]["variables"]["x2"], 6, places=3)


if __name__ == "__main__":
    unittest.main()