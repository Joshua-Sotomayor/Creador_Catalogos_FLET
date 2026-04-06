"""
Componente de vista previa de imagen.
Muestra una imagen PIL en la interfaz de Flet usando base64.
"""
import flet as ft
from typing import Optional

from PIL import Image

from configuracion.constantes import (
    ALTO_VISTA_PREVIA,
    ANCHO_VISTA_PREVIA,
    COLOR_FONDO_SECUNDARIO,
    COLOR_BORDE,
    COLOR_TEXTO_SECUNDARIO,
    RADIO_BORDE,
)
from utilidades.ayudantes_imagen import imagen_a_base64, redimensionar_para_vista_previa


class VistaPreviaImagen(ft.Column):
    """Componente para mostrar una vista previa de imagen PIL."""

    def __init__(
        self,
        ancho: int = ANCHO_VISTA_PREVIA,
        alto: int = ALTO_VISTA_PREVIA,
        titulo: str = "Vista previa",
    ):
        super().__init__()
        self.ancho_preview = ancho
        self.alto_preview = alto
        self.titulo = titulo
        self._imagen_actual = None

        self._control_imagen = ft.Image(
            width=ancho,
            height=alto,
            fit=ft.ImageFit.CONTAIN,
            border_radius=8,
        )

        self._texto_vacio = ft.Text(
            "Sin imagen para mostrar",
            size=13,
            color=COLOR_TEXTO_SECUNDARIO,
            text_align=ft.TextAlign.CENTER,
        )

        self._contenedor_imagen = ft.Container(
            content=self._texto_vacio,
            width=ancho,
            height=alto,
            bgcolor=COLOR_FONDO_SECUNDARIO,
            border_radius=RADIO_BORDE,
            border=ft.border.all(1, COLOR_BORDE),
            alignment=ft.alignment.center,
        )

        self.spacing = 8
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.controls = [
            ft.Text(
                self.titulo,
                size=13,
                weight=ft.FontWeight.W_600,
                color="#ffffff",
            ),
            self._contenedor_imagen,
        ]

    def actualizar_imagen(self, imagen: Optional[Image.Image]):
        """
        Actualiza la imagen mostrada en la vista previa.

        Args:
            imagen: Imagen PIL a mostrar, o None para limpiar.
        """
        if imagen is None:
            self._contenedor_imagen.content = self._texto_vacio
            self._imagen_actual = None
        else:
            self._imagen_actual = imagen
            imagen_preview = redimensionar_para_vista_previa(
                imagen, self.ancho_preview, self.alto_preview
            )
            datos_base64 = imagen_a_base64(imagen_preview)
            self._control_imagen.src_base64 = datos_base64
            self._contenedor_imagen.content = self._control_imagen

        self._contenedor_imagen.update()

    def obtener_imagen_actual(self) -> Optional[Image.Image]:
        """Retorna la imagen actual."""
        return self._imagen_actual
