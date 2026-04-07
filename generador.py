"""
Generador de laberintos usando Recursive Backtracker (DFS aleatorio).

Produce laberintos con un camino garantizado entre cualquier par de celdas
libres (laberinto perfecto: exactamente un camino entre cada par).

La grilla resultante usa la convención de la app:
  True  = pared
  False = libre
"""

import random


def generar_laberinto(filas: int, cols: int) -> list[list[bool]]:
    """
    Genera un laberinto perfecto de tamaño filas×cols.

    Internamente trabaja con una grilla donde las celdas impares son
    "habitaciones" y las pares son "paredes" potenciales. Luego mapea
    al tamaño solicitado.
    """
    # Trabajar en grilla interna de tamaño impar para tener paredes entre celdas
    f_int = filas if filas % 2 == 1 else filas - 1
    c_int = cols if cols % 2 == 1 else cols - 1

    # Todo empieza como pared
    grilla = [[True] * c_int for _ in range(f_int)]

    def en_rango(r: int, c: int) -> bool:
        return 0 <= r < f_int and 0 <= c < c_int

    # Recursive backtracker con stack explícito
    inicio_r, inicio_c = 1, 1
    grilla[inicio_r][inicio_c] = False
    stack = [(inicio_r, inicio_c)]

    while stack:
        r, c = stack[-1]
        # Vecinos a distancia 2 (saltar la pared intermedia)
        vecinos = []
        for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nr, nc = r + dr, c + dc
            if en_rango(nr, nc) and grilla[nr][nc]:
                vecinos.append((nr, nc, r + dr // 2, c + dc // 2))

        if vecinos:
            nr, nc, mr, mc = random.choice(vecinos)
            grilla[mr][mc] = False  # abrir pared intermedia
            grilla[nr][nc] = False  # abrir celda destino
            stack.append((nr, nc))
        else:
            stack.pop()

    # Expandir a tamaño original si la grilla interna es menor
    resultado = [[True] * cols for _ in range(filas)]
    for r in range(f_int):
        for c in range(c_int):
            resultado[r][c] = grilla[r][c]

    return resultado
