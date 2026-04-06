"""
Componente selector de color con propuesta automática y selección manual.
"""
import flet as ft
from typing import Callable, Optional, Tuple

from configuracion.constantes import (
    COLOR_FONDO_TARJETA,
    COLOR_TEXTO_PRINCIPAL,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_BORDE,
    RADIO_BORDE,
)
from utilidades.ayudantes_imagen import rgb_a_hex, hex_a_rgb


class SelectorColor(ft.Column):
    """Selector de color con vista previa, propuesta automática y entrada manual hex."""

    def __init__(
        self,
        titulo: str = "Color del texto",
        color_inicial: Tuple[int, int, int] = (255, 255, 255),
        al_cambiar: Optional[Callable[[Tuple[int, int, int]], None]] = None,
    ):
        super().__init__()
        self.titulo = titulo
        self.color_actual = color_inicial
        self.al_cambiar = al_cambiar
        self._color_propuesto = None

        self._muestra_color = ft.Container(
            width=36,
            height=36,
            bgcolor=rgb_a_hex(color_inicial),
            border_radius=8,
            border=ft.border.all(2, COLOR_BORDE),
        )

        self._campo_hex = ft.TextField(
            value=rgb_a_hex(color_inicial),
            width=120,
            height=40,
            text_size=13,
            border_color=COLOR_BORDE,
            focused_border_color="#e94560",
            color=COLOR_TEXTO_PRINCIPAL,
            bgcolor="#0a0a1a",
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
            on_change=self._al_cambiar_hex,
            prefix_text="#",
        )

        self._boton_propuesta = ft.TextButton(
            "Usar propuesta",
            style=ft.ButtonStyle(color=COLOR_TEXTO_SECUNDARIO),
            visible=False,
            on_click=self._al_usar_propuesta,
        )

        # Colores predefinidos rápidos
        colores_rapidos = [
            (255, 255, 255),  # Blanco
            (0, 0, 0),        # Negro
            (255, 215, 0),    # Dorado
            (233, 69, 96),    # Rojo rosado
            (76, 175, 80),    # Verde
            (33, 150, 243),   # Azul
        ]
        self._fila_colores_rapidos = ft.Row(
            controls=[
                ft.Container(
                    width=24,
                    height=24,
                    bgcolor=rgb_a_hex(c),
                    border_radius=12,
                    border=ft.border.all(1, COLOR_BORDE),
                    on_click=lambda e, color=c: self._establecer_color(color),
                    tooltip=rgb_a_hex(c),
                )
                for c in colores_rapidos
            ],
            spacing=4,
        )

        self.spacing = 6
        self.controls = [
            ft.Text(
                self.titulo,
                size=13,
                weight=ft.FontWeight.W_600,
                color=COLOR_TEXTO_PRINCIPAL,
            ),
            ft.Row(
                controls=[self._muestra_color, self._campo_hex, self._boton_propuesta],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            self._fila_colores_rapidos,
        ]

    def _al_cambiar_hex(self, e):
        """Procesa el cambio de color vía entrada hexadecimal."""
        valor = e.control.value.lstrip("#")
        if len(valor) == 6:
            try:
                color = hex_a_rgb(valor)
                self.color_actual = color
                self._muestra_color.bgcolor = rgb_a_hex(color)
                self._muestra_color.update()
                if self.al_cambiar:
                    self.al_cambiar(color)
            except ValueError:
                pass

    def _establecer_color(self, color: Tuple[int, int, int]):
        """Establece un color directamente."""
        self.color_actual = color
        self._muestra_color.bgcolor = rgb_a_hex(color)
        self._campo_hex.value = rgb_a_hex(color)
        self._muestra_color.update()
        self._campo_hex.update()
        if self.al_cambiar:
            self.al_cambiar(color)

    def establecer_propuesta(self, color: Tuple[int, int, int]):
        """Establece un color propuesto automáticamente."""
        self._color_propuesto = color
        self._boton_propuesta.visible = True
        self._boton_propuesta.text = f"Usar propuesta ({rgb_a_hex(color)})"
        self._boton_propuesta.update()

    def _al_usar_propuesta(self, e):
        """Aplica el color propuesto."""
        if self._color_propuesto:
            self._establecer_color(self._color_propuesto)

    def obtener_color(self) -> Tuple[int, int, int]:
        """Retorna el color actual seleccionado."""
        return self.color_actual
