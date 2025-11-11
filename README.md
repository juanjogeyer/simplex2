# Simplex Solver API

Proyecto en **FastAPI** para resolver problemas de programación lineal con el método Simplex.  
El entorno y las dependencias se manejan con [uv](https://docs.astral.sh/uv/).

---

## Requisitos previos

- Tener instalado **Python 3.12+**
- Instalar **uv** (gestor de dependencias y entornos)

## Instalación
Una vez clonado el repositorio hay que instalar las dependencias con:

```bash
uv sync
```
## Ejecución
Ejecutar el proyecto en modo development con:

```bash
uv run fastapi dev
```

La aplicación quedará disponible en http://127.0.0.1:8000 y la documentación automática en http://127.0.0.1:8000/docs

## Autores

- [@juanjo_geyer](https://github.com/juanjogeyer)
- [@juan_lopez](https://github.com/juan1lopez)
- [@manuel_olivares](https://github.com/manuolivares05)
- [@tomas_alfaro](https://github.com/tomasalfaro)
- [@joaquin_lepez](https://github.com/JoaquinLepez)


## 1. Formulación de Programación Lineal


Problema: 

Maximizar Z = 3x + 2y 
sujeto a:

x + y ≤ 4

x - y ≤ 2


**En el caso de testear en el proyecto siempre las restricciones deben esta impuestas ≤.**

```
{
  "model": "max",          // "min" para minimizar, "max" para maximizar
  "c": [3, 2],             // Coeficientes de la función objetivo
  "A": [[1, 1], [1, -1]], // Restricciones (matriz A)
  "b": [4, 2]            // Lado derecho de las restricciones
}
```

## 2. Cómo testear en Postman

  - Abrir Postman y crear una nueva request.

  - Seleccionar método POST.

```
http://127.0.0.1:8000/simplex/solve
```

- Respuesta esperada:
```
{
  "success": true,
  "status": "Optimization terminated successfully. (HiGHS Status 7: Optimal)",
  "objective_value": 12.0,
  "solution": [4.0, 0.0],
  "model": "max"
}

```
Cuando llamas al endpoint /simplex/solve, la API devuelve un JSON con los siguientes campos:

**success:** indica si el problema se resolvió correctamente.

- true significa que se encontró una solución óptima factible.

- false significa que no se encontró solución (puede ser infactible o ilimitado).

**status:** es un mensaje del solver HiGHS que describe cómo terminó la optimización.

- Por ejemplo: "Optimization terminated successfully" quiere decir que encontró una solución óptima.

- Otros posibles mensajes son "Problem is infeasible" (no hay solución factible) o "Problem is unbounded" (la función objetivo crece indefinidamente).

**objective_value:** es el valor óptimo de la función objetivo 𝑍.

- Si el modelo era de minimización, muestra el menor valor alcanzable.

- Si era de maximización, muestra el mayor valor alcanzable.

**solution:** es un arreglo con los valores de las variables de decisión que alcanzan el valor óptimo.

- Ejemplo: [4.0, 0.0] significa que 𝑥1 = 4 y 𝑥2 = 0

**model:** indica si el problema enviado era de tipo "min" (minimización) o "max" (maximización).
