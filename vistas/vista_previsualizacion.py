"""
Vista de previsualizacion final (Paso 4).
Muestra todas las imagenes finales con botones para editar o guardar.
"""
import flet as ft
from typing import Callable, Dict, List, Optional

from PIL import Image

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
from modelos.producto import Producto
from servicios.servicio_texto import ServicioTexto
from servicios.servicio_deteccion_color import ServicioDeteccionColor
from utilidades.ayudantes_imagen import (
    imagen_a_base64,
    redimensionar_para_vista_previa,
    cargar_imagen,
)


class VistaPrevisualizacion(ft.UserControl):
    """
    Vista de previsualizacion final.
    Muestra las imagenes resultantes con opciones de editar o guardar.
    """

    def __init__(
        self,
        pagina: ft.Page,
        productos: List[Producto],
        imagenes_compuestas: Dict[int, Image.Image],
        al_editar_producto: Optional[Callable[[int], None]] = None,
        al_exportar: Optional[Callable[[List[Producto]], None]] = None,
        al_exportar_individual: Optional[Callable[[int], None]] = None,
    ):
        super().__init__()
        self.pagina = pagina
        self.productos = productos
        self.imagenes_compuestas = imagenes_compuestas
        self.al_editar_producto = al_editar_producto
        self.al_exportar = al_exportar
        self.al_exportar_individual = al_exportar_individual
        self._servicio_texto = ServicioTexto()
        self._imagenes_finales: Dict[int, Image.Image] = {}
        self._tarjetas: Dict[int, ft.Container] = {}

        self.expand = True

    def did_mount(self):
        """Generar las imagenes de previsualizacion al montarse en la pagina."""
        self._generar_todas_las_previews()

    def build(self):
        return ft.Column(
            controls=[self._construir_contenido()],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            expand=True
        )

    def _construir_contenido(self) -> ft.Container:
        """Construye el contenido completo de la vista."""

        # Encabezado
        encabezado = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.PREVIEW, color=COLOR_ACENTO_PRIMARIO, size=28),
                            ft.Text(
                                "Previsualizacion final",
                                size=24,
                                weight=ft.FontWeight.W_800,
                                color=COLOR_TEXTO_PRINCIPAL,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    ft.Text(
                        "Revisa las imagenes. Puedes editar cualquiera o guardarlas todas.",
                        size=13,
                        color=COLOR_TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.padding.symmetric(vertical=16),
        )

        # Grilla de imagenes
        self._grilla_productos = ft.GridView(
            expand=True,
            max_extent=320,
            child_aspect_ratio=0.78,
            spacing=16,
            run_spacing=16,
        )

        # Boton global: Guardar todas
        boton_guardar_todas = ft.ElevatedButton(
            "Guardar todas las imagenes",
            icon=ft.Icons.SAVE_ALT,
            style=ft.ButtonStyle(
                bgcolor=COLOR_EXITO,
                color=COLOR_TEXTO_PRINCIPAL,
                padding=ft.padding.symmetric(horizontal=30, vertical=14),
                shape=ft.RoundedRectangleBorder(radius=RADIO_BORDE),
                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600),
            ),
            on_click=self._al_guardar_todas,
        )

        self._mensaje_estado = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)

        return ft.Container(
            content=ft.Column(
                controls=[
                    encabezado,
                    ft.Divider(height=1, color=COLOR_BORDE),
                    ft.Container(
                        content=self._grilla_productos,
                        padding=ft.padding.all(16),
                        expand=True,
                    ),
                    self._mensaje_estado,
                    ft.Container(
                        content=boton_guardar_todas,
                        padding=ft.padding.symmetric(vertical=16),
                        alignment=ft.alignment.center,
                    ),
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            padding=ft.padding.symmetric(horizontal=20),
            expand=True,
        )

    def _generar_todas_las_previews(self):
        """Genera las imagenes de preview para todos los productos."""
        for indice, producto in enumerate(self.productos):
            imagen_base = self.imagenes_compuestas.get(indice)
            if not imagen_base:
                continue

            imagen_fondo_precio = None
            if producto.ruta_fondo_precio:
                imagen_fondo_precio = cargar_imagen(producto.ruta_fondo_precio)

            nombre = None
            posicion_nombre = None
            if producto.incluir_nombre:
                nombre = producto.obtener_nombre_limpio()
                posicion_nombre = producto.posicion_nombre

            try:
                imagen_final = self._servicio_texto.generar_vista_previa(
                    imagen_base=imagen_base,
                    texto_precio=producto.precio,
                    posicion_precio=producto.posicion_precio,
                    color_precio=producto.color_texto_precio or (255, 255, 255),
                    nombre_producto=nombre,
                    posicion_nombre=posicion_nombre,
                    alineacion_nombre=producto.alineacion_nombre or "centro",
                    color_nombre=producto.color_texto_nombre or (255, 255, 255),
                    imagen_fondo_precio=imagen_fondo_precio,
                    ruta_fuente=producto.fuente,
                    tamano_precio=producto.tamano_precio,
                    tamano_nombre=producto.tamano_nombre,
                    tamano_etiqueta=producto.tamano_etiqueta,
                )
                self._imagenes_finales[indice] = imagen_final
            except Exception as error:
                print(f"Error generando preview de '{producto.nombre}': {error}")

        self._actualizar_grilla()

    def _actualizar_grilla(self):
        """Reconstruye la grilla de productos."""
        self._grilla_productos.controls.clear()
        self._tarjetas.clear()

        for indice, producto in enumerate(self.productos):
            tarjeta = self._crear_tarjeta_producto(indice, producto)
            self._tarjetas[indice] = tarjeta
            self._grilla_productos.controls.append(tarjeta)

        try:
            self._grilla_productos.update()
        except Exception:
            pass

    def _crear_tarjeta_producto(self, indice: int, producto: Producto) -> ft.Container:
        """Crea una tarjeta visual para un producto."""
        # Imagen
        control_imagen = ft.Container(
            content=ft.Text("Sin imagen", color=COLOR_TEXTO_SECUNDARIO, size=11),
            alignment=ft.alignment.center,
            height=180,
            bgcolor="#0a0a1a",
            border_radius=8,
        )

        imagen_final = self._imagenes_finales.get(indice)
        if imagen_final:
            imagen_redim = redimensionar_para_vista_previa(imagen_final, 280, 180)
            b64 = imagen_a_base64(imagen_redim)
            control_imagen = ft.Image(
                src_base64=b64,
                width=280,
                height=180,
                fit=ft.ImageFit.CONTAIN,
                border_radius=8,
            )

        # Botones: Editar y Guardar
        botones = ft.Row(
            controls=[
                ft.TextButton(
                    "Editar",
                    icon=ft.Icons.EDIT,
                    style=ft.ButtonStyle(color=COLOR_ACENTO_PRIMARIO),
                    on_click=lambda e, i=indice: self._al_editar(i),
                ),
                ft.TextButton(
                    "Guardar",
                    icon=ft.Icons.SAVE,
                    style=ft.ButtonStyle(color=COLOR_EXITO),
                    on_click=lambda e, i=indice: self._al_guardar_individual(i),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            spacing=0,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    control_imagen,
                    ft.Text(
                        producto.obtener_nombre_limpio(),
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=COLOR_TEXTO_PRINCIPAL,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        producto.precio or "Sin precio",
                        size=14,
                        weight=ft.FontWeight.W_700,
                        color=COLOR_ACENTO_PRIMARIO,
                    ),
                    botones,
                ],
                spacing=6,
            ),
            padding=ft.padding.all(12),
            border_radius=RADIO_BORDE,
            bgcolor=COLOR_FONDO_SECUNDARIO,
            border=ft.border.all(1, COLOR_BORDE),
        )

    def _al_editar(self, indice: int):
        """Navega a la vista de edicion para un producto especifico."""
        if self.al_editar_producto:
            self.al_editar_producto(indice)

    def _al_guardar_individual(self, indice: int):
        """Guarda una imagen individual."""
        if self.al_exportar_individual:
            self.al_exportar_individual(indice)
        else:
            # Fallback: marcar como aprobado y notificar
            self.productos[indice].aprobado = True
            tarjeta = self._tarjetas.get(indice)
            if tarjeta:
                tarjeta.border = ft.border.all(2, COLOR_EXITO)
                try:
                    tarjeta.update()
                except Exception:
                    pass
            self._mensaje_estado.value = f"Imagen '{self.productos[indice].obtener_nombre_limpio()}' marcada para guardar"
            self._mensaje_estado.color = COLOR_EXITO
            try:
                self._mensaje_estado.update()
            except Exception:
                pass

    def _al_guardar_todas(self, e):
        """Exporta todas las imagenes."""
        # Marcar todos como aprobados para el flujo de exportacion
        for producto in self.productos:
            producto.aprobado = True

        if self.al_exportar:
            self.al_exportar(self.productos)

    def obtener_imagenes_finales(self) -> Dict[int, Image.Image]:
        """Retorna el diccionario de imagenes finales generadas."""
        return self._imagenes_finales
