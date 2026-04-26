"""
Vista de previsualización final (Paso 4).
Muestra todas las imágenes finales para aprobación antes de exportar.
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
    Vista de previsualización final.
    Muestra las imágenes resultantes para que el usuario las apruebe o edite
    antes de exportar a las carpetas finales.
    """

    def __init__(
        self,
        pagina: ft.Page,
        productos: List[Producto],
        imagenes_compuestas: Dict[int, Image.Image],
        al_editar_producto: Optional[Callable[[int], None]] = None,
        al_exportar: Optional[Callable[[List[Producto]], None]] = None,
    ):
        super().__init__()
        self.pagina = pagina
        self.productos = productos
        self.imagenes_compuestas = imagenes_compuestas
        self.al_editar_producto = al_editar_producto
        self.al_exportar = al_exportar
        self._servicio_texto = ServicioTexto()
        self._imagenes_finales: Dict[int, Image.Image] = {}
        self._tarjetas: Dict[int, ft.Container] = {}

        self.expand = True

    def did_mount(self):
        """Generar las imágenes de previsualización al montarse en la página."""
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
                                "Previsualización final",
                                size=24,
                                weight=ft.FontWeight.W_800,
                                color=COLOR_TEXTO_PRINCIPAL,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    ft.Text(
                        "Revisa cada imagen antes de exportar. Puedes aprobarlas individualmente o todas a la vez.",
                        size=13,
                        color=COLOR_TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.padding.symmetric(vertical=20),
        )

        # Contadores
        self._etiqueta_aprobadas = ft.Text(
            "0 aprobadas",
            size=13,
            color=COLOR_EXITO,
            weight=ft.FontWeight.W_600,
        )
        self._etiqueta_pendientes = ft.Text(
            f"{len(self.productos)} pendientes",
            size=13,
            color=COLOR_TEXTO_SECUNDARIO,
        )

        fila_contadores = ft.Row(
            controls=[self._etiqueta_aprobadas, self._etiqueta_pendientes],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        # Grilla de imágenes
        self._grilla_productos = ft.GridView(
            expand=True,
            max_extent=320,
            child_aspect_ratio=0.75,
            spacing=16,
            run_spacing=16,
        )

        # Botones de acción
        botones = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "✅ Aceptar todo",
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_ACENTO_SECUNDARIO,
                        color=COLOR_TEXTO_PRINCIPAL,
                        padding=ft.padding.symmetric(horizontal=30, vertical=14),
                        shape=ft.RoundedRectangleBorder(radius=RADIO_BORDE),
                        text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600),
                    ),
                    on_click=self._al_aceptar_todo,
                ),
                ft.ElevatedButton(
                    "📁 Exportar catálogo",
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_EXITO,
                        color=COLOR_TEXTO_PRINCIPAL,
                        padding=ft.padding.symmetric(horizontal=30, vertical=14),
                        shape=ft.RoundedRectangleBorder(radius=RADIO_BORDE),
                        text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600),
                    ),
                    on_click=self._al_exportar_catalogo,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
        )

        self._mensaje_estado = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)

        return ft.Container(
            content=ft.Column(
                controls=[
                    encabezado,
                    fila_contadores,
                    ft.Divider(height=1, color=COLOR_BORDE),
                    ft.Container(
                        content=self._grilla_productos,
                        padding=ft.padding.all(16),
                        expand=True,
                    ),
                    self._mensaje_estado,
                    ft.Container(content=botones, padding=ft.padding.symmetric(vertical=20)),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            padding=ft.padding.symmetric(horizontal=20),
            expand=True,
        )

    def _generar_todas_las_previews(self):
        """Genera las imágenes de preview para todos los productos."""
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

        self._actualizar_contadores()

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

        # Estado
        icono_estado = ft.Icon(
            ft.Icons.CHECK_CIRCLE if producto.aprobado else ft.Icons.PENDING,
            color=COLOR_EXITO if producto.aprobado else COLOR_TEXTO_SECUNDARIO,
            size=18,
        )

        # Botones
        botones = ft.Row(
            controls=[
                ft.TextButton(
                    "✅ Aprobar",
                    style=ft.ButtonStyle(color=COLOR_EXITO),
                    on_click=lambda e, i=indice: self._al_aprobar(i),
                ),
                ft.TextButton(
                    "✏️ Editar",
                    style=ft.ButtonStyle(color=COLOR_ACENTO_PRIMARIO),
                    on_click=lambda e, i=indice: self._al_editar(i),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            spacing=0,
        )

        color_borde = COLOR_EXITO if producto.aprobado else COLOR_BORDE

        return ft.Container(
            content=ft.Column(
                controls=[
                    control_imagen,
                    ft.Row(
                        controls=[
                            ft.Text(
                                producto.obtener_nombre_limpio(),
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=COLOR_TEXTO_PRINCIPAL,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            icono_estado,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(
                        producto.precio or "Sin precio",
                        size=14,
                        weight=ft.FontWeight.W_700,
                        color=COLOR_ACENTO_PRIMARIO,
                    ),
                    botones,
                ],
                spacing=8,
            ),
            padding=ft.padding.all(12),
            border_radius=RADIO_BORDE,
            bgcolor=COLOR_FONDO_SECUNDARIO,
            border=ft.border.all(2, color_borde),
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

    def _al_aprobar(self, indice: int):
        """Aprueba un producto individual."""
        self.productos[indice].aprobado = True
        tarjeta = self._tarjetas.get(indice)
        if tarjeta:
            tarjeta.border = ft.border.all(2, COLOR_EXITO)
            tarjeta.update()
        self._actualizar_contadores()

    def _al_editar(self, indice: int):
        """Navega a la vista de edición para un producto específico."""
        if self.al_editar_producto:
            self.al_editar_producto(indice)

    def _al_aceptar_todo(self, e):
        """Aprueba todos los productos."""
        for indice, producto in enumerate(self.productos):
            producto.aprobado = True
            tarjeta = self._tarjetas.get(indice)
            if tarjeta:
                tarjeta.border = ft.border.all(2, COLOR_EXITO)

        self._actualizar_contadores()
        try:
            self._grilla_productos.update()
        except Exception:
            pass

    def _al_exportar_catalogo(self, e):
        """Exporta el catálogo si todos los productos están aprobados."""
        no_aprobados = [p for p in self.productos if not p.aprobado]
        if no_aprobados:
            self._mensaje_estado.value = (
                f"⚠️ Hay {len(no_aprobados)} producto(s) sin aprobar. "
                "Apruébalos o haz click en 'Aceptar todo'."
            )
            self._mensaje_estado.color = COLOR_ERROR
            self._mensaje_estado.update()
            return

        if self.al_exportar:
            self.al_exportar(self.productos)

    def _actualizar_contadores(self):
        """Actualiza los contadores de aprobadas/pendientes."""
        aprobadas = sum(1 for p in self.productos if p.aprobado)
        pendientes = len(self.productos) - aprobadas

        self._etiqueta_aprobadas.value = f"{aprobadas} aprobada(s)"
        self._etiqueta_pendientes.value = f"{pendientes} pendiente(s)"

        try:
            self._etiqueta_aprobadas.update()
            self._etiqueta_pendientes.update()
        except Exception:
            pass

    def obtener_imagenes_finales(self) -> Dict[int, Image.Image]:
        """Retorna el diccionario de imágenes finales generadas."""
        return self._imagenes_finales
