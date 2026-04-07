"""
Algoritmo: A* (A-estrella)

Características:
  - Garantiza el camino más corto usando heurística admisible.
  - Heurística: distancia Manhattan (apropiada para 4 direcciones).
  - Combina el costo real g(n) + heurística h(n).
  - Movimiento: 4 direcciones (arriba, abajo, izquierda, derecha).
"""

import heapq
from .base import AlgoritmoBase, ResultadoBusqueda, DIRECCIONES


class AStar(AlgoritmoBase):
    NOMBRE = "A* (Manhattan)"

    def _heuristica(self, a: tuple[int, int], b: tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def buscar(self) -> ResultadoBusqueda:
        # heap: (f, g, nodo)
        heap: list[tuple[int, int, tuple[int, int]]] = []
        g_inicio = 0
        h_inicio = self._heuristica(self.inicio, self.fin)
        heapq.heappush(heap, (g_inicio + h_inicio, g_inicio, self.inicio))

        padres: dict = {self.inicio: None}
        costo_g: dict[tuple[int, int], int] = {self.inicio: 0}
        cerrados: set[tuple[int, int]] = set()
        visitados: list[tuple[int, int]] = []
        nodos_expandidos = 0

        while heap:
            f, g, actual = heapq.heappop(heap)

            if actual in cerrados:
                continue
            cerrados.add(actual)

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
                if not self.es_valida(*vecino):
                    continue
                nuevo_g = g + 1
                if vecino not in costo_g or nuevo_g < costo_g[vecino]:
                    costo_g[vecino] = nuevo_g
                    padres[vecino] = actual
                    h = self._heuristica(vecino, self.fin)
                    heapq.heappush(heap, (nuevo_g + h, nuevo_g, vecino))

        return ResultadoBusqueda(
            camino=[],
            visitados=visitados,
            nodos_expandidos=nodos_expandidos,
            encontrado=False,
        )
