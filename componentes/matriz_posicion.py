"""
Componente de matriz de posición clickeable (NxN).
Permite seleccionar una celda para posicionar precio o nombre.
"""
import flet as ft
from typing import Callable, Optional, Tuple

from configuracion.constantes import (
    COLOR_CELDA_SELECCIONADA,
    COLOR_CELDA_NORMAL,
    COLOR_CELDA_HOVER,
    COLOR_TEXTO_PRINCIPAL,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_BORDE,
    RADIO_BORDE,
    TAMANO_CELDA_GRILLA,
)


class MatrizPosicion(ft.Column):
    """
    Grilla interactiva de NxN celdas para seleccionar posición.
    Al hacer click en una celda, se resalta y notifica la posición.
    """

    def __init__(
        self,
        filas: int = 5,
        columnas: int = 5,
        titulo: str = "Posición",
        al_seleccionar: Optional[Callable[[Tuple[int, int]], None]] = None,
        celda_seleccionada: Optional[Tuple[int, int]] = None,
        tamano_celda: int = TAMANO_CELDA_GRILLA,
    ):
        super().__init__()
        self.filas = filas
        self.columnas = columnas
        self.titulo = titulo
        self.al_seleccionar = al_seleccionar
        self.celda_seleccionada_actual = celda_seleccionada
        self.tamano_celda = tamano_celda
        self._celdas = {}

        self.spacing = 8
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.controls = self._construir_grilla()

    def _construir_grilla(self) -> list:
        """Construye la grilla de celdas."""
        controles = [
            ft.Text(
                self.titulo,
                size=13,
                weight=ft.FontWeight.W_600,
                color=COLOR_TEXTO_PRINCIPAL,
            )
        ]

        filas_controles = []
        for fila in range(self.filas):
            celdas_fila = []
            for columna in range(self.columnas):
                es_seleccionada = (
                    self.celda_seleccionada_actual == (fila, columna)
                    if self.celda_seleccionada_actual
                    else False
                )

                celda = ft.Container(
                    width=self.tamano_celda,
                    height=self.tamano_celda,
                    bgcolor=COLOR_CELDA_SELECCIONADA if es_seleccionada else COLOR_CELDA_NORMAL,
                    border_radius=4,
                    border=ft.border.all(
                        1,
                        COLOR_CELDA_SELECCIONADA if es_seleccionada else COLOR_BORDE,
                    ),
                    on_click=lambda e, f=fila, c=columna: self._al_click_celda(f, c),
                    on_hover=lambda e, f=fila, c=columna: self._al_hover_celda(e, f, c),
                    animate=ft.animation.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
                    data=(fila, columna),
                )
                self._celdas[(fila, columna)] = celda
                celdas_fila.append(celda)

            filas_controles.append(
                ft.Row(
                    controls=celdas_fila,
                    spacing=3,
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )

        controles.append(
            ft.Container(
                content=ft.Column(controls=filas_controles, spacing=3),
                padding=ft.padding.all(8),
                border_radius=RADIO_BORDE,
                border=ft.border.all(1, COLOR_BORDE),
                bgcolor="#0a0a1a",
            )
        )

        # Etiqueta de celda seleccionada
        self._etiqueta_posicion = ft.Text(
            self._texto_posicion(),
            size=11,
            color=COLOR_TEXTO_SECUNDARIO,
            text_align=ft.TextAlign.CENTER,
        )
        controles.append(self._etiqueta_posicion)

        return controles

    def _texto_posicion(self) -> str:
        """Genera texto descriptivo de la posición seleccionada."""
        if not self.celda_seleccionada_actual:
            return "Sin posición seleccionada"
        fila, columna = self.celda_seleccionada_actual
        return f"Fila {fila + 1}, Columna {columna + 1}"

    def _al_click_celda(self, fila: int, columna: int):
        """Maneja el click en una celda."""
        # Deseleccionar celda anterior
        if self.celda_seleccionada_actual and self.celda_seleccionada_actual in self._celdas:
            celda_anterior = self._celdas[self.celda_seleccionada_actual]
            celda_anterior.bgcolor = COLOR_CELDA_NORMAL
            celda_anterior.border = ft.border.all(1, COLOR_BORDE)

        # Seleccionar nueva celda
        self.celda_seleccionada_actual = (fila, columna)
        celda_nueva = self._celdas[(fila, columna)]
        celda_nueva.bgcolor = COLOR_CELDA_SELECCIONADA
        celda_nueva.border = ft.border.all(1, COLOR_CELDA_SELECCIONADA)

        self._etiqueta_posicion.value = self._texto_posicion()

        self.update()

        if self.al_seleccionar:
            self.al_seleccionar((fila, columna))

    def _al_hover_celda(self, e: ft.HoverEvent, fila: int, columna: int):
        """Maneja el hover sobre una celda."""
        if self.celda_seleccionada_actual == (fila, columna):
            return

        celda = self._celdas[(fila, columna)]
        if e.data == "true":
            celda.bgcolor = COLOR_CELDA_HOVER
            celda.border = ft.border.all(1, COLOR_CELDA_HOVER)
        else:
            celda.bgcolor = COLOR_CELDA_NORMAL
            celda.border = ft.border.all(1, COLOR_BORDE)
        celda.update()

    def obtener_posicion(self) -> Optional[Tuple[int, int]]:
        """Retorna la posición seleccionada actualmente."""
        return self.celda_seleccionada_actual

    def establecer_posicion(self, fila: int, columna: int):
        """Establece la posición seleccionada programáticamente."""
        self._al_click_celda(fila, columna)
