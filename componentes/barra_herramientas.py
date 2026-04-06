"""
Componente de barra de herramientas para cambiar entre modos de asignación de precio.
"""
import flet as ft
from typing import Callable, Optional

from configuracion.constantes import (
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_FONDO_TARJETA,
    COLOR_TEXTO_PRINCIPAL,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_BORDE,
    RADIO_BORDE,
    MODO_AUTOMATICO,
    MODO_MANUAL,
    MODO_SELECCION_FONDO,
)


class BarraHerramientas(ft.Container):
    """Barra de botones para cambiar entre modos de edición."""

    def __init__(
        self,
        al_cambiar_modo: Optional[Callable[[str], None]] = None,
        modo_inicial: str = MODO_MANUAL,
    ):
        super().__init__()
        self.al_cambiar_modo = al_cambiar_modo
        self.modo_actual = modo_inicial
        self._botones = {}

        self.content = self._construir_barra()
        self.padding = ft.padding.symmetric(horizontal=8, vertical=4)
        self.border_radius = RADIO_BORDE
        self.bgcolor = COLOR_FONDO_TARJETA
        self.border = ft.border.all(1, COLOR_BORDE)

    def _construir_barra(self) -> ft.Row:
        """Construye la fila de botones de modo."""
        modos = [
            (MODO_AUTOMATICO, "Automático", ft.Icons.AUTO_MODE),
            (MODO_MANUAL, "Manual", ft.Icons.EDIT),
            (MODO_SELECCION_FONDO, "Fondo Precio", ft.Icons.IMAGE),
        ]

        botones = []
        for modo_id, etiqueta, icono in modos:
            es_activo = modo_id == self.modo_actual
            boton = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            icono,
                            size=18,
                            color=COLOR_TEXTO_PRINCIPAL if es_activo else COLOR_TEXTO_SECUNDARIO,
                        ),
                        ft.Text(
                            etiqueta,
                            size=12,
                            weight=ft.FontWeight.W_600 if es_activo else ft.FontWeight.W_400,
                            color=COLOR_TEXTO_PRINCIPAL if es_activo else COLOR_TEXTO_SECUNDARIO,
                        ),
                    ],
                    spacing=6,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                border_radius=8,
                bgcolor=COLOR_ACENTO_PRIMARIO if es_activo else "transparent",
                on_click=lambda e, m=modo_id: self._al_click_modo(m),
                animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
                ink=True,
            )
            self._botones[modo_id] = boton
            botones.append(boton)

        return ft.Row(
            controls=botones,
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def _al_click_modo(self, modo: str):
        """Maneja el cambio de modo."""
        if modo == self.modo_actual:
            return

        # Desactivar botón anterior
        boton_anterior = self._botones.get(self.modo_actual)
        if boton_anterior:
            boton_anterior.bgcolor = "transparent"
            fila = boton_anterior.content
            if isinstance(fila, ft.Row):
                for control in fila.controls:
                    if isinstance(control, ft.Icon):
                        control.color = COLOR_TEXTO_SECUNDARIO
                    elif isinstance(control, ft.Text):
                        control.color = COLOR_TEXTO_SECUNDARIO
                        control.weight = ft.FontWeight.W_400

        # Activar nuevo botón
        self.modo_actual = modo
        boton_nuevo = self._botones.get(modo)
        if boton_nuevo:
            boton_nuevo.bgcolor = COLOR_ACENTO_PRIMARIO
            fila = boton_nuevo.content
            if isinstance(fila, ft.Row):
                for control in fila.controls:
                    if isinstance(control, ft.Icon):
                        control.color = COLOR_TEXTO_PRINCIPAL
                    elif isinstance(control, ft.Text):
                        control.color = COLOR_TEXTO_PRINCIPAL
                        control.weight = ft.FontWeight.W_600

        self.update()

        if self.al_cambiar_modo:
            self.al_cambiar_modo(modo)

    def obtener_modo(self) -> str:
        """Retorna el modo actual."""
        return self.modo_actual
