"""
Contrato base que TODOS los algoritmos en esta carpeta deben cumplir.

Para agregar un nuevo algoritmo:
  1. Crea un archivo .py en esta carpeta (ej: dijkstra.py)
  2. Define una clase que herede de AlgoritmoBase
  3. Implementa el método `buscar()`
  4. La aplicación lo detectará automáticamente

Movimiento permitido: solo 4 direcciones (arriba, abajo, izquierda, derecha).
Sin diagonales.
"""

from abc import ABC, abstractmethod
from typing import Optional


# Las 4 direcciones permitidas: (fila_delta, col_delta)
DIRECCIONES = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class ResultadoBusqueda:
    """
    Objeto de retorno estándar que todos los algoritmos deben devolver.

    Atributos:
        camino      : Lista de celdas (fila, col) desde inicio hasta fin.
                      Lista vacía si no hay camino.
        visitados   : Lista de celdas en el orden en que fueron exploradas
                      (útil para animar la búsqueda en la UI).
        nodos_expandidos : Total de nodos sacados de la frontera de búsqueda.
        encontrado  : True si existe un camino válido hasta el destino.
    """

    def __init__(
        self,
        camino: list[tuple[int, int]],
        visitados: list[tuple[int, int]],
        nodos_expandidos: int,
        encontrado: bool,
    ):
        self.camino = camino
        self.visitados = visitados
        self.nodos_expandidos = nodos_expandidos
        self.encontrado = encontrado

    @property
    def distancia(self) -> int:
        """Número de pasos del camino encontrado (0 si no hay camino)."""
        return len(self.camino) - 1 if self.camino else 0


class AlgoritmoBase(ABC):
    """
    Clase base abstracta para todos los algoritmos de búsqueda de rutas.

    Entradas (recibidas en __init__):
        grilla      : Lista 2D de booleanos. True = obstáculo, False = libre.
        inicio      : Tupla (fila, col) de la celda de inicio.
        fin         : Tupla (fila, col) de la celda de destino.

    Salida (devuelta por buscar()):
        ResultadoBusqueda con camino, visitados, nodos_expandidos y encontrado.

    Restricción de movimiento: solo ARRIBA, ABAJO, IZQUIERDA, DERECHA.
    """

    # Nombre legible que aparecerá en el Combobox de la UI.
    # Sobreescribir en cada subclase.
    NOMBRE: str = "Algoritmo Base"

    def __init__(
        self,
        grilla: list[list[bool]],
        inicio: tuple[int, int],
        fin: tuple[int, int],
    ):
        self.grilla = grilla
        self.inicio = inicio
        self.fin = fin
        self.filas = len(grilla)
        self.cols = len(grilla[0]) if grilla else 0

    @abstractmethod
    def buscar(self) -> ResultadoBusqueda:
        """
        Ejecuta el algoritmo y retorna un ResultadoBusqueda.
        Este método es el único punto de entrada que la UI invoca.
        """
        ...

    def es_valida(self, fila: int, col: int) -> bool:
        """Devuelve True si la celda está dentro de los límites y no es obstáculo."""
        return (
            0 <= fila < self.filas
            and 0 <= col < self.cols
            and not self.grilla[fila][col]
        )

    def reconstruir_camino(
        self, padres: dict[tuple[int, int], Optional[tuple[int, int]]]
    ) -> list[tuple[int, int]]:
        """
        Reconstruye el camino desde fin hasta inicio usando el diccionario de padres.
        Retorna la lista ordenada de inicio → fin.
        """
        camino = []
        actual: Optional[tuple[int, int]] = self.fin
        while actual is not None:
            camino.append(actual)
            actual = padres.get(actual)
        camino.reverse()
        # Verificar que realmente llegue al inicio
        if camino and camino[0] == self.inicio:
            return camino
        return []
