"""
Componente selector de fuente tipográfica.
Permite al usuario elegir entre fuentes disponibles del sistema.
"""
import flet as ft
import os
from typing import Callable, List, Optional, Tuple

from configuracion.constantes import (
    COLOR_FONDO_TARJETA,
    COLOR_TEXTO_PRINCIPAL,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_BORDE,
    COLOR_ACENTO_PRIMARIO,
    RADIO_BORDE,
    RUTA_FUENTES,
)


FUENTES_PREDETERMINADAS = [
    ("Roboto Bold", "Roboto-Bold.ttf"),
    ("Roboto Regular", "Roboto-Regular.ttf"),
    ("Arial", "arial.ttf"),
    ("Arial Bold", "arialbd.ttf"),
    ("Times New Roman", "times.ttf"),
    ("Verdana", "verdana.ttf"),
    ("Georgia", "georgia.ttf"),
    ("Trebuchet MS", "trebuc.ttf"),
    ("Impact", "impact.ttf"),
]


class SelectorFuente(ft.Column):
    """Selector de fuente tipográfica con dropdown y vista previa del texto."""

    def __init__(
        self,
        titulo: str = "Fuente",
        al_cambiar: Optional[Callable[[str], None]] = None,
        fuente_inicial: str = "Roboto-Bold.ttf",
    ):
        super().__init__()
        self.titulo = titulo
        self.al_cambiar = al_cambiar
        self.fuente_actual = fuente_inicial

        # Detectar fuentes disponibles
        self._fuentes_disponibles = self._detectar_fuentes()

        opciones = [
            ft.dropdown.Option(key=ruta, text=nombre)
            for nombre, ruta in self._fuentes_disponibles
        ]

        self._dropdown = ft.Dropdown(
            options=opciones,
            value=fuente_inicial,
            width=250,
            height=45,
            text_size=13,
            border_color=COLOR_BORDE,
            focused_border_color=COLOR_ACENTO_PRIMARIO,
            color=COLOR_TEXTO_PRINCIPAL,
            bgcolor="#0a0a1a",
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
            on_change=self._al_cambiar_fuente,
        )

        self._preview_texto = ft.Text(
            "Producto $99.99",
            size=16,
            color=COLOR_TEXTO_PRINCIPAL,
        )

        self.spacing = 6
        self.controls = [
            ft.Text(
                self.titulo,
                size=13,
                weight=ft.FontWeight.W_600,
                color=COLOR_TEXTO_PRINCIPAL,
            ),
            self._dropdown,
            ft.Container(
                content=self._preview_texto,
                padding=ft.padding.all(8),
                border_radius=6,
                bgcolor="#0a0a1a",
                border=ft.border.all(1, COLOR_BORDE),
            ),
        ]

    def _detectar_fuentes(self) -> List[Tuple[str, str]]:
        """Detecta fuentes disponibles en el sistema y en la carpeta de assets."""
        fuentes = []

        # Fuentes en la carpeta del proyecto
        if os.path.isdir(RUTA_FUENTES):
            for archivo in os.listdir(RUTA_FUENTES):
                if archivo.lower().endswith(('.ttf', '.otf')):
                    nombre = os.path.splitext(archivo)[0].replace("-", " ").replace("_", " ")
                    ruta_completa = os.path.join(RUTA_FUENTES, archivo)
                    fuentes.append((nombre, ruta_completa))

        # Fuentes del sistema (Windows)
        ruta_fuentes_windows = "C:/Windows/Fonts"
        for nombre_visible, nombre_archivo in FUENTES_PREDETERMINADAS:
            ruta_sistema = os.path.join(ruta_fuentes_windows, nombre_archivo)
            ruta_assets = os.path.join(RUTA_FUENTES, nombre_archivo)

            # Evitar duplicados
            ya_existe = any(n == nombre_visible for n, _ in fuentes)
            if ya_existe:
                continue

            if os.path.isfile(ruta_assets):
                fuentes.append((nombre_visible, ruta_assets))
            elif os.path.isfile(ruta_sistema):
                fuentes.append((nombre_visible, ruta_sistema))
            else:
                # Intentar cargar directamente por nombre
                fuentes.append((nombre_visible, nombre_archivo))

        if not fuentes:
            fuentes.append(("Predeterminada", "default"))

        return fuentes

    def _al_cambiar_fuente(self, e):
        """Maneja el cambio de fuente."""
        self.fuente_actual = e.control.value
        if self.al_cambiar:
            self.al_cambiar(self.fuente_actual)

    def obtener_fuente(self) -> str:
        """Retorna la ruta de la fuente actual."""
        return self.fuente_actual
