from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Literal
from services.simplex_service import resolver_simplex_tabular, generar_grafico_2d
import uuid
import tempfile
import os
import logging
import base64

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/simplex",
    tags=["Simplex Solver"]
)

class SimplexRequest(BaseModel):
    problem_type: Literal['minimization', 'maximization']
    C: List[float]
    LI: List[List[float]]
    LD: List[float]
    O: List[Literal['<=', '>=', '=']]


def _cleanup_file(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        # Silenciar errores de limpieza
        pass

@router.post("/solve-tabular")
async def solve_tabular(request: SimplexRequest):
    try:
        result = resolver_simplex_tabular(
            problem_type=request.problem_type,
            C=request.C,
            LI=request.LI,
            LD=request.LD,
            O=request.O
        )
        logger.info("Resolviendo problema simplex")
        return result
    except ValueError as e:
        logger.warning(f"Error de validación en /solve-tabular: {e}")
        raise HTTPException(status_code=400, detail=f"Datos inválidos: {e}")
    except Exception as e:
        logger.exception("Error interno en /solve-tabular")        
        raise HTTPException(status_code=500, detail="Ocurrió un error interno al resolver el problema. Intente nuevamente.")

@router.post("/generate-graph")
async def generate_graph(request: SimplexRequest, background_tasks: BackgroundTasks):
    if len(request.C) != 2:
        raise HTTPException(status_code=400, detail="El gráfico solo puede generarse para problemas con exactamente 2 variables.")

    try:
        # Resolver para obtener punto óptimo
        solve = resolver_simplex_tabular(
            problem_type=request.problem_type,
            C=request.C,
            LI=request.LI,
            LD=request.LD,
            O=request.O,
        )
        mark = None
        if solve.get("status") == "optimo" and solve.get("solucion"):
            vars_ = solve["solucion"]["variables"]
            mx = float(vars_.get("x1", 0.0))
            my = float(vars_.get("x2", 0.0))
            mark = (mx, my)

        tmp_dir = tempfile.gettempdir()
        filename = f"simplex_graph_{uuid.uuid4().hex}.png"
        graph_path = os.path.join(tmp_dir, filename)
        saved_path = generar_grafico_2d(
            request.C,
            request.LI,
            request.LD,
            titulo="Gráfico de Restricciones y Función Objetivo",
            save_path=graph_path,
            mark_point=mark,
        )
        if not saved_path or not os.path.exists(saved_path):
            raise HTTPException(status_code=500, detail="No se pudo generar el gráfico.")
        # Programar eliminación del archivo después de enviar
        background_tasks.add_task(_cleanup_file, saved_path)
        return FileResponse(saved_path, media_type="image/png", filename="graph.png")
    except ValueError as e:
        logger.warning(f"Error de validación en /generate-graph: {e}")
        raise HTTPException(status_code=400, detail=f"Datos inválidos: {e}")
    except Exception:
        logger.exception("Error interno en /generate-graph")
        raise HTTPException(status_code=500, detail="Ocurrió un error al generar el gráfico. Intente nuevamente.")

@router.post("/generate-graph-html", response_class=HTMLResponse)
async def generate_graph_html(request: SimplexRequest):
    if len(request.C) != 2:
        raise HTTPException(status_code=400, detail="Solo se puede graficar con exactamente 2 variables.")
    try:
        solve = resolver_simplex_tabular(
            problem_type=request.problem_type,
            C=request.C,
            LI=request.LI,
            LD=request.LD,
            O=request.O,
        )
        mark = None
        if solve.get("status") == "optimo" and solve.get("solucion"):
            vars_ = solve["solucion"]["variables"]
            mx = float(vars_.get("x1", 0.0))
            my = float(vars_.get("x2", 0.0))
            mark = (mx, my)

        raw_png = generar_grafico_2d(
            request.C,
            request.LI,
            request.LD,
            titulo="Gráfico de Restricciones y Función Objetivo",
            mark_point=mark,
        )
        if not isinstance(raw_png, (bytes, bytearray)):
            raise HTTPException(status_code=500, detail="Error generando imagen.")
        b64 = base64.b64encode(raw_png).decode("ascii")
        html = f"""
        <html><head><title>Gráfico Simplex</title></head>
        <body style='font-family: Arial;'>
        <h2>Gráfico de Restricciones y Función Objetivo</h2>
        <img src='data:image/png;base64,{b64}' alt='Grafico Simplex' style='max-width:100%;height:auto;border:1px solid #ccc;' />
        </body></html>
        """
        return HTMLResponse(content=html)
    except ValueError as e:
        logger.warning(f"Error de validación en /generate-graph-html: {e}")
        raise HTTPException(status_code=400, detail=f"Datos inválidos: {e}")
    except Exception:
        logger.exception("Error interno en /generate-graph-html")
        raise HTTPException(status_code=500, detail="Ocurrió un error al generar el gráfico en HTML. Intente nuevamente.")