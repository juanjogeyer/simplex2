from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from routers import router 
import logging
from fastapi.exceptions import RequestValidationError


logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

logger = logging.getLogger(__name__)
logger.info("Iniciando aplicación FastAPI...")

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_html():
    try:
        with open("frontend/templates/index.html", "r", encoding="utf-8") as f:
            logger.info("Cargando página principal: index.html")
            return HTMLResponse(content=f.read(), status_code=200)
    except Exception as e:
        logger.exception("Error cargando index.html")
        return HTMLResponse(content=f"<h1>Error interno: {e}</h1>", status_code=500)


@app.get("/tablas", response_class=HTMLResponse)
async def get_tablas_html():
    try:
        with open("frontend/templates/tablas.html", "r", encoding="utf-8") as f:
            logger.info("Cargando página de tablas: tablas.html")
            return HTMLResponse(content=f.read(), status_code=200)
    except Exception as e:
        logger.exception("Error cargando tablas.html")
        return HTMLResponse(content=f"<h1>Error interno: {e}</h1>", status_code=500)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Error de validación en {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Datos de entrada inválidos. Verifica el formato del JSON."},
    )
app.include_router(router)

logger.info("Aplicación lista. Servidor iniciado correctamente.")