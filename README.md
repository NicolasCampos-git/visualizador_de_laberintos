# Visualizador de Algoritmos de Busqueda en Laberintos

<div align="center">
  <img src="logo.png" alt="logo" width="300">
</div>

Aplicacion de escritorio en Python (Tkinter) para visualizar, probar y comparar algoritmos de busqueda de rutas sobre laberintos.

El objetivo es entender de forma visual como cada algoritmo explora el espacio de busqueda, que camino encuentra y a que costo, facilitando la comparacion directa entre distintas estrategias (BFS, DFS, A*, etc.).

## Que hace la aplicacion

- Muestra un laberinto en una grilla donde se pueden dibujar paredes, definir un punto de inicio y un punto de fin.
- Permite seleccionar un algoritmo de busqueda desde un menu desplegable.
- Al ejecutar, **anima paso a paso** los nodos explorados y luego resalta el camino encontrado.
- Muestra metricas de telemetria: distancia (pasos), tiempo de ejecucion (ms) y cantidad de nodos expandidos.
- Incluye generacion automatica de laberintos y control de velocidad de animacion.

### Controles

| Accion | Control |
|---|---|
| Colocar/borrar paredes | Clic izquierdo + arrastrar |
| Definir inicio / fin | Clic derecho (cicla entre inicio, fin, borrar) |
| Ejecutar algoritmo | Boton "Iniciar" |
| Borrar resultado (sin perder el laberinto) | Boton "Limpiar camino" |
| Generar un laberinto aleatorio nuevo | Boton "Generar laberinto" |

## Requisitos

- Python 3.10+
- Tkinter (incluido en la libreria estandar de Python)

En Arch Linux, si tkinter no esta disponible:

```bash
sudo pacman -S tk
```

En Ubuntu/Debian:

```bash
sudo apt install python3-tk
```

## Ejecucion

```bash
python3 main.py
```

## Estructura del proyecto

```
ejercicio-laberinto/
├── main.py              # Aplicacion principal (UI + logica)
├── generador.py         # Generador de laberintos (recursive backtracker)
├── logo.png             # Imagen del proyecto
├── algoritmos/
│   ├── __init__.py
│   ├── base.py          # Contrato base (clase abstracta)
│   ├── bfs.py           # Busqueda por amplitud
│   ├── dfs.py           # Busqueda por profundidad
│   └── astar.py         # A* con heuristica Manhattan
└── README.md
```

## Como implementar un nuevo algoritmo

La aplicacion usa un **sistema de plugins**: cualquier archivo `.py` dentro de la carpeta `algoritmos/` que contenga una clase heredando de `AlgoritmoBase` se detecta automaticamente y aparece en el menu desplegable, sin modificar ningun otro archivo.

### Paso 1 — Crear el archivo

Crear un archivo en `algoritmos/`, por ejemplo `algoritmos/bfs.py`.

### Paso 2 — Heredar de `AlgoritmoBase` e implementar `buscar()`

```python
from .base import AlgoritmoBase, ResultadoBusqueda, DIRECCIONES


class BFS(AlgoritmoBase):
    NOMBRE = "BFS (Amplitud)"

    def buscar(self) -> ResultadoBusqueda:
        # Implementar el algoritmo aca
        ...
```

### Paso 3 — Entender el contrato

Tu clase recibe estos datos a traves de `self` (inyectados por `__init__` de `AlgoritmoBase`):

| Atributo | Tipo | Descripcion |
|---|---|---|
| `self.grilla` | `list[list[bool]]` | Matriz 2D. `True` = pared, `False` = celda libre |
| `self.inicio` | `tuple[int, int]` | Coordenada `(fila, columna)` del punto de partida |
| `self.fin` | `tuple[int, int]` | Coordenada `(fila, columna)` del destino |
| `self.filas` | `int` | Cantidad de filas de la grilla |
| `self.cols` | `int` | Cantidad de columnas de la grilla |

Tu metodo `buscar()` debe retornar un `ResultadoBusqueda`:

| Campo | Tipo | Descripcion |
|---|---|---|
| `camino` | `list[tuple[int, int]]` | Lista de celdas desde inicio hasta fin. Lista vacia si no hay camino. |
| `visitados` | `list[tuple[int, int]]` | Celdas en el orden en que fueron exploradas (la UI las usa para la animacion). |
| `nodos_expandidos` | `int` | Total de nodos sacados de la frontera de busqueda. |
| `encontrado` | `bool` | `True` si se encontro un camino valido. |

### Paso 4 — Restricciones de movimiento

Solo se permiten **4 direcciones**: arriba, abajo, izquierda, derecha. Sin diagonales.

Las direcciones estan definidas en `base.py` como:

```python
DIRECCIONES = [(-1, 0), (1, 0), (0, -1), (0, 1)]
```

### Paso 5 — Metodos auxiliares disponibles

`AlgoritmoBase` provee dos metodos utiles que podes usar en tu implementacion:

- **`self.es_valida(fila, col)`** — Devuelve `True` si la celda esta dentro de los limites y no es pared.
- **`self.reconstruir_camino(padres)`** — Recibe un diccionario `{celda: celda_padre}` (donde el inicio tiene padre `None`) y devuelve la lista ordenada del camino desde inicio hasta fin.

### Ejemplo completo: BFS (Busqueda por Amplitud)

```python
"""
Algoritmo: BFS (Busqueda por Amplitud / Breadth-First Search)

Garantiza encontrar el camino mas corto en grafos sin pesos.
Explora nivel por nivel desde el nodo inicio.
"""

from collections import deque
from .base import AlgoritmoBase, ResultadoBusqueda, DIRECCIONES


class BFS(AlgoritmoBase):
    NOMBRE = "BFS (Amplitud)"

    def buscar(self) -> ResultadoBusqueda:
        cola: deque[tuple[int, int]] = deque([self.inicio])
        padres: dict = {self.inicio: None}
        visitados: list[tuple[int, int]] = []
        nodos_expandidos = 0

        while cola:
            actual = cola.popleft()
            nodos_expandidos += 1
            visitados.append(actual)

            if actual == self.fin:
                camino = self.reconstruir_camino(padres)
                return ResultadoBusqueda(
                    camino=camino,
                    visitados=visitados,
                    nodos_expandidos=nodos_expandidos,
                    encontrado=True,
                )

            for df, dc in DIRECCIONES:
                vecino = (actual[0] + df, actual[1] + dc)
                if self.es_valida(*vecino) and vecino not in padres:
                    padres[vecino] = actual
                    cola.append(vecino)

        return ResultadoBusqueda(
            camino=[],
            visitados=visitados,
            nodos_expandidos=nodos_expandidos,
            encontrado=False,
        )
```

Guarda ese archivo como `algoritmos/bfs.py`, ejecuta `python3 main.py` y "BFS (Amplitud)" va a aparecer automaticamente en el menu.
