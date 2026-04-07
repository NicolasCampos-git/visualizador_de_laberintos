"""
Algoritmo: DFS (Búsqueda por Profundidad / Depth-First Search)

Características:
  - NO garantiza el camino más corto.
  - Usa una pila (LIFO) en lugar de una cola.
  - Útil para detectar si existe algún camino, no el óptimo.
  - Movimiento: 4 direcciones (arriba, abajo, izquierda, derecha).
"""

from .base import AlgoritmoBase, ResultadoBusqueda, DIRECCIONES


class DFS(AlgoritmoBase):
    NOMBRE = "DFS (Profundidad)"

    def buscar(self) -> ResultadoBusqueda:
        pila: list[tuple[int, int]] = [self.inicio]
        padres: dict = {self.inicio: None}
        visitados: list[tuple[int, int]] = []
        nodos_expandidos = 0

        while pila:
            actual = pila.pop()
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
                    pila.append(vecino)

        return ResultadoBusqueda(
            camino=[],
            visitados=visitados,
            nodos_expandidos=nodos_expandidos,
            encontrado=False,
        )
