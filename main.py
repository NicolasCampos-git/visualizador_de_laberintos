"""
Visualizador de Algoritmos de Búsqueda en Laberintos
=====================================================
Arquitectura: Tkinter + sistema de plugins (carpeta algoritmos/)

Controles del editor:
  - Click izquierdo + arrastrar : colocar/borrar paredes
  - Click derecho               : ciclar Inicio → Fin → borrar
  - Botón "Iniciar"             : ejecutar algoritmo seleccionado
  - Botón "Limpiar camino"      : borrar resultado sin perder el laberinto
  - Botón "Generar laberinto"   : generar un laberinto aleatorio nuevo

Movimiento de los algoritmos: 4 direcciones (↑ ↓ ← →). Sin diagonales.
"""

import importlib
import inspect
import os
import random
import sys
import time
import tkinter as tk
from tkinter import messagebox, ttk

# Agregar la carpeta raíz al path para que los algoritmos puedan importar base
sys.path.insert(0, os.path.dirname(__file__))

from algoritmos.base import AlgoritmoBase
from generador import generar_laberinto

# ── Configuración visual ──────────────────────────────────────────────────────
FILAS = 21
COLS = 31
TAM_CELDA = 26          # píxeles por celda

# Paleta alto contraste — paredes azules, caminos blancos (estilo imagen)
COLOR_FONDO      = "#1B2838"   # fondo general de la app (azul muy oscuro)
COLOR_GRILLA_BG  = "#2B4C9B"   # fondo del canvas (azul)
COLOR_CELDA      = "#FFFFFF"   # celda libre (blanco)
COLOR_PARED      = "#2B4C9B"   # obstáculo (azul fuerte)
COLOR_INICIO     = "#E53935"   # rojo brillante (pin de inicio)
COLOR_FIN        = "#43A047"   # verde bandera (meta)
COLOR_VISITADO   = "#FFCC80"   # naranja pastel (nodo explorado)
COLOR_CAMINO     = "#FF6F00"   # naranja fuerte (camino final)
COLOR_BORDE      = "#1A3780"   # borde de celdas (azul oscuro)

COLOR_PANEL      = "#0F1C30"   # panel de control
COLOR_TEXTO      = "#E8EAF6"   # texto principal
COLOR_TEXTO_DIM  = "#7986CB"   # texto secundario (indigo claro)
COLOR_ACENTO     = "#64B5F6"   # azul claro acento
COLOR_BTN_START  = "#43A047"   # verde
COLOR_BTN_CLEAR  = "#1E88E5"   # azul medio
COLOR_BTN_GEN    = "#FFA726"   # naranja

DELAY_ANIMACION  = 8           # ms entre pasos de animación

# ── Carga dinámica de algoritmos ──────────────────────────────────────────────

def cargar_algoritmos() -> dict[str, type[AlgoritmoBase]]:
    """
    Escanea la carpeta algoritmos/ y carga todas las clases que hereden
    de AlgoritmoBase. Devuelve {NOMBRE: Clase}.
    """
    algoritmos: dict[str, type[AlgoritmoBase]] = {}
    carpeta = os.path.join(os.path.dirname(__file__), "algoritmos")

    for archivo in sorted(os.listdir(carpeta)):
        if archivo.endswith(".py") and archivo not in ("__init__.py", "base.py"):
            modulo_nombre = f"algoritmos.{archivo[:-3]}"
            try:
                modulo = importlib.import_module(modulo_nombre)
                for _, obj in inspect.getmembers(modulo, inspect.isclass):
                    if (
                        issubclass(obj, AlgoritmoBase)
                        and obj is not AlgoritmoBase
                        and obj.__module__ == modulo_nombre
                    ):
                        algoritmos[obj.NOMBRE] = obj
            except Exception as e:
                print(f"[WARN] No se pudo cargar {archivo}: {e}")

    return algoritmos


# ── Aplicación principal ──────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Laberintos — Visualizador de Algoritmos")
        self.configure(bg=COLOR_FONDO)
        self.resizable(False, False)

        self.algoritmos = cargar_algoritmos()

        # Generar laberinto inicial (semilla fija para reproducibilidad)
        random.seed(42)
        self.grilla: list[list[bool]] = generar_laberinto(FILAS, COLS)
        random.seed()  # volver a aleatorio para futuros usos

        # Inicio abajo-izquierda, fin arriba-centro (como la imagen de referencia)
        self.inicio: tuple[int, int] | None = self._buscar_libre_desde(
            FILAS - 1, 0, rango_f=range(FILAS - 1, -1, -1), rango_c=range(COLS)
        )
        self.fin: tuple[int, int] | None = self._buscar_libre_desde(
            0, COLS // 2, rango_f=range(FILAS), rango_c=range(COLS // 2, -1, -1)
        )

        self._drag_mode: str | None = None   # "pared" | "borrar"
        self._animacion_id: str | None = None
        self._ejecutando = False

        self._construir_ui()
        self._dibujar_grilla_completa()
        self._centrar_ventana()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2
        self.geometry(f"+{x}+{y}")

    def _buscar_libre_desde(
        self, f_pref: int, c_pref: int,
        rango_f: range = None, rango_c: range = None,
    ) -> tuple[int, int] | None:
        """Busca la primera celda libre escaneando en el orden dado por rango_f y rango_c."""
        if rango_f is None:
            rango_f = range(FILAS)
        if rango_c is None:
            rango_c = range(COLS)
        for f in rango_f:
            for c in rango_c:
                if not self.grilla[f][c]:
                    return (f, c)
        return None

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _construir_ui(self):
        # ── Barra de título ──
        barra = tk.Frame(self, bg=COLOR_FONDO)
        barra.pack(fill="x", padx=12, pady=(10, 0))

        tk.Label(
            barra,
            text="LABERINTO",
            font=("Courier", 18, "bold"),
            fg=COLOR_ACENTO,
            bg=COLOR_FONDO,
        ).pack(side="left")

        tk.Label(
            barra,
            text=" — Visualizador de Algoritmos",
            font=("Courier", 11),
            fg=COLOR_TEXTO_DIM,
            bg=COLOR_FONDO,
        ).pack(side="left", pady=(4, 0))

        # ── Contenedor principal (canvas + panel) ──
        contenedor = tk.Frame(self, bg=COLOR_FONDO)
        contenedor.pack(padx=12, pady=8)

        self._construir_canvas(contenedor)
        self._construir_panel(contenedor)

        # ── Barra de estado inferior ──
        self._lbl_estado = tk.Label(
            self,
            text="Listo. Dibuja el laberinto y presiona Iniciar.",
            font=("Courier", 9),
            fg=COLOR_TEXTO_DIM,
            bg=COLOR_FONDO,
            anchor="w",
        )
        self._lbl_estado.pack(fill="x", padx=14, pady=(0, 8))

    def _construir_canvas(self, padre):
        ancho = COLS * TAM_CELDA
        alto  = FILAS * TAM_CELDA

        marco = tk.Frame(padre, bg=COLOR_BORDE, bd=1, relief="flat")
        marco.pack(side="left")

        self.canvas = tk.Canvas(
            marco,
            width=ancho,
            height=alto,
            bg=COLOR_GRILLA_BG,
            highlightthickness=0,
            cursor="crosshair",
        )
        self.canvas.pack()

        self.canvas.bind("<Button-1>",        self._on_click_izq)
        self.canvas.bind("<B1-Motion>",       self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda e: setattr(self, "_drag_mode", None))
        self.canvas.bind("<Button-3>",        self._on_click_der)

        # Matriz de IDs de rectángulos para actualización rápida
        self._rect_ids: list[list[int]] = []
        for f in range(FILAS):
            fila_ids = []
            for c in range(COLS):
                x1 = c * TAM_CELDA + 1
                y1 = f * TAM_CELDA + 1
                x2 = x1 + TAM_CELDA - 2
                y2 = y1 + TAM_CELDA - 2
                rid = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=COLOR_CELDA,
                    outline="#D0D8E8",
                    width=1,
                )
                fila_ids.append(rid)
            self._rect_ids.append(fila_ids)

    def _construir_panel(self, padre):
        panel = tk.Frame(padre, bg=COLOR_PANEL, width=220)
        panel.pack(side="left", fill="y", padx=(10, 0))
        panel.pack_propagate(False)

        def seccion(texto):
            tk.Label(
                panel,
                text=texto,
                font=("Courier", 8, "bold"),
                fg=COLOR_ACENTO,
                bg=COLOR_PANEL,
                anchor="w",
            ).pack(fill="x", padx=14, pady=(14, 2))
            tk.Frame(panel, bg=COLOR_BORDE, height=1).pack(fill="x", padx=14)

        # ── Sección: Algoritmo ──
        seccion("▸ ALGORITMO")

        nombres = list(self.algoritmos.keys())
        self._var_algo = tk.StringVar(value=nombres[0] if nombres else "")

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure(
            "Dark.TCombobox",
            fieldbackground="#1A2940",
            background="#1A2940",
            foreground=COLOR_TEXTO,
            selectbackground=COLOR_ACENTO,
            selectforeground="#0F1C30",
            arrowcolor=COLOR_ACENTO,
            bordercolor="#2B4C9B",
            lightcolor="#2B4C9B",
            darkcolor="#2B4C9B",
        )

        self._combo = ttk.Combobox(
            panel,
            textvariable=self._var_algo,
            values=nombres,
            state="readonly",
            style="Dark.TCombobox",
            font=("Courier", 10),
        )
        self._combo.pack(fill="x", padx=14, pady=8)

        # ── Botones de control ──
        seccion("▸ CONTROL")

        self._btn_iniciar = self._boton(
            panel, "▶  INICIAR", COLOR_BTN_START, "#FFFFFF", self._iniciar
        )
        self._btn_limpiar = self._boton(
            panel, "◌  LIMPIAR CAMINO", COLOR_BTN_CLEAR, "#FFFFFF", self._limpiar_camino
        )
        self._btn_generar = self._boton(
            panel, "⚙  GENERAR LABERINTO", COLOR_BTN_GEN, "#1e1e2e", self._generar_laberinto
        )

        # ── Sección: Telemetría ──
        seccion("▸ TELEMETRÍA")

        self._metricas: dict[str, tk.StringVar] = {}
        metricas_def = [
            ("distancia",    "Distancia (pasos)", "—"),
            ("tiempo",       "Tiempo (ms)",       "—"),
            ("nodos",        "Nodos expandidos",  "—"),
            ("encontrado",   "Resultado",         "—"),
        ]

        for clave, etiqueta, valor_ini in metricas_def:
            var = tk.StringVar(value=valor_ini)
            self._metricas[clave] = var
            fila = tk.Frame(panel, bg=COLOR_PANEL)
            fila.pack(fill="x", padx=14, pady=3)
            tk.Label(
                fila,
                text=etiqueta,
                font=("Courier", 9),
                fg=COLOR_TEXTO_DIM,
                bg=COLOR_PANEL,
                anchor="w",
                width=18,
            ).pack(side="left")
            tk.Label(
                fila,
                textvariable=var,
                font=("Courier", 10, "bold"),
                fg=COLOR_TEXTO,
                bg=COLOR_PANEL,
                anchor="e",
            ).pack(side="right")

        # ── Sección: Velocidad ──
        seccion("▸ VELOCIDAD")

        vel_frame = tk.Frame(panel, bg=COLOR_PANEL)
        vel_frame.pack(fill="x", padx=14, pady=(6, 2))

        self._lbl_vel = tk.Label(
            vel_frame,
            text="8 ms/paso",
            font=("Courier", 9),
            fg=COLOR_TEXTO,
            bg=COLOR_PANEL,
            anchor="e",
        )
        self._lbl_vel.pack(side="right")

        tk.Label(
            vel_frame,
            text="Delay anim.",
            font=("Courier", 9),
            fg=COLOR_TEXTO_DIM,
            bg=COLOR_PANEL,
            anchor="w",
        ).pack(side="left")

        self._var_velocidad = tk.IntVar(value=DELAY_ANIMACION)
        self._slider_vel = tk.Scale(
            panel,
            from_=1,
            to=100,
            orient="horizontal",
            variable=self._var_velocidad,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            troughcolor="#1A2940",
            highlightthickness=0,
            bd=0,
            sliderrelief="flat",
            font=("Courier", 8),
            showvalue=False,
            command=self._on_velocidad_cambia,
        )
        self._slider_vel.pack(fill="x", padx=14, pady=(0, 4))

        vel_labels = tk.Frame(panel, bg=COLOR_PANEL)
        vel_labels.pack(fill="x", padx=14)
        tk.Label(
            vel_labels, text="Rápido", font=("Courier", 7),
            fg=COLOR_TEXTO_DIM, bg=COLOR_PANEL, anchor="w",
        ).pack(side="left")
        tk.Label(
            vel_labels, text="Lento", font=("Courier", 7),
            fg=COLOR_TEXTO_DIM, bg=COLOR_PANEL, anchor="e",
        ).pack(side="right")

        # ── Leyenda ──
        seccion("▸ LEYENDA")
        leyenda = [
            (COLOR_INICIO,   "Inicio"),
            (COLOR_FIN,      "Fin"),
            (COLOR_PARED,    "Pared"),
            (COLOR_VISITADO, "Explorado"),
            (COLOR_CAMINO,   "Camino"),
        ]
        for color, texto in leyenda:
            fila = tk.Frame(panel, bg=COLOR_PANEL)
            fila.pack(fill="x", padx=14, pady=2)
            tk.Canvas(
                fila, width=14, height=14,
                bg=color, highlightthickness=0,
            ).pack(side="left", padx=(0, 6))
            tk.Label(
                fila, text=texto,
                font=("Courier", 9), fg=COLOR_TEXTO_DIM, bg=COLOR_PANEL,
            ).pack(side="left")

        # ── Instrucciones ──
        seccion("▸ CONTROLES")
        instrucciones = [
            "Clic izq  → pared",
            "Arrastrar → pintar",
            "Clic der  → inicio/fin",
        ]
        for txt in instrucciones:
            tk.Label(
                panel, text=txt,
                font=("Courier", 8), fg=COLOR_TEXTO_DIM, bg=COLOR_PANEL, anchor="w",
            ).pack(fill="x", padx=14, pady=1)

    def _boton(self, padre, texto, bg, fg, comando):
        btn = tk.Button(
            padre,
            text=texto,
            font=("Courier", 10, "bold"),
            bg=bg,
            fg=fg,
            activebackground=COLOR_BORDE,
            activeforeground=COLOR_TEXTO,
            relief="flat",
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
            command=comando,
        )
        btn.pack(fill="x", padx=14, pady=4)
        return btn

    # ── Dibujo ───────────────────────────────────────────────────────────────

    def _color_celda(self, f: int, c: int) -> str:
        if (f, c) == self.inicio:
            return COLOR_INICIO
        if (f, c) == self.fin:
            return COLOR_FIN
        if self.grilla[f][c]:
            return COLOR_PARED
        return COLOR_CELDA

    def _dibujar_grilla_completa(self):
        for f in range(FILAS):
            for c in range(COLS):
                self.canvas.itemconfig(
                    self._rect_ids[f][c],
                    fill=self._color_celda(f, c),
                )

    def _pintar_celda(self, f: int, c: int, color: str):
        self.canvas.itemconfig(self._rect_ids[f][c], fill=color)

    # ── Eventos del canvas ────────────────────────────────────────────────────

    def _celda_desde_evento(self, event) -> tuple[int, int] | None:
        c = event.x // TAM_CELDA
        f = event.y // TAM_CELDA
        if 0 <= f < FILAS and 0 <= c < COLS:
            return f, c
        return None

    def _auto_limpiar_resultado(self):
        """Si hay un resultado visible en pantalla, limpiarlo antes de editar."""
        if any(self._metricas[k].get() != "—" for k in self._metricas):
            self._limpiar_camino()

    def _on_click_izq(self, event):
        if self._ejecutando:
            return
        celda = self._celda_desde_evento(event)
        if celda is None or celda in (self.inicio, self.fin):
            return
        self._auto_limpiar_resultado()
        f, c = celda
        # Alternar pared
        nuevo = not self.grilla[f][c]
        self.grilla[f][c] = nuevo
        self._drag_mode = "pared" if nuevo else "borrar"
        self._pintar_celda(f, c, COLOR_PARED if nuevo else COLOR_CELDA)

    def _on_drag(self, event):
        if self._ejecutando or self._drag_mode is None:
            return
        celda = self._celda_desde_evento(event)
        if celda is None or celda in (self.inicio, self.fin):
            return
        f, c = celda
        poner_pared = self._drag_mode == "pared"
        if self.grilla[f][c] != poner_pared:
            self.grilla[f][c] = poner_pared
            self._pintar_celda(f, c, COLOR_PARED if poner_pared else COLOR_CELDA)

    def _on_click_der(self, event):
        if self._ejecutando:
            return
        celda = self._celda_desde_evento(event)
        if celda is None:
            return
        self._auto_limpiar_resultado()
        f, c = celda
        if self.grilla[f][c]:
            return  # No colocar inicio/fin sobre una pared

        if (f, c) == self.inicio:
            # Quitar inicio
            self.inicio = None
            self._pintar_celda(f, c, COLOR_CELDA)
        elif (f, c) == self.fin:
            # Quitar fin
            self.fin = None
            self._pintar_celda(f, c, COLOR_CELDA)
        elif self.inicio is None:
            # Poner inicio
            self.inicio = (f, c)
            self._pintar_celda(f, c, COLOR_INICIO)
        elif self.fin is None:
            # Poner fin
            self.fin = (f, c)
            self._pintar_celda(f, c, COLOR_FIN)
        else:
            # Ciclar: quitar inicio primero
            self._pintar_celda(*self.inicio, COLOR_CELDA)
            self.inicio = self.fin
            self.fin = (f, c)
            self._pintar_celda(*self.inicio, COLOR_INICIO)
            self._pintar_celda(*self.fin, COLOR_FIN)

    # ── Lógica de ejecución ───────────────────────────────────────────────────

    def _iniciar(self):
        if self._ejecutando:
            return
        if self.inicio is None or self.fin is None:
            messagebox.showwarning(
                "Faltan puntos",
                "Coloca un punto de inicio y uno de fin\n(clic derecho sobre el tablero).",
            )
            return

        nombre = self._var_algo.get()
        ClaseAlgo = self.algoritmos.get(nombre)
        if ClaseAlgo is None:
            messagebox.showerror("Error", f"Algoritmo '{nombre}' no encontrado.")
            return

        self._limpiar_camino()
        self._set_controles(False)
        self._actualizar_estado(f"Ejecutando {nombre}...")

        t0 = time.perf_counter()
        algo = ClaseAlgo(self.grilla, self.inicio, self.fin)
        resultado = algo.buscar()
        t1 = time.perf_counter()
        tiempo_ms = (t1 - t0) * 1000

        self._metricas["tiempo"].set(f"{tiempo_ms:.2f} ms")
        self._metricas["nodos"].set(str(resultado.nodos_expandidos))
        self._metricas["distancia"].set(
            str(resultado.distancia) if resultado.encontrado else "—"
        )
        self._metricas["encontrado"].set(
            "✓ Encontrado" if resultado.encontrado else "✗ Sin camino"
        )

        # Animación de nodos visitados
        self._ejecutando = True
        self._animar_visitados(resultado.visitados, resultado.camino, 0)

    def _animar_visitados(
        self,
        visitados: list[tuple[int, int]],
        camino: list[tuple[int, int]],
        idx: int,
    ):
        if idx < len(visitados):
            f, c = visitados[idx]
            if (f, c) not in (self.inicio, self.fin):
                self._pintar_celda(f, c, COLOR_VISITADO)
            self._animacion_id = self.after(
                self._var_velocidad.get(),
                self._animar_visitados,
                visitados,
                camino,
                idx + 1,
            )
        else:
            # Dibujar camino final
            for f, c in camino:
                if (f, c) not in (self.inicio, self.fin):
                    self._pintar_celda(f, c, COLOR_CAMINO)
            self._ejecutando = False
            self._set_controles(True)
            if camino:
                self._actualizar_estado(
                    f"Listo. Camino encontrado en {len(camino)-1} pasos."
                )
            else:
                self._actualizar_estado("No existe camino entre inicio y fin.")

    def _limpiar_camino(self):
        if self._animacion_id:
            self.after_cancel(self._animacion_id)
            self._animacion_id = None
        self._ejecutando = False
        for f in range(FILAS):
            for c in range(COLS):
                if (f, c) not in (self.inicio, self.fin) and not self.grilla[f][c]:
                    self._pintar_celda(f, c, COLOR_CELDA)
        for clave in self._metricas:
            self._metricas[clave].set("—")
        self._actualizar_estado("Camino limpiado. Listo para ejecutar.")

    def _generar_laberinto(self):
        if self._ejecutando:
            return
        self._limpiar_camino()
        self.grilla = generar_laberinto(FILAS, COLS)
        self.inicio = self._buscar_libre_desde(
            FILAS - 1, 0,
            rango_f=range(FILAS - 1, -1, -1), rango_c=range(COLS),
        )
        self.fin = self._buscar_libre_desde(
            0, COLS // 2,
            rango_f=range(FILAS), rango_c=range(COLS // 2, -1, -1),
        )
        self._dibujar_grilla_completa()
        self._actualizar_estado("Laberinto generado. Seleccioná un algoritmo e Iniciar.")

    def _on_velocidad_cambia(self, _val):
        ms = self._var_velocidad.get()
        self._lbl_vel.config(text=f"{ms} ms/paso")

    def _set_controles(self, habilitado: bool):
        estado = "normal" if habilitado else "disabled"
        self._btn_iniciar.config(state=estado)
        self._btn_limpiar.config(state=estado)
        self._btn_generar.config(state=estado)
        self._combo.config(state="readonly" if habilitado else "disabled")

    def _actualizar_estado(self, texto: str):
        self._lbl_estado.config(text=texto)


# ── Punto de entrada ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
