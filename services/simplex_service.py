import numpy as np
from typing import List, Dict, Any, Tuple, Literal, Optional
from io import BytesIO
import matplotlib
# Use a non-interactive backend suitable for servers and tests
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def _formatear_tableau(
    tableau: np.ndarray, 
    var_names: List[str], 
    basic_vars: List[str], 
    titulo: str
) -> Dict[str, Any]:
    """Formatea un tableau de numpy en un diccionario legible."""
    
    # Encabezados de las columnas
    headers = ["Base"] + var_names + ["LD (RHS)"]
    
    # Fila de la Función Objetivo (Fila Z)
    fila_obj_vals = [round(val, 6) for val in tableau[-1, :]]
    fila_obj = ["Z"] + list(fila_obj_vals)
    
    # Filas de las restricciones
    filas_restricciones = []
    for i, var_basica in enumerate(basic_vars):
        fila_vals = [round(val, 6) for val in tableau[i, :]]
        fila = [var_basica] + list(fila_vals)
        filas_restricciones.append(fila)
        
    return {
        "titulo": titulo,
        "headers": headers,
        "filas": filas_restricciones,
        "fila_obj": fila_obj
    }

def _obtener_solucion_final(
    tableau: np.ndarray, 
    var_names: List[str], 
    basic_vars: List[str], 
    num_vars_originales: int,
    problem_type: str
) -> Dict[str, Any]:
    """Extrae los valores finales del último tableau."""
    
    solucion = {"variables": {}, "valor_optimo": 0.0}
    
    valor_optimo_raw = tableau[-1, -1]
    
    # Se revierte el signo en caso de problema de minimización
    if problem_type == 'minimization':
        solucion["valor_optimo"] = -valor_optimo_raw
    else:
        solucion["valor_optimo"] = valor_optimo_raw

    # Inicializar todas las variables originales a 0
    for i in range(num_vars_originales):
        solucion["variables"][f"x{i+1}"] = 0.0
        
    # Variables de holgura/exceso 
    for var in var_names:
        if not var.startswith('x') and not var.startswith('a'):
             solucion["variables"][var] = 0.0

    # Sobrescribir con los valores de las variables básicas
    for i, var_basica in enumerate(basic_vars):
        if var_basica in solucion["variables"]:
            solucion["variables"][var_basica] = round(tableau[i, -1], 6)
            
    return solucion

def _ejecutar_iteraciones_simplex(
    tableau: np.ndarray, 
    var_names: List[str], 
    basic_vars: List[str],
    fase: int,
    iter_offset: int = 0
) -> Tuple[str, np.ndarray, List[Dict[str, Any]], List[str]]:
    """
    Ejecuta el bucle de iteraciones del Simplex sobre un tableau dado.
    Retorna (status, tableau_final, historial_tablas, basic_vars_finales)
    """
    
    historial_tablas = []
    num_restricciones = tableau.shape[0] - 1
    
    # Copiamos las variables básicas para no modificar la lista original en el scope superior
    current_basic_vars = list(basic_vars)

    # Límite de iteraciones para evitar bucles infinitos (degeneración)
    for iteracion in range(1, 51):
        titulo = f"Fase {fase} - Iteración {iteracion + iter_offset}"
        historial_tablas.append(
            _formatear_tableau(tableau, var_names, current_basic_vars, titulo)
        )

        # 1. Comprobar optimalidad:
        # Fila Z (última fila), sin incluir la columna RHS (última columna)
        fila_obj = tableau[-1, :-1]
        
        # Tolerancia para comparaciones de punto flotante
        TOL = -1e-9
        
        if np.all(fila_obj >= TOL):
            # ÓPTIMO ENCONTRADO
            return "optimo", tableau, historial_tablas, current_basic_vars

        # 2. Encontrar Columna Pivote (variable entrante)
        # La columna con el valor más negativo en la fila Z
        pivot_col = np.argmin(fila_obj)
        columna_pivote_vals = tableau[:-1, pivot_col] # Valores de la columna, sin fila Z

        # 3. Comprobar si es No Acotado 
        if np.all(columna_pivote_vals <= 1e-9):
            # Todos los coeficientes en la columna pivote son <= 0
            return "no acotado", tableau, historial_tablas, current_basic_vars

        # 4. Encontrar Fila Pivote (Test de Razón Mínima)
        rhs = tableau[:-1, -1] # Lado derecho (RHS)
        
        # Ignorar filas donde el elemento de la columna pivote es <= 0
        # Usamos np.inf para valores no válidos
        ratios = np.full(num_restricciones, np.inf)
        for i in range(num_restricciones):
            if columna_pivote_vals[i] > 1e-9:
                ratios[i] = rhs[i] / columna_pivote_vals[i]

        pivot_row = np.argmin(ratios)
        
        # 5. Realizar Pivoteo (Gauss-Jordan)
        
        # Actualizar la variable básica de la fila
        current_basic_vars[pivot_row] = var_names[pivot_col]
        
        pivot_element = tableau[pivot_row, pivot_col]
        
        # a) Normalizar la fila pivote
        tableau[pivot_row, :] = tableau[pivot_row, :] / pivot_element
        
        # b) Hacer cero los otros elementos de la columna pivote
        for i in range(tableau.shape[0]): # Incluye la fila Z
            if i != pivot_row:
                factor = tableau[i, pivot_col]
                tableau[i, :] = tableau[i, :] - factor * tableau[pivot_row, :]

    # Si llega aquí, excedió el límite de iteraciones
    return "max_iterations_reached", tableau, historial_tablas, current_basic_vars

def resolver_simplex_tabular(
    problem_type: Literal['minimization', 'maximization'],
    C: List[float],
    LI: List[List[float]],
    LD: List[float],
    O: List[Literal["<=", ">=", "="]]
) -> Dict[str, Any]:
    """
    Resuelve un problema de Programación Lineal usando el Método Simplex Tabular
    (Dos Fases si es necesario).

    Retorna un diccionario con:
    - status: 'optimo', 'infactible', 'no acotado'
    - tablas: Una lista de todas las tablas intermedias y finales.
    - solucion: (si es óptimo) Un diccionario con 'valor_optimo' y 'variables'.
    """

    num_vars_originales = len(C)
    num_restricciones = len(LI)
    
    # Estandarización del problema
    
    C_interno = np.array(C, dtype=float)
    A_matrix = np.array(LI, dtype=float)
    LD_vector = np.array(LD, dtype=float).reshape(-1, 1) # Vector columna
    
    for i in range(num_restricciones):
        if LD_vector[i] < 0:
            LD_vector[i] *= -1
            A_matrix[i, :] *= -1
            if O[i] == "<=":
                O[i] = ">="
            elif O[i] == ">=":
                O[i] = "<="
                
    if problem_type == 'minimization':
        C_interno = -C_interno
    
    # Nombres de las variables
    var_names = [f'x{i+1}' for i in range(num_vars_originales)]
    basic_vars_por_fila = [None] * num_restricciones 
    
    # Listas para almacenar columnas y sus nombres
    slack_cols_list = []
    surplus_cols_list = []
    artificial_cols_list = []
    
    slack_names = []
    surplus_names = []
    artificial_names = []
    
    necesita_fase_1 = False

    for i, op in enumerate(O):
        if op == "<=":
            # Añadir variable de Holgura
            var_name = f's{i+1}'
            slack_names.append(var_name)
            basic_vars_por_fila[i] = var_name # Asignar por índice
            
            col = np.zeros(num_restricciones)
            col[i] = 1
            slack_cols_list.append(col)
            
        elif op == ">=":
            # Añadir variable de Exceso (surplus) y Artificial
            necesita_fase_1 = True
            
            var_name_e = f'e{i+1}'
            surplus_names.append(var_name_e)
            col_e = np.zeros(num_restricciones)
            col_e[i] = -1
            surplus_cols_list.append(col_e)
            
            var_name_a = f'a{i+1}'
            artificial_names.append(var_name_a)
            basic_vars_por_fila[i] = var_name_a # Asignar por índice
            col_a = np.zeros(num_restricciones)
            col_a[i] = 1
            artificial_cols_list.append(col_a)
            
        elif op == "=":
            # Añadir variable Artificial
            necesita_fase_1 = True
            var_name_a = f'a{i+1}'
            artificial_names.append(var_name_a)
            basic_vars_por_fila[i] = var_name_a # Asignar por índice
            
            col_a = np.zeros(num_restricciones)
            col_a[i] = 1
            artificial_cols_list.append(col_a)

    # Ensamblar la matriz de restricciones y var_names EN EL MISMO ORDEN
    partes_A = [A_matrix]
    
    if slack_cols_list:
        partes_A.append(np.stack(slack_cols_list, axis=1))
        var_names.extend(slack_names)
        
    if surplus_cols_list:
        partes_A.append(np.stack(surplus_cols_list, axis=1))
        var_names.extend(surplus_names)

    if artificial_cols_list:
        partes_A.append(np.stack(artificial_cols_list, axis=1))
        var_names.extend(artificial_names)
    
    # Matriz A completa (cuerpo del tableau)
    tableau_cuerpo = np.hstack(partes_A)
    
    # Ahora filtramos los None 
    basic_vars_fase1 = [v for v in basic_vars_por_fila if v is not None]

    historial_tablas_completo = []
    
    # FASE 1 (Si es necesaria) 
    
    if necesita_fase_1:
        
        fila_obj_fase1 = np.zeros(tableau_cuerpo.shape[1] + 1)
        indices_a = [i for i, nombre in enumerate(var_names) if nombre.startswith('a')]
        fila_obj_fase1[indices_a] = 1.0
        
        tableau_fase1 = np.vstack([
            np.hstack([tableau_cuerpo, LD_vector]), 
            fila_obj_fase1                        
        ])
        
        # Poner Fila Z en forma canónica
        for i, var_basica in enumerate(basic_vars_fase1): # Usar la lista limpia
            if var_basica.startswith('a'):
                tableau_fase1[-1, :] -= tableau_fase1[i, :]
        
        # Ejecutar Simplex Fase 1
        status_f1, tableau_f1_final, tablas_f1, basic_vars_f1 = \
            _ejecutar_iteraciones_simplex(
                tableau_fase1, var_names, basic_vars_fase1, fase=1 # Usar la lista limpia
            )
        
        historial_tablas_completo.extend(tablas_f1)
        
        if status_f1 != 'optimo':
            return {"status": status_f1, "tablas": historial_tablas_completo, "solucion": None}

        if abs(tableau_f1_final[-1, -1]) > 1e-9:
            return {"status": "infactible", "tablas": historial_tablas_completo, "solucion": None}

        # Preparación FASE 2 ---

        indices_a = [i for i, nombre in enumerate(var_names) if nombre.startswith('a')]
        
        tableau_cuerpo_f2 = np.delete(tableau_f1_final[:-1, :], indices_a, axis=1)
        var_names_f2 = [v for v in var_names if not v.startswith('a')]
        
        fila_obj_f2 = np.zeros(len(var_names_f2) + 1) 
        fila_obj_f2[:num_vars_originales] = -C_interno
        
        tableau_fase2 = np.vstack([
            tableau_cuerpo_f2,
            fila_obj_f2
        ])
        
        for i, var_basica in enumerate(basic_vars_f1):
            if var_basica in var_names_f2:
                col_basica_idx = var_names_f2.index(var_basica)
                coef_en_obj = tableau_fase2[-1, col_basica_idx]
                
                if abs(coef_en_obj) > 1e-9:
                    tableau_fase2[-1, :] -= coef_en_obj * tableau_fase2[i, :]
        
        tableau_para_iterar = tableau_fase2
        var_names_para_iterar = var_names_f2
        basic_vars_para_iterar = basic_vars_f1
        fase_actual = 2
        iter_offset = len(historial_tablas_completo)

    else:
        # Problema Estándar (Sin Fase 1) 
        
        fila_obj_f_std = np.zeros(tableau_cuerpo.shape[1] + 1)
        fila_obj_f_std[:num_vars_originales] = -C_interno
        
        tableau_std = np.vstack([
            np.hstack([tableau_cuerpo, LD_vector]), 
            fila_obj_f_std                        
        ])
        
        tableau_para_iterar = tableau_std
        var_names_para_iterar = var_names
        basic_vars_para_iterar = basic_vars_fase1 # Usar la lista limpia
        fase_actual = 0 
        iter_offset = 0

    # FASE 2 (o Fase Única) 
    
    status_f2, tableau_f2_final, tablas_f2, basic_vars_f2 = \
        _ejecutar_iteraciones_simplex(
            tableau_para_iterar, 
            var_names_para_iterar, 
            basic_vars_para_iterar, 
            fase=fase_actual,
            iter_offset=iter_offset
        )

    historial_tablas_completo.extend(tablas_f2)
    
    # Preparar Resultados Finales 
    
    if status_f2 != 'optimo':
        return {"status": status_f2, "tablas": historial_tablas_completo, "solucion": None}

    solucion_final = _obtener_solucion_final(
        tableau_f2_final,
        var_names_para_iterar,
        basic_vars_f2,
        num_vars_originales,
        problem_type
    )
    
    return {
        "status": "optimo",
        "tablas": historial_tablas_completo,
        "solucion": solucion_final
    }

def generar_grafico_2d(
    C,
    LI,
    LD,
    titulo: str = "Grafico de Restricciones y Funcion Objetivo",
    save_path: Optional[str] = None,
    xlim: Optional[Tuple[float, float]] = None,
    ylim: Optional[Tuple[float, float]] = None,
    show: bool = False,
    mark_point: Optional[Tuple[float, float]] = None,
):
    """
    Genera un gráfico que muestra las restricciones y la función objetivo.
    Solo funciona para problemas con 2 variables.

    Args:
        C (List[float]): Coeficientes de la función objetivo.
        LI (List[List[float]]): Coeficientes de las restricciones.
        LD (List[float]): Lados derechos de las restricciones.
        titulo (str): Título del gráfico.
    """
    if len(C) != 2:
        raise ValueError("El gráfico solo puede generarse para problemas con exactamente 2 variables.")

    # Calcular límites automáticos si no se especifican
    def _finite_vals(vals):
        vals = [v for v in vals if v is not None and np.isfinite(v)]
        return vals

    xs: List[float] = []
    ys: List[float] = []
    # Interceptos con ejes por cada restricción a*x1 + b*x2 = r
    for coef, r in zip(LI, LD):
        a, b = coef[0], coef[1]
        if a != 0:
            xs.append(r / a)
            ys.append(0.0)
        if b != 0:
            xs.append(0.0)
            ys.append(r / b)
    # Intersecciones entre pares de rectas
    n = len(LI)
    for i in range(n):
        a1, b1 = LI[i]
        r1 = LD[i]
        for j in range(i + 1, n):
            a2, b2 = LI[j]
            r2 = LD[j]
            det = a1 * b2 - a2 * b1
            if abs(det) > 1e-12:
                x_int = (r1 * b2 - r2 * b1) / det
                y_int = (a1 * r2 - a2 * r1) / det
                xs.append(x_int)
                ys.append(y_int)

    xs = _finite_vals(xs)
    ys = _finite_vals(ys)

    # Restringir a valores no negativos por convención (x1>=0, x2>=0)
    xs_pos = [v for v in xs if v is not None and np.isfinite(v) and v >= 0]
    ys_pos = [v for v in ys if v is not None and np.isfinite(v) and v >= 0]

    # Límites con márgen
    if xlim is None:
        if xs_pos:
            xmax = max(xs_pos)
            x_min, x_max = 0.0, max(1.0, xmax) * 1.1
        else:
            x_min, x_max = 0.0, 10.0
    else:
        x_min, x_max = xlim

    if ylim is None:
        if ys_pos:
            ymax = max(ys_pos)
            y_min, y_max = 0.0, max(1.0, ymax) * 1.1
        else:
            y_min, y_max = 0.0, 10.0
    else:
        y_min, y_max = ylim

    # Asegurar que el punto óptimo quede dentro de los límites
    if mark_point is not None:
        mx, my = mark_point
        if np.isfinite(mx) and mx >= 0:
            x_max = max(x_max, mx * 1.1 if mx > 0 else 1.0)
        if np.isfinite(my) and my >= 0:
            y_max = max(y_max, my * 1.1 if my > 0 else 1.0)

    x = np.linspace(x_min, x_max, 400)  # Rango de valores para x1

    plt.figure(figsize=(10, 6))

    # Graficar restricciones
    for i, (coef, ld) in enumerate(zip(LI, LD)):
        if coef[1] != 0:
            y = (ld - coef[0] * x) / coef[1]
            plt.plot(x, y, label=f"Restricción {i+1}")
        else:
            plt.axvline(x=ld / coef[0], label=f"Restricción {i+1}")

    # Graficar función objetivo
    if C[1] != 0:
        y_obj = (-C[0] * x) / C[1]
        plt.plot(x, y_obj, 'r--', label="Función Objetivo")
    else:
        plt.axvline(x=0, color='r', linestyle='--', label="Función Objetivo")

    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.title(titulo)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)

    # Marcar punto óptimo si se proporciona
    if mark_point is not None:
        mx, my = mark_point
        if np.isfinite(mx) and np.isfinite(my):
            plt.scatter([mx], [my], c='k', s=60, zorder=5, label='Óptimo')
            # Asegurar que la leyenda muestre el punto (manejar duplicación)
            handles, labels = plt.gca().get_legend_handles_labels()
            seen = set()
            new = []
            for h, l in zip(handles, labels):
                if l not in seen:
                    new.append((h, l))
                    seen.add(l)
            if new:
                plt.legend(*zip(*new))

    # Guardar si se especifica ruta; si no, devolver bytes PNG
    result = None
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
        result = save_path
    else:
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        result = buf.getvalue()
        buf.close()

    # Mostrar solo si se solicita (por defecto False en entorno servidor)
    if show:
        plt.show()

    plt.close()
    return result