"""
Algoritmo: BFS (Búsqueda por Amplitud / Breadth-First Search)

Características:
  - Garantiza encontrar el camino más corto en grafos sin pesos.
  - Explora nivel por nivel desde el nodo inicio.
  - Complejidad: O(V + E) donde V = celdas libres, E = aristas.
  - Movimiento: 4 direcciones (arriba, abajo, izquierda, derecha).
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
