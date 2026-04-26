"""
Vista de edición de precio y nombre (Paso 3).
Interfaz interactiva donde el usuario asigna precios, posiciones y colores.
"""
import flet as ft
from typing import Callable, Dict, List, Optional, Tuple

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
    COLOR_ADVERTENCIA,
    RADIO_BORDE,
    ESPACIADO_GENERAL,
    FILAS_GRILLA_PRECIO,
    COLUMNAS_GRILLA_PRECIO,
    FILAS_GRILLA_NOMBRE,
    COLUMNAS_GRILLA_NOMBRE,
    MODO_AUTOMATICO,
    MODO_MANUAL,
    MODO_SELECCION_FONDO,
    ALINEACION_CENTRO,
    ALINEACION_IZQUIERDA,
    ALINEACION_DERECHA,
)
from modelos.producto import Producto
from componentes.matriz_posicion import MatrizPosicion
from componentes.vista_previa_imagen import VistaPreviaImagen
from componentes.barra_herramientas import BarraHerramientas
from componentes.selector_color import SelectorColor
from componentes.selector_fuente import SelectorFuente
from componentes.galeria_imagenes import GaleriaImagenes
from servicios.servicio_texto import ServicioTexto
from servicios.servicio_deteccion_color import ServicioDeteccionColor
from utilidades.ayudantes_imagen import cargar_imagen


class VistaEdicion(ft.UserControl):
    """
    Vista de edición de precio y nombre para cada producto.
    Muestra las imágenes secuencialmente y permite configurar:
    - Posición del precio (grilla 5x5)
    - Posición del nombre (grilla 3x3) con alineación
    - Color del texto
    - Fondo decorativo del precio
    - Vista previa en tiempo real
    """

    def __init__(
        self,
        pagina: ft.Page,
        productos: List[Producto],
        precios: List[str],
        incluir_nombre: bool = True,
        imagenes_fondo_precio: List[str] = None,
        al_finalizar: Optional[Callable[[List[Producto]], None]] = None,
        indice_inicial: int = 0,
    ):
        super().__init__()
        self.pagina = pagina
        self.productos = productos
        self.precios = precios
        self.incluir_nombre = incluir_nombre
        self.imagenes_fondo_precio = imagenes_fondo_precio or []
        self.al_finalizar = al_finalizar

        self._indice_actual = indice_inicial
        self._servicio_texto = ServicioTexto()
        self._servicio_color = ServicioDeteccionColor()
        self._imagenes_compuestas: Dict[int, Image.Image] = {}

        self.expand = True

        self._contenido = self._construir_contenido()

    def did_mount(self):
        # Inicializar una vez que ya formamos parte de la pantalla gráfica
        if self.productos:
            self._cargar_producto_actual()

    def build(self):
        return ft.Column(
            controls=[self._contenido],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            expand=True
        )

    def _construir_contenido(self) -> ft.Container:
        """Construye el layout principal de la vista."""

        # === Encabezado con navegación ===
        self._etiqueta_progreso = ft.Text(
            "Producto 1 de 0",
            size=14,
            weight=ft.FontWeight.W_600,
            color=COLOR_TEXTO_PRINCIPAL,
        )

        self._barra_progreso = ft.ProgressBar(
            value=0,
            color=COLOR_ACENTO_PRIMARIO,
            bgcolor=COLOR_FONDO_TARJETA,
            height=4,
            border_radius=2,
        )

        self._etiqueta_nombre_producto = ft.Text(
            "",
            size=18,
            weight=ft.FontWeight.W_700,
            color=COLOR_ACENTO_PRIMARIO,
        )

        encabezado = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                ft.Icons.ARROW_BACK_IOS,
                                icon_color=COLOR_TEXTO_SECUNDARIO,
                                icon_size=20,
                                on_click=self._al_anterior,
                                tooltip="Producto anterior",
                            ),
                            ft.Column(
                                controls=[
                                    self._etiqueta_nombre_producto,
                                    self._etiqueta_progreso,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=4,
                            ),
                            ft.IconButton(
                                ft.Icons.ARROW_FORWARD_IOS,
                                icon_color=COLOR_TEXTO_SECUNDARIO,
                                icon_size=20,
                                on_click=self._al_siguiente,
                                tooltip="Producto siguiente",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    self._barra_progreso,
                ],
                spacing=8,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
        )

        # === Barra de herramientas de modos (oculta pero conservada) ===
        self._barra_modos = BarraHerramientas(
            al_cambiar_modo=self._al_cambiar_modo,
            modo_inicial=MODO_MANUAL,
        )

        # === Panel izquierdo: Vista previa ===
        self._vista_previa = VistaPreviaImagen(
            ancho=460,
            alto=460,
            titulo="Vista previa",
        )

        panel_imagen = ft.Container(
            content=self._vista_previa,
            padding=ft.padding.all(12),
            bgcolor=COLOR_FONDO_SECUNDARIO,
            border_radius=RADIO_BORDE,
            border=ft.border.all(1, COLOR_BORDE),
        )

        # === Panel derecho superior: Precio ===
        self._campo_precio = ft.TextField(
            label="Precio", hint_text="Ej: $29.99", width=200, height=45, text_size=15,
            border_color=COLOR_BORDE, focused_border_color=COLOR_ACENTO_PRIMARIO,
            color=COLOR_TEXTO_PRINCIPAL, bgcolor="#0a0a1a", border_radius=8,
            prefix_icon=ft.Icons.ATTACH_MONEY, on_change=self._al_cambiar_precio,
        )
        self._matriz_precio = MatrizPosicion(
            filas=FILAS_GRILLA_PRECIO, columnas=COLUMNAS_GRILLA_PRECIO,
            titulo="Posicion del precio (6x6)", al_seleccionar=self._al_seleccionar_posicion_precio,
        )
        self._selector_color_precio = SelectorColor(
            titulo="Color del precio", color_inicial=(255, 255, 255), al_cambiar=self._al_cambiar_color_precio,
        )
        self._slider_tamano_precio = ft.Slider(
            min=10, max=150, value=30, divisions=140, label="{value}",
            active_color=COLOR_ACENTO_PRIMARIO, on_change=self._al_cambiar_tamano_precio, width=200,
        )
        self._slider_tamano_etiqueta = ft.Slider(
            min=10, max=200, value=50, divisions=190, label="{value}",
            active_color=COLOR_ACENTO_SECUNDARIO, on_change=self._al_cambiar_tamano_etiqueta, width=200,
        )
        sliders_precio = ft.Column(controls=[
            ft.Text("Texto", size=11, color=COLOR_TEXTO_SECUNDARIO), self._slider_tamano_precio,
            ft.Text("Etiqueta", size=11, color=COLOR_TEXTO_SECUNDARIO), self._slider_tamano_etiqueta,
        ], spacing=2, width=210)
        fila_grilla_precio = ft.Row(
            controls=[self._matriz_precio, sliders_precio], spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        seccion_precio = ft.Container(
            content=ft.Column(controls=[
                ft.Text("Precio", size=14, weight=ft.FontWeight.W_700, color=COLOR_TEXTO_PRINCIPAL),
                self._campo_precio, fila_grilla_precio, self._selector_color_precio,
            ], spacing=8),
            padding=ft.padding.all(12), border_radius=RADIO_BORDE,
            bgcolor=COLOR_FONDO_SECUNDARIO, border=ft.border.all(1, COLOR_BORDE),
        )

        # === Panel inferior izquierdo: Nombre ===
        self._campo_nombre = ft.TextField(
            label="Nombre del producto", width=200, height=45, text_size=13,
            border_color=COLOR_BORDE, focused_border_color=COLOR_ACENTO_PRIMARIO,
            color=COLOR_TEXTO_PRINCIPAL, bgcolor="#0a0a1a", border_radius=8,
            prefix_icon=ft.Icons.LABEL, on_change=self._al_cambiar_nombre,
        )
        self._switch_incluir_nombre = ft.Switch(
            label="Incluir", value=self.incluir_nombre, active_color=COLOR_ACENTO_PRIMARIO,
            label_style=ft.TextStyle(color=COLOR_TEXTO_PRINCIPAL, size=11),
            on_change=self._al_cambiar_switch_nombre,
        )
        self._matriz_nombre = MatrizPosicion(
            filas=FILAS_GRILLA_NOMBRE, columnas=COLUMNAS_GRILLA_NOMBRE,
            titulo="Posicion del nombre (7x7)", al_seleccionar=self._al_seleccionar_posicion_nombre,
        )
        self._dropdown_alineacion = ft.Dropdown(
            label="Alineacion", options=[
                ft.dropdown.Option(key=ALINEACION_IZQUIERDA, text="Izquierda"),
                ft.dropdown.Option(key=ALINEACION_CENTRO, text="Centro"),
                ft.dropdown.Option(key=ALINEACION_DERECHA, text="Derecha"),
            ], value=ALINEACION_CENTRO, width=140, height=42, text_size=12,
            border_color=COLOR_BORDE, focused_border_color=COLOR_ACENTO_PRIMARIO,
            color=COLOR_TEXTO_PRINCIPAL, bgcolor="#0a0a1a", border_radius=8,
            on_change=self._al_cambiar_alineacion,
        )
        self._selector_color_nombre = SelectorColor(
            titulo="Color del nombre", color_inicial=(255, 255, 255), al_cambiar=self._al_cambiar_color_nombre,
        )
        self._slider_tamano_nombre = ft.Slider(
            min=8, max=120, value=20, divisions=112, label="{value}",
            active_color=COLOR_ACENTO_PRIMARIO, on_change=self._al_cambiar_tamano_nombre, width=200,
        )
        sliders_nombre = ft.Column(controls=[
            ft.Text("Texto", size=11, color=COLOR_TEXTO_SECUNDARIO), self._slider_tamano_nombre,
            self._dropdown_alineacion,
        ], spacing=2, width=210)
        fila_grilla_nombre = ft.Row(
            controls=[self._matriz_nombre, sliders_nombre], spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        self._contenedor_nombre = ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Text("Nombre", size=14, weight=ft.FontWeight.W_700, color=COLOR_TEXTO_PRINCIPAL),
                    self._switch_incluir_nombre,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self._campo_nombre, fila_grilla_nombre, self._selector_color_nombre,
            ], spacing=8),
            padding=ft.padding.all(12), border_radius=RADIO_BORDE,
            bgcolor=COLOR_FONDO_SECUNDARIO, border=ft.border.all(1, COLOR_BORDE),
        )

        # === Fondo del precio (oculto) ===
        self._galeria_fondos_precio = GaleriaImagenes(
            titulo="Fondos para el precio", al_seleccionar=self._al_seleccionar_fondo_precio,
        )
        if self.imagenes_fondo_precio:
            self._galeria_fondos_precio.cargar_desde_lista(self.imagenes_fondo_precio)
        self._contenedor_fondo_precio = ft.Container(content=self._galeria_fondos_precio, visible=False)

        # === Panel inferior derecho: Fuente + Acciones ===
        self._selector_fuente = SelectorFuente(titulo="Fuente", al_cambiar=self._al_cambiar_fuente)
        seccion_fuente = ft.Container(
            content=self._selector_fuente, padding=ft.padding.all(12),
            border_radius=RADIO_BORDE, bgcolor=COLOR_FONDO_SECUNDARIO, border=ft.border.all(1, COLOR_BORDE),
        )

        self._mensaje_estado = ft.Text("", size=12, color=COLOR_ADVERTENCIA)

        botones_accion = ft.Column(controls=[
            ft.ElevatedButton("Anterior", icon=ft.Icons.ARROW_BACK, style=ft.ButtonStyle(
                bgcolor=COLOR_FONDO_TARJETA, color=COLOR_TEXTO_PRINCIPAL,
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                shape=ft.RoundedRectangleBorder(radius=8)), on_click=self._al_anterior, width=220),
            ft.ElevatedButton("Actualizar preview", icon=ft.Icons.REFRESH, style=ft.ButtonStyle(
                bgcolor=COLOR_ACENTO_SECUNDARIO, color=COLOR_TEXTO_PRINCIPAL,
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                shape=ft.RoundedRectangleBorder(radius=8)), on_click=self._al_actualizar_preview, width=220),
            ft.ElevatedButton("Confirmar y Siguiente", icon=ft.Icons.ARROW_FORWARD, style=ft.ButtonStyle(
                bgcolor=COLOR_ACENTO_PRIMARIO, color=COLOR_TEXTO_PRINCIPAL,
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                shape=ft.RoundedRectangleBorder(radius=8)), on_click=self._al_confirmar_siguiente, width=220),
            ft.ElevatedButton("Finalizar y guardar", icon=ft.Icons.SAVE, style=ft.ButtonStyle(
                bgcolor=COLOR_EXITO, color=COLOR_TEXTO_PRINCIPAL,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                shape=ft.RoundedRectangleBorder(radius=RADIO_BORDE),
                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600)),
                on_click=self._al_finalizar_edicion, width=220),
        ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        panel_inferior_derecho = ft.Container(
            content=ft.Column(controls=[
                seccion_fuente, self._contenedor_fondo_precio, self._mensaje_estado, botones_accion,
            ], spacing=8),
            padding=ft.padding.all(0),
        )

        # === Layout 2x2 ===
        fila_superior = ft.Row(
            controls=[panel_imagen, seccion_precio], spacing=12,
            alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START,
        )
        fila_inferior = ft.Row(
            controls=[self._contenedor_nombre, panel_inferior_derecho], spacing=12,
            alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START,
        )

        return ft.Container(
            content=ft.Column(controls=[
                encabezado, fila_superior, fila_inferior,
            ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(8),
        )

    # === Carga de producto ===

    def _cargar_producto_actual(self):
        """Carga los datos del producto actual en la interfaz."""
        if not self.productos or self._indice_actual >= len(self.productos):
            return

        producto = self.productos[self._indice_actual]

        # Actualizar progreso
        total = len(self.productos)
        self._etiqueta_progreso.value = f"Producto {self._indice_actual + 1} de {total}"
        self._barra_progreso.value = (self._indice_actual + 1) / total
        self._etiqueta_nombre_producto.value = producto.obtener_nombre_limpio()

        # Cargar precio
        if producto.precio:
            self._campo_precio.value = producto.precio
        elif self._indice_actual < len(self.precios):
            self._campo_precio.value = self.precios[self._indice_actual]
            producto.precio = self.precios[self._indice_actual]
        else:
            self._campo_precio.value = ""

        # Cargar nombre
        self._campo_nombre.value = producto.obtener_nombre_limpio()

        # Cargar imagen compuesta
        if self._indice_actual in self._imagenes_compuestas:
            imagen_compuesta = self._imagenes_compuestas[self._indice_actual]
        elif producto.ruta_compuesta:
            imagen_compuesta = cargar_imagen(producto.ruta_compuesta)
            if imagen_compuesta:
                self._imagenes_compuestas[self._indice_actual] = imagen_compuesta
        else:
            imagen_compuesta = None

        if producto.tamano_precio:
            self._slider_tamano_precio.value = producto.tamano_precio
        else:
            self._slider_tamano_precio.value = 30  # Default referencial

        if producto.tamano_etiqueta:
            self._slider_tamano_etiqueta.value = producto.tamano_etiqueta
        else:
            self._slider_tamano_etiqueta.value = 50  # Default referencial

        if producto.tamano_nombre:
            self._slider_tamano_nombre.value = producto.tamano_nombre
        else:
            self._slider_tamano_nombre.value = 20  # Default referencial

        if producto.fuente:
            self._selector_fuente._dropdown.value = producto.fuente

        if imagen_compuesta:
            self._vista_previa.actualizar_imagen(imagen_compuesta)

            # Proponer color de contraste
            if producto.posicion_precio:
                color_propuesto = self._servicio_color.obtener_color_contraste_avanzado(
                    imagen_compuesta, producto.posicion_precio
                )
                self._selector_color_precio.establecer_propuesta(color_propuesto)

        # Restaurar posiciones guardadas
        if producto.posicion_precio:
            self._matriz_precio.establecer_posicion(*producto.posicion_precio)
        if producto.posicion_nombre:
            self._matriz_nombre.establecer_posicion(*producto.posicion_nombre)

        try:
            self.update()
        except Exception:
            pass

    def registrar_imagen_compuesta(self, indice: int, imagen: Image.Image):
        """Registra una imagen compuesta para un producto específico."""
        self._imagenes_compuestas[indice] = imagen

    # === Callbacks de cambio ===

    def _al_cambiar_modo(self, modo: str):
        """Cambia el modo de edición."""
        self._contenedor_fondo_precio.visible = (
            modo == MODO_SELECCION_FONDO or bool(self.imagenes_fondo_precio)
        )
        try:
            self._contenedor_fondo_precio.update()
        except Exception:
            pass

    def _al_cambiar_precio(self, e):
        if self._indice_actual < len(self.productos):
            self.productos[self._indice_actual].precio = e.control.value

    def _al_cambiar_nombre(self, e):
        pass  # El nombre se usa directamente del campo al generar preview

    def _al_cambiar_switch_nombre(self, e):
        if self._indice_actual < len(self.productos):
            self.productos[self._indice_actual].incluir_nombre = e.control.value

    def _al_seleccionar_posicion_precio(self, posicion: Tuple[int, int]):
        if self._indice_actual < len(self.productos):
            self.productos[self._indice_actual].posicion_precio = posicion
            # Proponer color de contraste
            imagen = self._imagenes_compuestas.get(self._indice_actual)
            if imagen:
                color = self._servicio_color.obtener_color_contraste_avanzado(
                    imagen, posicion
                )
                self._selector_color_precio.establecer_propuesta(color)
            self._generar_preview()

    def _al_seleccionar_posicion_nombre(self, posicion: Tuple[int, int]):
        if self._indice_actual < len(self.productos):
            self.productos[self._indice_actual].posicion_nombre = posicion
            self._generar_preview()

    def _al_cambiar_color_precio(self, color: Tuple[int, int, int]):
        if self._indice_actual < len(self.productos):
            self.productos[self._indice_actual].color_texto_precio = color
            self._generar_preview()

    def _al_cambiar_color_nombre(self, color: Tuple[int, int, int]):
        if self._indice_actual < len(self.productos):
            self.productos[self._indice_actual].color_texto_nombre = color
            self._generar_preview()

    def _al_cambiar_alineacion(self, e):
        if self._indice_actual < len(self.productos):
            self.productos[self._indice_actual].alineacion_nombre = e.control.value
            self._generar_preview()

    def _al_seleccionar_fondo_precio(self, ruta: str):
        if self._indice_actual < len(self.productos):
            self.productos[self._indice_actual].ruta_fondo_precio = ruta
            self._generar_preview()

    def _al_cambiar_tamano_precio(self, e):
        if self._indice_actual < len(self.productos):
            self.productos[self._indice_actual].tamano_precio = int(e.control.value)
            self._generar_preview()

    def _al_cambiar_tamano_etiqueta(self, e):
        if self._indice_actual < len(self.productos):
            self.productos[self._indice_actual].tamano_etiqueta = int(e.control.value)
            self._generar_preview()

    def _al_cambiar_tamano_nombre(self, e):
        if self._indice_actual < len(self.productos):
            self.productos[self._indice_actual].tamano_nombre = int(e.control.value)
            self._generar_preview()

    def _al_cambiar_fuente(self, fuente: str):
        """Asigna la ruta de la fuente al producto actual."""
        if self._indice_actual < len(self.productos):
            self.productos[self._indice_actual].fuente = fuente
            self._generar_preview()

    # === Generación de preview ===

    def _generar_preview(self):
        """Genera la vista previa actual con todos los parámetros configurados."""
        if self._indice_actual not in self._imagenes_compuestas:
            return

        producto = self.productos[self._indice_actual]
        imagen_base = self._imagenes_compuestas[self._indice_actual]

        # Cargar fondo de precio si existe
        imagen_fondo_precio = None
        if producto.ruta_fondo_precio:
            imagen_fondo_precio = cargar_imagen(producto.ruta_fondo_precio)

        # Nombre del producto
        nombre = None
        posicion_nombre = None
        if producto.incluir_nombre:
            nombre = self._campo_nombre.value or producto.obtener_nombre_limpio()
            posicion_nombre = producto.posicion_nombre

        preview = self._servicio_texto.generar_vista_previa(
            imagen_base=imagen_base,
            texto_precio=producto.precio,
            posicion_precio=producto.posicion_precio,
            color_precio=producto.color_texto_precio or (255, 255, 255),
            nombre_producto=nombre,
            posicion_nombre=posicion_nombre,
            alineacion_nombre=producto.alineacion_nombre or ALINEACION_CENTRO,
            color_nombre=producto.color_texto_nombre or (255, 255, 255),
            imagen_fondo_precio=imagen_fondo_precio,
            ruta_fuente=producto.fuente or self._selector_fuente.obtener_fuente(),
            tamano_precio=producto.tamano_precio,
            tamano_nombre=producto.tamano_nombre,
            tamano_etiqueta=producto.tamano_etiqueta,
        )

        self._vista_previa.actualizar_imagen(preview)

    def _al_actualizar_preview(self, e):
        """Fuerza la actualización del preview."""
        self._generar_preview()

    # === Navegación ===

    def _al_anterior(self, e):
        """Navega al producto anterior."""
        if self._indice_actual > 0:
            self._guardar_producto_actual()
            self._indice_actual -= 1
            self._cargar_producto_actual()

    def _al_siguiente(self, e):
        """Navega al producto siguiente."""
        if self._indice_actual < len(self.productos) - 1:
            self._guardar_producto_actual()
            self._indice_actual += 1
            self._cargar_producto_actual()

    def _al_confirmar_siguiente(self, e):
        """Confirma el producto actual y avanza al siguiente."""
        self._guardar_producto_actual()
        self.productos[self._indice_actual].aprobado = True

        if self._indice_actual < len(self.productos) - 1:
            self._indice_actual += 1
            self._cargar_producto_actual()
        else:
            self._mensaje_estado.value = "✅ Todos los productos han sido configurados"
            self._mensaje_estado.color = COLOR_EXITO
            self._mensaje_estado.update()

    def _guardar_producto_actual(self):
        """Guarda los datos del formulario en el producto actual."""
        if self._indice_actual >= len(self.productos):
            return

        producto = self.productos[self._indice_actual]
        producto.precio = self._campo_precio.value
        producto.incluir_nombre = self._switch_incluir_nombre.value
        producto.color_texto_precio = self._selector_color_precio.obtener_color()
        producto.color_texto_nombre = self._selector_color_nombre.obtener_color()
        producto.alineacion_nombre = self._dropdown_alineacion.value
        producto.tamano_precio = int(self._slider_tamano_precio.value)
        producto.tamano_nombre = int(self._slider_tamano_nombre.value)
        producto.tamano_etiqueta = int(self._slider_tamano_etiqueta.value)
        producto.fuente = self._selector_fuente.obtener_fuente()

    def _al_finalizar_edicion(self, e):
        """Finaliza la edición y pasa a la vista de previsualización."""
        self._guardar_producto_actual()

        if self.al_finalizar:
            self.al_finalizar(self.productos)

    # === Navegación directa a un producto ===

    def ir_a_producto(self, indice: int):
        """Navega directamente a un producto específico."""
        if 0 <= indice < len(self.productos):
            self._guardar_producto_actual()
            self._indice_actual = indice
            self._cargar_producto_actual()
