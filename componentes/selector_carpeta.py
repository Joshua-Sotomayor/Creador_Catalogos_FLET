"""
Componente de selección de carpetas y archivos reutilizable.
Responsive: se adapta al ancho disponible.
"""
import flet as ft
from typing import Callable, Optional, List

from configuracion.constantes import (
    COLOR_FONDO_TARJETA,
    COLOR_ACENTO_PRIMARIO,
    COLOR_TEXTO_PRINCIPAL,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_BORDE,
    COLOR_EXITO,
    RADIO_BORDE,
)


class SelectorCarpeta(ft.UserControl):
    """Componente reutilizable para seleccionar carpetas o archivos.
    Se adapta al ancho del contenedor padre."""

    def __init__(
        self,
        pagina: ft.Page,
        etiqueta: str,
        descripcion: str = "",
        tipo: str = "carpeta",  # "carpeta", "archivo", "archivos_multiples"
        extensiones_permitidas: Optional[List[str]] = None,
        al_seleccionar: Optional[Callable[[str], None]] = None,
        icono: str = ft.Icons.FOLDER_OPEN,
    ):
        super().__init__()
        self.pagina = pagina
        self.etiqueta = etiqueta
        self.descripcion = descripcion
        self.tipo = tipo
        self.extensiones_permitidas = extensiones_permitidas
        self.al_seleccionar = al_seleccionar
        self.icono = icono
        self.ruta_seleccionada = None
        self.rutas_seleccionadas = []

        self._etiqueta_ruta = ft.Text(
            "Sin seleccionar — haz click para elegir",
            size=12,
            color=COLOR_TEXTO_SECUNDARIO,
        )

        self._indicador_estado = ft.Icon(
            ft.Icons.RADIO_BUTTON_UNCHECKED,
            color=COLOR_TEXTO_SECUNDARIO,
            size=18,
        )

        self._selector = ft.FilePicker(on_result=self._al_resultado)

    def did_mount(self):
        if self._selector not in self.pagina.overlay:
            self.pagina.overlay.append(self._selector)
            self.pagina.update()

    def will_unmount(self):
        if self._selector in self.pagina.overlay:
            self.pagina.overlay.remove(self._selector)
            self.pagina.update()

    def build(self):
        self.tarjeta = self._construir_tarjeta()
        return self.tarjeta

    def _construir_tarjeta(self) -> ft.Container:
        """Construye la tarjeta visual del selector — 100% ancho."""

        info_columna = ft.Column(
            controls=[
                ft.Text(
                    self.etiqueta,
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=COLOR_TEXTO_PRINCIPAL,
                ),
            ] + ([
                ft.Text(
                    self.descripcion,
                    size=11,
                    color=COLOR_TEXTO_SECUNDARIO,
                )
            ] if self.descripcion else []) + [
                self._etiqueta_ruta,
            ],
            spacing=3,
        )

        contenido_fila = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(self.icono, color=COLOR_ACENTO_PRIMARIO, size=24),
                    width=44,
                    height=44,
                    border_radius=10,
                    bgcolor="#2a101f", # Color oscuro estático en lugar de opacidad mal calculada
                    alignment=ft.alignment.center,
                ),
                ft.Container(content=info_columna, expand=True),
                self._indicador_estado,
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Container(
            content=contenido_fila,
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            border_radius=RADIO_BORDE,
            border=ft.border.all(1, COLOR_BORDE),
            bgcolor=COLOR_FONDO_TARJETA,
            on_click=self._al_clickear,
            ink=True,
            on_hover=self._al_hover,
        )

    def _al_hover(self, e: ft.HoverEvent):
        """Maneja el evento hover sobre la tarjeta."""
        contenedor = e.control
        if e.data == "true":
            contenedor.border = ft.border.all(1.5, COLOR_ACENTO_PRIMARIO)
            contenedor.bgcolor = "#1a1a3a"
        else:
            contenedor.border = ft.border.all(1, COLOR_BORDE)
            contenedor.bgcolor = COLOR_FONDO_TARJETA
        contenedor.update()

    def _al_clickear(self, e):
        """Abre el diálogo de selección según el tipo."""
        if self.tipo == "carpeta":
            self._selector.get_directory_path(dialog_title=self.etiqueta)
        elif self.tipo == "archivo":
            self._selector.pick_files(
                dialog_title=self.etiqueta,
                allowed_extensions=self.extensiones_permitidas,
                allow_multiple=False,
            )
        elif self.tipo == "archivos_multiples":
            self._selector.pick_files(
                dialog_title=self.etiqueta,
                allowed_extensions=self.extensiones_permitidas,
                allow_multiple=True,
            )

    def _al_resultado(self, e: ft.FilePickerResultEvent):
        """Procesa el resultado de la selección."""
        if self.tipo == "carpeta":
            if e.path:
                self.ruta_seleccionada = e.path
                self._actualizar_ui_seleccion(e.path)
                if self.al_seleccionar:
                    self.al_seleccionar(e.path)
        elif self.tipo == "archivo":
            if e.files and len(e.files) > 0:
                self.ruta_seleccionada = e.files[0].path
                self._actualizar_ui_seleccion(e.files[0].path)
                if self.al_seleccionar:
                    self.al_seleccionar(e.files[0].path)
        elif self.tipo == "archivos_multiples":
            if e.files:
                self.rutas_seleccionadas = [f.path for f in e.files]
                texto = f"✅ {len(e.files)} archivo(s) seleccionado(s)"
                self._actualizar_ui_seleccion(texto)
                if self.al_seleccionar:
                    self.al_seleccionar(self.rutas_seleccionadas)

    def _actualizar_ui_seleccion(self, texto_ruta: str):
        """Actualiza la UI para reflejar la selección."""
        self._etiqueta_ruta.value = f"📂 {texto_ruta}"
        self._etiqueta_ruta.color = COLOR_EXITO
        self._indicador_estado.name = ft.Icons.CHECK_CIRCLE
        self._indicador_estado.color = COLOR_EXITO
        self.update()

    def reiniciar(self):
        """Reinicia el selector a su estado inicial."""
        self.ruta_seleccionada = None
        self.rutas_seleccionadas = []
        self._etiqueta_ruta.value = "Sin seleccionar — haz click para elegir"
        self._etiqueta_ruta.color = COLOR_TEXTO_SECUNDARIO
        self._indicador_estado.name = ft.Icons.RADIO_BUTTON_UNCHECKED
        self._indicador_estado.color = COLOR_TEXTO_SECUNDARIO
        self.update()
