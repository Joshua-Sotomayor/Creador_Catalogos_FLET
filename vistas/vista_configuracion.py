"""
Vista de configuración inicial (Paso 1).
El usuario selecciona carpetas, archivos de precios y opciones generales.
"""
import flet as ft
from typing import Callable, Optional

from configuracion.constantes import (
    COLOR_FONDO_PRINCIPAL,
    COLOR_FONDO_SECUNDARIO,
    COLOR_FONDO_TARJETA,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_TEXTO_PRINCIPAL,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_BORDE,
    COLOR_EXITO,
    COLOR_ERROR,
    RADIO_BORDE,
    ESPACIADO_GENERAL,
)
from componentes.selector_carpeta import SelectorCarpeta


class VistaConfiguracion(ft.Column):
    """
    Pantalla de configuración inicial del catálogo.
    Permite al usuario seleccionar:
    - Carpeta madre de productos
    - Carpeta de fondos por categoría
    - Opción de incluir nombre del producto
    - Carpeta/imagen de fondo para precios
    - Archivo de precios (txt/csv)
    """

    def __init__(
        self,
        pagina: ft.Page,
        al_iniciar_proceso: Optional[Callable] = None,
    ):
        super().__init__()
        self.pagina = pagina
        self.al_iniciar_proceso = al_iniciar_proceso

        # Estado
        self._ruta_carpeta_madre = None
        self._ruta_carpeta_fondos = None
        self._ruta_carpeta_fondos_precio = None
        self._ruta_fondo_precio_unico = None
        self._ruta_archivo_precios = None
        self._rutas_imagenes_fondo_precio_manual = []
        self._ruta_imagen_individual = None
        self._incluir_nombre = True
        self._modo_entrada = "carpeta"  # "carpeta" o "individual"

        # Construir UI
        self.scroll = ft.ScrollMode.AUTO
        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 0
        self.controls = [self._construir_contenido()]

    def _construir_contenido(self) -> ft.Container:
        """Construye todo el contenido de la vista."""

        # === Encabezado ===
        encabezado = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.AUTO_AWESOME, color=COLOR_ACENTO_PRIMARIO, size=32),
                            ft.Text(
                                "CatalogoCreator",
                                size=28,
                                weight=ft.FontWeight.W_800,
                                color=COLOR_TEXTO_PRINCIPAL,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    ft.Text(
                        "Crea catálogos de productos profesionales en minutos",
                        size=14,
                        color=COLOR_TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.padding.symmetric(vertical=30),
        )

        # === Selector de modo de entrada ===
        self._segmento_modo = ft.SegmentedButton(
            selected={"carpeta"},
            segments=[
                ft.Segment(
                    value="carpeta",
                    label=ft.Text("Carpeta de productos"),
                    icon=ft.Icon(ft.Icons.FOLDER),
                ),
                ft.Segment(
                    value="individual",
                    label=ft.Text("Imagen individual"),
                    icon=ft.Icon(ft.Icons.IMAGE),
                ),
            ],
            on_change=self._al_cambiar_modo_entrada,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.SELECTED: COLOR_ACENTO_PRIMARIO,
                },
            ),
        )

        seccion_modo = self._crear_seccion(
            "Modo de entrada",
            "Selecciona si quieres procesar una carpeta completa o una imagen individual",
            [self._segmento_modo],
        )

        # === Sección: Carpetas principales (obligatorias) ===
        self._selector_carpeta_madre = SelectorCarpeta(
            pagina=self.pagina,
            etiqueta="Carpeta madre de productos",
            descripcion="Carpeta con subcarpetas por categoría. Cada imagen = un producto.",
            tipo="carpeta",
            al_seleccionar=self._al_seleccionar_carpeta_madre,
            icono=ft.Icons.FOLDER_SPECIAL,
        )

        self._selector_imagen_individual = SelectorCarpeta(
            pagina=self.pagina,
            etiqueta="Imagen individual",
            descripcion="Selecciona una imagen de producto.",
            tipo="archivo",
            extensiones_permitidas=["png", "jpg", "jpeg", "webp", "bmp"],
            al_seleccionar=self._al_seleccionar_imagen_individual,
            icono=ft.Icons.IMAGE,
        )
        self._selector_imagen_individual.visible = False

        self._selector_fondos = SelectorCarpeta(
            pagina=self.pagina,
            etiqueta="Carpeta de fondos por categoría",
            descripcion="Subcarpetas con fondos. El nombre de la subcarpeta = categoría.",
            tipo="carpeta",
            al_seleccionar=self._al_seleccionar_fondos,
            icono=ft.Icons.WALLPAPER,
        )

        seccion_obligatoria = self._crear_seccion(
            "📁 Archivos principales",
            "Estas carpetas son necesarias para crear el catálogo",
            [
                self._selector_carpeta_madre,
                self._selector_imagen_individual,
                self._selector_fondos,
            ],
        )

        # === Sección: Nombre del producto ===
        self._switch_nombre = ft.Switch(
            label="Incluir nombre del producto en la imagen",
            value=True,
            active_color=COLOR_ACENTO_PRIMARIO,
            label_style=ft.TextStyle(color=COLOR_TEXTO_PRINCIPAL, size=13),
            on_change=self._al_cambiar_incluir_nombre,
        )

        seccion_nombre = self._crear_seccion(
            "✏️ Nombre del producto",
            "El nombre se toma del nombre del archivo de imagen (sin extensión)",
            [self._switch_nombre],
        )

        # === Sección: Fondos de precio (opcional) ===
        self._selector_fondos_precio = SelectorCarpeta(
            pagina=self.pagina,
            etiqueta="Carpeta de fondos para precio (por categoría)",
            descripcion="Subcarpetas con imágenes decorativas para el etiquetado del precio.",
            tipo="carpeta",
            al_seleccionar=self._al_seleccionar_fondos_precio,
            icono=ft.Icons.PRICE_CHANGE,
        )

        self._selector_fondo_precio_unico = SelectorCarpeta(
            pagina=self.pagina,
            etiqueta="O imagen única de fondo para todos los precios",
            descripcion="Una sola imagen que se usará para encerrar el precio de todos los productos.",
            tipo="archivo",
            extensiones_permitidas=["png", "jpg", "jpeg", "webp"],
            al_seleccionar=self._al_seleccionar_fondo_precio_unico,
            icono=ft.Icons.PRICE_CHECK,
        )

        self._selector_imagenes_precio_manual = SelectorCarpeta(
            pagina=self.pagina,
            etiqueta="O seleccionar imágenes manualmente",
            descripcion="Selecciona múltiples imágenes para ir eligiendo durante la edición.",
            tipo="archivos_multiples",
            extensiones_permitidas=["png", "jpg", "jpeg", "webp"],
            al_seleccionar=self._al_seleccionar_imagenes_precio_manual,
            icono=ft.Icons.COLLECTIONS,
        )

        seccion_fondo_precio = self._crear_seccion(
            "🏷️ Fondo decorativo para precio (opcional)",
            "Imagen decorativa que encierra el precio. Puedes elegir una de las tres opciones.",
            [
                self._selector_fondos_precio,
                ft.Divider(height=1, color=COLOR_BORDE),
                self._selector_fondo_precio_unico,
                ft.Divider(height=1, color=COLOR_BORDE),
                self._selector_imagenes_precio_manual,
            ],
        )

        # === Sección: Archivo de precios ===
        self._selector_precios = SelectorCarpeta(
            pagina=self.pagina,
            etiqueta="Archivo de precios (txt o csv)",
            descripcion="Un precio por línea. Se emparejan con las imágenes en orden.",
            tipo="archivo",
            extensiones_permitidas=["txt", "csv"],
            al_seleccionar=self._al_seleccionar_precios,
            icono=ft.Icons.ATTACH_MONEY,
        )

        seccion_precios = self._crear_seccion(
            "💰 Archivo de precios (opcional)",
            "Si no cargas un archivo, podrás ingresar precios manualmente",
            [self._selector_precios],
        )

        # === Botón iniciar ===
        self._mensaje_estado = ft.Text(
            "",
            size=12,
            color=COLOR_ERROR,
            text_align=ft.TextAlign.CENTER,
        )

        boton_iniciar = ft.Container(
            content=ft.ElevatedButton(
                "🚀 Iniciar proceso",
                style=ft.ButtonStyle(
                    bgcolor=COLOR_ACENTO_PRIMARIO,
                    color=COLOR_TEXTO_PRINCIPAL,
                    padding=ft.padding.symmetric(horizontal=40, vertical=16),
                    shape=ft.RoundedRectangleBorder(radius=RADIO_BORDE),
                    text_style=ft.TextStyle(size=16, weight=ft.FontWeight.W_700),
                    elevation=4,
                    animation_duration=200,
                ),
                on_click=self._al_iniciar,
            ),
            padding=ft.padding.symmetric(vertical=20),
            alignment=ft.alignment.center,
        )

        # === Contenedor principal ===
        return ft.Container(
            content=ft.Column(
                controls=[
                    encabezado,
                    seccion_modo,
                    seccion_obligatoria,
                    seccion_nombre,
                    seccion_fondo_precio,
                    seccion_precios,
                    self._mensaje_estado,
                    boton_iniciar,
                ],
                spacing=ESPACIADO_GENERAL,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=40, vertical=20),
            expand=True,
            width=700,
            alignment=ft.alignment.top_center,
        )

    def _crear_seccion(self, titulo: str, descripcion: str, controles: list) -> ft.Container:
        """Crea una sección visual con título, descripción y controles."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        titulo,
                        size=16,
                        weight=ft.FontWeight.W_700,
                        color=COLOR_TEXTO_PRINCIPAL,
                    ),
                    ft.Text(
                        descripcion,
                        size=12,
                        color=COLOR_TEXTO_SECUNDARIO,
                    ),
                    ft.Column(controls=controles, spacing=8),
                ],
                spacing=10,
            ),
            padding=ft.padding.all(20),
            border_radius=RADIO_BORDE,
            bgcolor=COLOR_FONDO_SECUNDARIO,
            border=ft.border.all(1, COLOR_BORDE),
        )

    # === Callbacks de selección ===

    def _al_cambiar_modo_entrada(self, e):
        """Cambia entre modo carpeta e imagen individual."""
        seleccionado = list(e.control.selected)[0] if e.control.selected else "carpeta"
        self._modo_entrada = seleccionado
        self._selector_carpeta_madre.visible = seleccionado == "carpeta"
        self._selector_imagen_individual.visible = seleccionado == "individual"
        self._selector_carpeta_madre.update()
        self._selector_imagen_individual.update()

    def _al_seleccionar_carpeta_madre(self, ruta: str):
        self._ruta_carpeta_madre = ruta

    def _al_seleccionar_imagen_individual(self, ruta: str):
        self._ruta_imagen_individual = ruta

    def _al_seleccionar_fondos(self, ruta: str):
        self._ruta_carpeta_fondos = ruta

    def _al_seleccionar_fondos_precio(self, ruta: str):
        self._ruta_carpeta_fondos_precio = ruta

    def _al_seleccionar_fondo_precio_unico(self, ruta: str):
        self._ruta_fondo_precio_unico = ruta

    def _al_seleccionar_imagenes_precio_manual(self, rutas):
        self._rutas_imagenes_fondo_precio_manual = rutas if isinstance(rutas, list) else []

    def _al_seleccionar_precios(self, ruta: str):
        self._ruta_archivo_precios = ruta

    def _al_cambiar_incluir_nombre(self, e):
        self._incluir_nombre = e.control.value

    def _al_iniciar(self, e):
        """Valida y lanza el proceso."""
        # Cláusulas de guarda
        if self._modo_entrada == "carpeta" and not self._ruta_carpeta_madre:
            self._mostrar_error("Selecciona la carpeta madre de productos.")
            return

        if self._modo_entrada == "individual" and not self._ruta_imagen_individual:
            self._mostrar_error("Selecciona una imagen de producto.")
            return

        if not self._ruta_carpeta_fondos:
            self._mostrar_error("Selecciona la carpeta de fondos por categoría.")
            return

        self._mensaje_estado.value = ""
        self._mensaje_estado.update()

        if self.al_iniciar_proceso:
            self.al_iniciar_proceso(self.obtener_configuracion())

    def _mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error."""
        self._mensaje_estado.value = f"⚠️ {mensaje}"
        self._mensaje_estado.color = COLOR_ERROR
        self._mensaje_estado.update()

    def obtener_configuracion(self) -> dict:
        """Retorna la configuración seleccionada como diccionario."""
        return {
            "modo_entrada": self._modo_entrada,
            "ruta_carpeta_madre": self._ruta_carpeta_madre,
            "ruta_imagen_individual": self._ruta_imagen_individual,
            "ruta_carpeta_fondos": self._ruta_carpeta_fondos,
            "ruta_carpeta_fondos_precio": self._ruta_carpeta_fondos_precio,
            "ruta_fondo_precio_unico": self._ruta_fondo_precio_unico,
            "rutas_imagenes_fondo_precio_manual": self._rutas_imagenes_fondo_precio_manual,
            "ruta_archivo_precios": self._ruta_archivo_precios,
            "incluir_nombre": self._incluir_nombre,
        }
