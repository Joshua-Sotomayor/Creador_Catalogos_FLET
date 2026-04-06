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
    ):
        super().__init__()
        self.pagina = pagina
        self.productos = productos
        self.precios = precios
        self.incluir_nombre = incluir_nombre
        self.imagenes_fondo_precio = imagenes_fondo_precio or []
        self.al_finalizar = al_finalizar

        self._indice_actual = 0
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
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        )

        # === Barra de herramientas de modos ===
        self._barra_modos = BarraHerramientas(
            al_cambiar_modo=self._al_cambiar_modo,
            modo_inicial=MODO_MANUAL,
        )

        # === Panel izquierdo: Vista previa ===
        self._vista_previa = VistaPreviaImagen(
            ancho=480,
            alto=480,
            titulo="Vista previa",
        )

        panel_izquierdo = ft.Container(
            content=self._vista_previa,
            padding=ft.padding.all(16),
            bgcolor=COLOR_FONDO_SECUNDARIO,
            border_radius=RADIO_BORDE,
            border=ft.border.all(1, COLOR_BORDE),
        )

        # === Panel derecho: Controles ===

        # -- Precio --
        self._campo_precio = ft.TextField(
            label="Precio",
            hint_text="Ej: $29.99",
            width=250,
            height=50,
            text_size=16,
            border_color=COLOR_BORDE,
            focused_border_color=COLOR_ACENTO_PRIMARIO,
            color=COLOR_TEXTO_PRINCIPAL,
            bgcolor="#0a0a1a",
            border_radius=8,
            prefix_icon=ft.Icons.ATTACH_MONEY,
            on_change=self._al_cambiar_precio,
        )

        self._matriz_precio = MatrizPosicion(
            filas=FILAS_GRILLA_PRECIO,
            columnas=COLUMNAS_GRILLA_PRECIO,
            titulo="Posición del precio (5×5)",
            al_seleccionar=self._al_seleccionar_posicion_precio,
        )

        self._selector_color_precio = SelectorColor(
            titulo="Color del precio",
            color_inicial=(255, 255, 255),
            al_cambiar=self._al_cambiar_color_precio,
        )

        seccion_precio = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("💰 Precio", size=15, weight=ft.FontWeight.W_700,
                            color=COLOR_TEXTO_PRINCIPAL),
                    self._campo_precio,
                    self._matriz_precio,
                    self._selector_color_precio,
                ],
                spacing=12,
            ),
            padding=ft.padding.all(16),
            border_radius=RADIO_BORDE,
            bgcolor=COLOR_FONDO_SECUNDARIO,
            border=ft.border.all(1, COLOR_BORDE),
        )

        # -- Nombre --
        self._campo_nombre = ft.TextField(
            label="Nombre del producto",
            width=250,
            height=50,
            text_size=14,
            border_color=COLOR_BORDE,
            focused_border_color=COLOR_ACENTO_PRIMARIO,
            color=COLOR_TEXTO_PRINCIPAL,
            bgcolor="#0a0a1a",
            border_radius=8,
            prefix_icon=ft.Icons.LABEL,
            on_change=self._al_cambiar_nombre,
        )

        self._switch_incluir_nombre = ft.Switch(
            label="Incluir nombre",
            value=self.incluir_nombre,
            active_color=COLOR_ACENTO_PRIMARIO,
            label_style=ft.TextStyle(color=COLOR_TEXTO_PRINCIPAL, size=12),
            on_change=self._al_cambiar_switch_nombre,
        )

        self._matriz_nombre = MatrizPosicion(
            filas=FILAS_GRILLA_NOMBRE,
            columnas=COLUMNAS_GRILLA_NOMBRE,
            titulo="Posición del nombre (3×3)",
            al_seleccionar=self._al_seleccionar_posicion_nombre,
            tamano_celda=50,
        )

        self._dropdown_alineacion = ft.Dropdown(
            label="Alineación",
            options=[
                ft.dropdown.Option(key=ALINEACION_IZQUIERDA, text="Izquierda"),
                ft.dropdown.Option(key=ALINEACION_CENTRO, text="Centro"),
                ft.dropdown.Option(key=ALINEACION_DERECHA, text="Derecha"),
            ],
            value=ALINEACION_CENTRO,
            width=200,
            height=50,
            text_size=13,
            border_color=COLOR_BORDE,
            focused_border_color=COLOR_ACENTO_PRIMARIO,
            color=COLOR_TEXTO_PRINCIPAL,
            bgcolor="#0a0a1a",
            border_radius=8,
            on_change=self._al_cambiar_alineacion,
        )

        self._selector_color_nombre = SelectorColor(
            titulo="Color del nombre",
            color_inicial=(255, 255, 255),
            al_cambiar=self._al_cambiar_color_nombre,
        )

        self._contenedor_nombre = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("✏️ Nombre", size=15, weight=ft.FontWeight.W_700,
                                    color=COLOR_TEXTO_PRINCIPAL),
                            self._switch_incluir_nombre,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self._campo_nombre,
                    self._matriz_nombre,
                    self._dropdown_alineacion,
                    self._selector_color_nombre,
                ],
                spacing=12,
            ),
            padding=ft.padding.all(16),
            border_radius=RADIO_BORDE,
            bgcolor=COLOR_FONDO_SECUNDARIO,
            border=ft.border.all(1, COLOR_BORDE),
        )

        # -- Fondo del precio --
        self._galeria_fondos_precio = GaleriaImagenes(
            titulo="Fondos para el precio",
            al_seleccionar=self._al_seleccionar_fondo_precio,
        )
        if self.imagenes_fondo_precio:
            self._galeria_fondos_precio.cargar_desde_lista(self.imagenes_fondo_precio)

        self._contenedor_fondo_precio = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("🎨 Fondo decorativo del precio", size=15,
                            weight=ft.FontWeight.W_700, color=COLOR_TEXTO_PRINCIPAL),
                    self._galeria_fondos_precio,
                ],
                spacing=12,
            ),
            padding=ft.padding.all(16),
            border_radius=RADIO_BORDE,
            bgcolor=COLOR_FONDO_SECUNDARIO,
            border=ft.border.all(1, COLOR_BORDE),
            visible=bool(self.imagenes_fondo_precio),
        )

        # -- Selector de fuente --
        self._selector_fuente = SelectorFuente(
            titulo="Fuente tipográfica",
            al_cambiar=self._al_cambiar_fuente,
        )

        seccion_fuente = ft.Container(
            content=self._selector_fuente,
            padding=ft.padding.all(16),
            border_radius=RADIO_BORDE,
            bgcolor=COLOR_FONDO_SECUNDARIO,
            border=ft.border.all(1, COLOR_BORDE),
        )

        panel_derecho = ft.Column(
            controls=[
                seccion_precio,
                self._contenedor_nombre,
                self._contenedor_fondo_precio,
                seccion_fuente,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            width=380,
            expand=True,
        )

        # === Botones de acción ===
        self._mensaje_estado = ft.Text("", size=12, color=COLOR_ADVERTENCIA)

        botones_accion = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "⬅️ Anterior",
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_FONDO_TARJETA,
                        color=COLOR_TEXTO_PRINCIPAL,
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=self._al_anterior,
                ),
                ft.ElevatedButton(
                    "👁️ Actualizar preview",
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_ACENTO_SECUNDARIO,
                        color=COLOR_TEXTO_PRINCIPAL,
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=self._al_actualizar_preview,
                ),
                ft.ElevatedButton(
                    "✅ Confirmar y Siguiente",
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_ACENTO_PRIMARIO,
                        color=COLOR_TEXTO_PRINCIPAL,
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=self._al_confirmar_siguiente,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        boton_finalizar = ft.ElevatedButton(
            "🏁 Finalizar y pasar a previsualización",
            style=ft.ButtonStyle(
                bgcolor=COLOR_EXITO,
                color=COLOR_TEXTO_PRINCIPAL,
                padding=ft.padding.symmetric(horizontal=30, vertical=14),
                shape=ft.RoundedRectangleBorder(radius=RADIO_BORDE),
                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600),
            ),
            on_click=self._al_finalizar_edicion,
        )

        # === Layout principal ===
        area_principal = ft.Row(
            controls=[panel_izquierdo, panel_derecho],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    encabezado,
                    ft.Container(
                        content=self._barra_modos,
                        padding=ft.padding.symmetric(horizontal=20),
                    ),
                    ft.Container(
                        content=area_principal,
                        padding=ft.padding.symmetric(horizontal=20),
                        expand=True,
                    ),
                    self._mensaje_estado,
                    botones_accion,
                    boton_finalizar,
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            padding=ft.padding.all(10),
            expand=True,
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

    def _al_cambiar_fuente(self, fuente: str):
        """Recarga la fuente en el servicio de texto (se reflejará en la siguiente preview)."""
        self._servicio_texto._fuente_cache.clear()
        # TODO: Implementar carga de fuente personalizada en el servicio
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

    def _al_finalizar_edicion(self, e):
        """Verifica que todos los productos tengan precio y finaliza."""
        self._guardar_producto_actual()

        productos_sin_precio = [
            p for p in self.productos
            if not p.precio or not p.posicion_precio
        ]

        if productos_sin_precio:
            nombres = ", ".join(p.obtener_nombre_limpio() for p in productos_sin_precio[:3])
            restantes = len(productos_sin_precio) - 3
            texto = f"⚠️ Faltan datos en: {nombres}"
            if restantes > 0:
                texto += f" y {restantes} más"
            self._mensaje_estado.value = texto
            self._mensaje_estado.color = COLOR_ADVERTENCIA
            self._mensaje_estado.update()
            return

        if self.al_finalizar:
            self.al_finalizar(self.productos)

    # === Navegación directa a un producto ===

    def ir_a_producto(self, indice: int):
        """Navega directamente a un producto específico."""
        if 0 <= indice < len(self.productos):
            self._guardar_producto_actual()
            self._indice_actual = indice
            self._cargar_producto_actual()
