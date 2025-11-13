# Imagen base mínima de Python
FROM python:3.12-slim AS base

# Establece el directorio de trabajo
WORKDIR /app

# Instala uv sin cache (ligero)
RUN pip install --no-cache-dir uv

# Copia solo los archivos de dependencias primero (mejor caché)
COPY pyproject.toml uv.lock ./

# Instala dependencias del proyecto directamente en el sistema
RUN uv pip install --system --no-cache-dir --requirements pyproject.toml

# Copia el resto del código (sin venv, __pycache__, etc.)
COPY . .

# Expone el puerto FastAPI
EXPOSE 5000

# Comando de ejecución
CMD ["uv", "run", "python", "main.py"]
