"""
Componente de galería de imágenes seleccionables.
Muestra una cuadrícula de imágenes que el usuario puede seleccionar.
"""
import flet as ft
import os
from typing import Callable, List, Optional

from configuracion.constantes import (
    COLOR_FONDO_SECUNDARIO,
    COLOR_ACENTO_PRIMARIO,
    COLOR_BORDE,
    COLOR_TEXTO_SECUNDARIO,
    EXTENSIONES_IMAGEN,
    RADIO_BORDE,
)


class GaleriaImagenes(ft.Column):
    """Galería de imágenes seleccionables en formato grid."""

    def __init__(
        self,
        titulo: str = "Galería",
        al_seleccionar: Optional[Callable[[str], None]] = None,
        ancho_miniatura: int = 80,
        alto_miniatura: int = 80,
        max_visible: int = 12,
    ):
        super().__init__()
        self.titulo_galeria = titulo
        self.al_seleccionar = al_seleccionar
        self.ancho_miniatura = ancho_miniatura
        self.alto_miniatura = alto_miniatura
        self.max_visible = max_visible
        self.rutas_imagenes: List[str] = []
        self.ruta_seleccionada: Optional[str] = None
        self._contenedores = {}

        self._grilla = ft.GridView(
            expand=False,
            max_extent=ancho_miniatura + 16,
            child_aspect_ratio=1.0,
            spacing=6,
            run_spacing=6,
            height=200,
        )

        self._etiqueta_conteo = ft.Text(
            "0 imágenes",
            size=11,
            color=COLOR_TEXTO_SECUNDARIO,
        )

        self.spacing = 6
        self.controls = [
            ft.Row(
                controls=[
                    ft.Text(
                        self.titulo_galeria,
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color="#ffffff",
                    ),
                    self._etiqueta_conteo,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(
                content=self._grilla,
                border_radius=RADIO_BORDE,
                border=ft.border.all(1, COLOR_BORDE),
                bgcolor=COLOR_FONDO_SECUNDARIO,
                padding=ft.padding.all(8),
            ),
        ]

    def cargar_desde_carpeta(self, ruta_carpeta: str):
        """Carga imágenes desde una carpeta."""
        if not ruta_carpeta or not os.path.isdir(ruta_carpeta):
            return

        self.rutas_imagenes = []
        for archivo in sorted(os.listdir(ruta_carpeta)):
            ruta_completa = os.path.join(ruta_carpeta, archivo)
            if os.path.isfile(ruta_completa):
                extension = os.path.splitext(archivo)[1].lower()
                if extension in EXTENSIONES_IMAGEN:
                    self.rutas_imagenes.append(ruta_completa)

        self._actualizar_grilla()

    def cargar_desde_lista(self, rutas: List[str]):
        """Carga imágenes desde una lista de rutas."""
        self.rutas_imagenes = [
            r for r in rutas
            if os.path.isfile(r) and os.path.splitext(r)[1].lower() in EXTENSIONES_IMAGEN
        ]
        self._actualizar_grilla()

    def _actualizar_grilla(self):
        """Reconstruye la grilla con las imágenes cargadas."""
        self._grilla.controls.clear()
        self._contenedores.clear()

        for ruta in self.rutas_imagenes[:self.max_visible]:
            contenedor = ft.Container(
                content=ft.Image(
                    src=ruta,
                    width=self.ancho_miniatura,
                    height=self.alto_miniatura,
                    fit=ft.ImageFit.COVER,
                    border_radius=6,
                ),
                width=self.ancho_miniatura + 8,
                height=self.alto_miniatura + 8,
                border_radius=8,
                border=ft.border.all(2, "transparent"),
                padding=ft.padding.all(4),
                on_click=lambda e, r=ruta: self._al_seleccionar_imagen(r),
                animate=ft.animation.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
                ink=True,
            )
            self._contenedores[ruta] = contenedor
            self._grilla.controls.append(contenedor)

        self._etiqueta_conteo.value = f"{len(self.rutas_imagenes)} imagen(es)"
        if self.page:
            self.update()

    def _al_seleccionar_imagen(self, ruta: str):
        """Maneja la selección de una imagen."""
        # Quitar borde de la anterior
        if self.ruta_seleccionada and self.ruta_seleccionada in self._contenedores:
            self._contenedores[self.ruta_seleccionada].border = ft.border.all(2, "transparent")

        # Resaltar la nueva
        self.ruta_seleccionada = ruta
        if ruta in self._contenedores:
            self._contenedores[ruta].border = ft.border.all(2, COLOR_ACENTO_PRIMARIO)

        if self.page:
            self.update()

        if self.al_seleccionar:
            self.al_seleccionar(ruta)

    def obtener_seleccion(self) -> Optional[str]:
        """Retorna la ruta de la imagen seleccionada."""
        return self.ruta_seleccionada
