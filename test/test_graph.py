import os
import tempfile
from services.simplex_service import generar_grafico_2d


def test_generar_grafico_2d_crea_archivo():
    C = [1, 1]
    LI = [[1, 0], [0, 1], [1, 1]]
    LD = [5, 6, 10]

    tmp_dir = tempfile.gettempdir()
    path = os.path.join(tmp_dir, "test_simplex_graph.png")
    try:
        out = generar_grafico_2d(C, LI, LD, save_path=path)
        assert out == path
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
    finally:
        if os.path.exists(path):
            os.remove(path)
