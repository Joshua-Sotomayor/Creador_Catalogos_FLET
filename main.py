"""
CatalogoCreator - Aplicación de creación de catálogos de productos.
Punto de entrada principal.
"""
import os
import sys
import threading
from typing import Dict, List, Optional

import flet as ft
from PIL import Image

from configuracion.constantes import (
    COLOR_FONDO_PRINCIPAL,
    COLOR_FONDO_SECUNDARIO,
    COLOR_FONDO_TARJETA,
    COLOR_ACENTO_PRIMARIO,
    COLOR_ACENTO_SECUNDARIO,
    COLOR_TEXTO_PRINCIPAL,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_EXITO,
    COLOR_ERROR,
    COLOR_BORDE,
    RADIO_BORDE,
    SUFIJO_FINALIZADO,
)
from modelos.producto import Producto
from modelos.categoria import Categoria
from modelos.configuracion_catalogo import ConfiguracionCatalogo
from servicios.servicio_archivos import ServicioArchivos
from servicios.servicio_remover_fondo import ServicioRemoverFondo
from servicios.servicio_composicion import ServicioComposicion
from servicios.servicio_texto import ServicioTexto
from servicios.servicio_deteccion_color import ServicioDeteccionColor
from utilidades.ayudantes_imagen import cargar_imagen
from vistas.vista_configuracion import VistaConfiguracion
from vistas.vista_edicion import VistaEdicion
from vistas.vista_previsualizacion import VistaPrevisualizacion


class AplicacionCatalogo:
    """Clase principal que orquesta toda la aplicación."""

    def __init__(self, pagina: ft.Page):
        self.pagina = pagina
        self.configuracion = ConfiguracionCatalogo()
        self.servicio_archivos = ServicioArchivos()
        self.servicio_remover_fondo = ServicioRemoverFondo()
        self.servicio_composicion = ServicioComposicion()
        self.servicio_texto = ServicioTexto()
        self.servicio_color = ServicioDeteccionColor()

        self._imagenes_compuestas: Dict[int, Image.Image] = {}
        self._productos: List[Producto] = []
        self._precios: List[str] = []
        self._imagenes_fondo_precio: List[str] = []

        self._vista_actual = None
        self._configurar_pagina()
        self._mostrar_vista_configuracion()

    def _configurar_pagina(self):
        """Configura las propiedades generales de la página."""
        self.pagina.title = "CatalogoCreator"
        self.pagina.theme_mode = ft.ThemeMode.DARK
        self.pagina.bgcolor = COLOR_FONDO_PRINCIPAL
        self.pagina.padding = 0
        self.pagina.window.width = 1100
        self.pagina.window.height = 800
        self.pagina.window.min_width = 900
        self.pagina.window.min_height = 700

        # Tema personalizado
        self.pagina.theme = ft.Theme(
            color_scheme_seed=COLOR_ACENTO_PRIMARIO,
            font_family="Roboto",
        )
        self.pagina.dark_theme = ft.Theme(
            color_scheme_seed=COLOR_ACENTO_PRIMARIO,
            font_family="Roboto",
        )

    def _limpiar_pagina(self):
        """Limpia los controles de la página."""
        self.pagina.controls.clear()

    # =========================================================================
    # VISTA 1: CONFIGURACIÓN
    # =========================================================================

    def _mostrar_vista_configuracion(self):
        """Muestra la vista de configuración inicial."""
        self._limpiar_pagina()
        vista = VistaConfiguracion(
            pagina=self.pagina,
            al_iniciar_proceso=self._al_iniciar_proceso,
        )
        self._vista_actual = vista
        self.pagina.add(vista)
        self.pagina.update()

    def _al_iniciar_proceso(self, configuracion: dict):
        """Callback cuando el usuario inicia el proceso desde la configuración."""
        self._mostrar_pantalla_procesamiento(configuracion)

    # =========================================================================
    # VISTA 2: PROCESAMIENTO (con barra de progreso)
    # =========================================================================

    def _mostrar_pantalla_procesamiento(self, configuracion: dict):
        """Muestra la pantalla de procesamiento con barra de progreso."""
        self._limpiar_pagina()

        self._etiqueta_estado_proceso = ft.Text(
            "Preparando...",
            size=16,
            weight=ft.FontWeight.W_600,
            color=COLOR_TEXTO_PRINCIPAL,
            text_align=ft.TextAlign.CENTER,
        )

        self._etiqueta_detalle_proceso = ft.Text(
            "",
            size=13,
            color=COLOR_TEXTO_SECUNDARIO,
            text_align=ft.TextAlign.CENTER,
        )

        self._barra_progreso_proceso = ft.ProgressBar(
            value=0,
            color=COLOR_ACENTO_PRIMARIO,
            bgcolor=COLOR_FONDO_TARJETA,
            height=6,
            border_radius=3,
            width=500,
        )

        self._porcentaje_proceso = ft.Text(
            "0%",
            size=14,
            color=COLOR_ACENTO_PRIMARIO,
            weight=ft.FontWeight.W_700,
        )

        contenido = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.HOURGLASS_TOP, size=64, color=COLOR_ACENTO_PRIMARIO),
                    ft.Text(
                        "Procesando catálogo",
                        size=24,
                        weight=ft.FontWeight.W_800,
                        color=COLOR_TEXTO_PRINCIPAL,
                    ),
                    ft.Container(height=20),
                    self._etiqueta_estado_proceso,
                    self._etiqueta_detalle_proceso,
                    ft.Container(height=10),
                    self._barra_progreso_proceso,
                    self._porcentaje_proceso,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

        self.pagina.add(contenido)
        self.pagina.update()

        # Ejecutar procesamiento en hilo separado para no bloquear la UI
        hilo = threading.Thread(
            target=self._ejecutar_procesamiento,
            args=(configuracion,),
            daemon=True,
        )
        hilo.start()

    def _actualizar_progreso(self, estado: str, detalle: str, progreso: float):
        """Actualiza la UI de progreso desde cualquier hilo."""
        try:
            self._etiqueta_estado_proceso.value = estado
            self._etiqueta_detalle_proceso.value = detalle
            self._barra_progreso_proceso.value = progreso
            self._porcentaje_proceso.value = f"{int(progreso * 100)}%"
            self.pagina.update()
        except Exception:
            pass

    def _ejecutar_procesamiento(self, configuracion: dict):
        """Ejecuta todo el pipeline de procesamiento."""
        try:
            # --- Paso 1: Escanear carpetas ---
            self._actualizar_progreso("📁 Escaneando carpetas...", "", 0.05)

            modo = configuracion.get("modo_entrada", "carpeta")
            if modo == "carpeta":
                categorias = self.servicio_archivos.escanear_carpeta_madre(
                    configuracion["ruta_carpeta_madre"]
                )
            else:
                categorias = self.servicio_archivos.escanear_imagen_individual(
                    configuracion["ruta_imagen_individual"]
                )

            if not categorias:
                self._actualizar_progreso("❌ No se encontraron imágenes", "", 0)
                return

            self.configuracion.categorias = categorias

            # Cargar fondos
            self.servicio_archivos.cargar_fondos_por_categoria(
                configuracion["ruta_carpeta_fondos"], categorias
            )

            # Cargar fondos de precio
            if configuracion.get("ruta_carpeta_fondos_precio"):
                self.servicio_archivos.cargar_fondos_precio_por_categoria(
                    configuracion["ruta_carpeta_fondos_precio"], categorias
                )

            # Cargar precios
            if configuracion.get("ruta_archivo_precios"):
                self._precios = self.servicio_archivos.leer_archivo_precios(
                    configuracion["ruta_archivo_precios"]
                )

            # Recopilar imágenes de fondo de precio
            self._imagenes_fondo_precio = []
            if configuracion.get("ruta_fondo_precio_unico"):
                self._imagenes_fondo_precio = [configuracion["ruta_fondo_precio_unico"]]
            elif configuracion.get("rutas_imagenes_fondo_precio_manual"):
                self._imagenes_fondo_precio = configuracion["rutas_imagenes_fondo_precio_manual"]
            else:
                for cat in categorias.values():
                    self._imagenes_fondo_precio.extend(cat.fondos_precio)

            self.configuracion.incluir_nombre = configuracion.get("incluir_nombre", True)

            # Lista plana de productos
            self._productos = self.configuracion.obtener_todos_los_productos()
            total_productos = len(self._productos)

            self._actualizar_progreso(
                f"📁 {total_productos} productos encontrados en {len(categorias)} categoría(s)",
                "",
                0.1,
            )

            # --- Paso 2: Crear carpetas de salida ---
            ruta_base = configuracion.get("ruta_carpeta_madre") or os.path.dirname(
                configuracion.get("ruta_imagen_individual", "")
            )
            rutas_salida = self.servicio_archivos.crear_estructura_salida(
                ruta_base, categorias
            )

            # --- Paso 3: Remover fondos ---
            self._actualizar_progreso("🔄 Removiendo fondos...", "", 0.15)

            for indice, producto in enumerate(self._productos):
                progreso_parcial = 0.15 + (0.45 * (indice / total_productos))
                nombre_corto = producto.obtener_nombre_limpio()
                self._actualizar_progreso(
                    "🔄 Removiendo fondos...",
                    f"Procesando: {nombre_corto} ({indice + 1}/{total_productos})",
                    progreso_parcial,
                )

                ruta_salida_cat = rutas_salida.get(producto.categoria, {}).get("convertido", "")
                nombre_png = f"{producto.nombre}.png"
                ruta_salida_img = os.path.join(ruta_salida_cat, nombre_png)

                ruta_guardada = self.servicio_remover_fondo.remover_fondo_y_guardar(
                    producto.ruta_original, ruta_salida_img
                )

                if ruta_guardada:
                    producto.ruta_sin_fondo = ruta_guardada

            # --- Paso 3.5: Remover fondos de imágenes de fondo de precio ---
            imagenes_precio_procesadas = []
            if self._imagenes_fondo_precio:
                self._actualizar_progreso("🏷️ Procesando fondos de precio...", "", 0.60)
                for ruta_fondo in self._imagenes_fondo_precio:
                    try:
                        img_test = Image.open(ruta_fondo)
                        if img_test.mode != "RGBA" or not img_test.getextrema()[3][0] < 255:
                            ruta_sin_fondo = ruta_fondo.replace(".", "_sin_fondo.", 1)
                            resultado = self.servicio_remover_fondo.remover_fondo_y_guardar(
                                ruta_fondo, ruta_sin_fondo
                            )
                            if resultado:
                                imagenes_precio_procesadas.append(resultado)
                            else:
                                imagenes_precio_procesadas.append(ruta_fondo)
                        else:
                            imagenes_precio_procesadas.append(ruta_fondo)
                    except Exception:
                        imagenes_precio_procesadas.append(ruta_fondo)

                self._imagenes_fondo_precio = imagenes_precio_procesadas

            # --- Paso 4: Componer sobre fondos ---
            self._actualizar_progreso("🎨 Componiendo imágenes...", "", 0.65)

            for indice, producto in enumerate(self._productos):
                progreso_parcial = 0.65 + (0.25 * (indice / total_productos))
                nombre_corto = producto.obtener_nombre_limpio()
                self._actualizar_progreso(
                    "🎨 Componiendo imágenes...",
                    f"Componiendo: {nombre_corto} ({indice + 1}/{total_productos})",
                    progreso_parcial,
                )

                if not producto.ruta_sin_fondo:
                    continue

                # Cargar imagen sin fondo
                imagen_producto = cargar_imagen(producto.ruta_sin_fondo)
                if not imagen_producto:
                    continue

                # Cargar fondo de categoría
                categoria = categorias.get(producto.categoria)
                if not categoria or not categoria.ruta_fondo:
                    # Si no hay fondo, usar la imagen sin fondo como compuesta
                    ruta_compuesta = os.path.join(
                        rutas_salida.get(producto.categoria, {}).get("compuesto", ""),
                        f"{producto.nombre}.png",
                    )
                    self.servicio_composicion.guardar_imagen(imagen_producto, ruta_compuesta)
                    producto.ruta_compuesta = ruta_compuesta
                    self._imagenes_compuestas[indice] = imagen_producto
                    continue

                imagen_fondo = cargar_imagen(categoria.ruta_fondo)
                if not imagen_fondo:
                    continue

                # Componer
                imagen_compuesta = self.servicio_composicion.componer_producto_sobre_fondo(
                    imagen_producto, imagen_fondo
                )

                # Guardar imagen compuesta (ANTES de agregar texto)
                ruta_compuesta = os.path.join(
                    rutas_salida.get(producto.categoria, {}).get("compuesto", ""),
                    f"{producto.nombre}.png",
                )
                self.servicio_composicion.guardar_imagen(imagen_compuesta, ruta_compuesta)
                producto.ruta_compuesta = ruta_compuesta
                self._imagenes_compuestas[indice] = imagen_compuesta

                # Asignar fondo de precio por categoría si existe
                if categoria.fondos_precio:
                    producto.ruta_fondo_precio = categoria.obtener_siguiente_fondo_precio()
                elif self._imagenes_fondo_precio:
                    producto.ruta_fondo_precio = self._imagenes_fondo_precio[
                        indice % len(self._imagenes_fondo_precio)
                    ]

                # Asignar precio del archivo si existe
                if indice < len(self._precios):
                    producto.precio = self._precios[indice]

                # Configurar inclusión de nombre
                producto.incluir_nombre = self.configuracion.incluir_nombre



            self._actualizar_progreso("✅ Procesamiento completado", "", 1.0)

            # Navegar a vista de edición
            self.pagina.run_task(self._navegar_a_edicion)

        except Exception as error:
            self._actualizar_progreso(f"❌ Error: {error}", "", 0)
            import traceback
            traceback.print_exc()

    async def _navegar_a_edicion(self):
        """Navega a la vista de edición (llamada desde hilo principal)."""
        import asyncio
        await asyncio.sleep(1)  # Pausa para que el usuario vea el 100%
        self._mostrar_vista_edicion()

    # =========================================================================
    # VISTA 3: EDICIÓN
    # =========================================================================

    def _mostrar_vista_edicion(self, indice_inicial: int = 0):
        """Muestra la vista de edición de precio y nombre."""
        self._limpiar_pagina()

        vista = VistaEdicion(
            pagina=self.pagina,
            productos=self._productos,
            precios=self._precios,
            incluir_nombre=self.configuracion.incluir_nombre,
            imagenes_fondo_precio=self._imagenes_fondo_precio,
            al_finalizar=self._al_finalizar_edicion,
            indice_inicial=indice_inicial,
        )

        # Registrar imágenes compuestas en la vista
        for indice, imagen in self._imagenes_compuestas.items():
            vista.registrar_imagen_compuesta(indice, imagen)

        self._vista_actual = vista
        self.pagina.add(vista)
        self.pagina.update()

    def _al_finalizar_edicion(self, productos: List[Producto]):
        """Callback cuando el usuario finaliza la edición."""
        self._productos = productos
        self._mostrar_vista_previsualizacion()

    # =========================================================================
    # VISTA 4: PREVISUALIZACIÓN
    # =========================================================================

    def _mostrar_vista_previsualizacion(self):
        """Muestra la vista de previsualización final."""
        self._limpiar_pagina()

        vista = VistaPrevisualizacion(
            pagina=self.pagina,
            productos=self._productos,
            imagenes_compuestas=self._imagenes_compuestas,
            al_editar_producto=self._al_editar_desde_preview,
            al_exportar=self._al_exportar,
        )

        self._vista_actual = vista
        self.pagina.add(vista)
        self.pagina.update()

    def _al_editar_desde_preview(self, indice: int):
        """Navega a edición para un producto específico desde la previsualización."""
        self._mostrar_vista_edicion(indice_inicial=indice)

    # =========================================================================
    # EXPORTACIÓN
    # =========================================================================

    def _al_exportar(self, productos: List[Producto]):
        """Exporta todas las imágenes finales a carpetas finalizadas."""
        # IMPORTANTE: Capturar las imágenes ANTES de limpiar la página
        imagenes_precapturadas = {}
        if hasattr(self._vista_actual, 'obtener_imagenes_finales'):
            imagenes_precapturadas = self._vista_actual.obtener_imagenes_finales()

        self._limpiar_pagina()

        self._etiqueta_estado_export = ft.Text(
            "Exportando...",
            size=16,
            weight=ft.FontWeight.W_600,
            color=COLOR_TEXTO_PRINCIPAL,
        )
        self._barra_progreso_export = ft.ProgressBar(
            value=0,
            color=COLOR_EXITO,
            bgcolor=COLOR_FONDO_TARJETA,
            height=6,
            width=500,
            border_radius=3,
        )

        contenido = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.SAVE_ALT, size=64, color=COLOR_EXITO),
                    ft.Text(
                        "Exportando catálogo",
                        size=24,
                        weight=ft.FontWeight.W_800,
                        color=COLOR_TEXTO_PRINCIPAL,
                    ),
                    self._etiqueta_estado_export,
                    self._barra_progreso_export,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
        self.pagina.add(contenido)
        self.pagina.update()

        # Exportar en hilo separado
        hilo = threading.Thread(
            target=self._ejecutar_exportacion,
            args=(productos, imagenes_precapturadas),
            daemon=True,
        )
        hilo.start()

    def _ejecutar_exportacion(self, productos: List[Producto], imagenes_precapturadas: dict = None):
        """Ejecuta la exportación de imágenes finales."""
        try:
            imagenes_finales = imagenes_precapturadas or {}

            if not imagenes_finales:
                # Regenerar desde los datos del producto
                servicio_texto = ServicioTexto()
                for indice, producto in enumerate(productos):
                    imagen_base = self._imagenes_compuestas.get(indice)
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

                    imagen_final = servicio_texto.generar_vista_previa(
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
                    imagenes_finales[indice] = imagen_final

            total = len(productos)
            for indice, producto in enumerate(productos):
                try:
                    self._etiqueta_estado_export.value = (
                        f"Guardando: {producto.obtener_nombre_limpio()} ({indice + 1}/{total})"
                    )
                    self._barra_progreso_export.value = (indice + 1) / total
                    self.pagina.update()
                except Exception:
                    pass

                imagen_final = imagenes_finales.get(indice)
                if not imagen_final:
                    continue

                # Determinar ruta de salida
                ruta_madre = self.configuracion.ruta_carpeta_madre
                carpeta_finalizada = f"{producto.categoria}{SUFIJO_FINALIZADO}"

                if ruta_madre:
                    ruta_carpeta_final = os.path.join(ruta_madre, carpeta_finalizada)
                else:
                    ruta_base = os.path.dirname(producto.ruta_original)
                    ruta_base_padre = os.path.dirname(ruta_base)
                    ruta_carpeta_final = os.path.join(ruta_base_padre, carpeta_finalizada)

                os.makedirs(ruta_carpeta_final, exist_ok=True)

                nombre_archivo = f"{producto.nombre}.png"
                ruta_final = os.path.join(ruta_carpeta_final, nombre_archivo)

                self.servicio_composicion.guardar_imagen(imagen_final, ruta_final)
                producto.ruta_final = ruta_final

            # Mostrar pantalla de éxito
            self.pagina.run_task(self._mostrar_exito, total)

        except Exception as error:
            try:
                self._etiqueta_estado_export.value = f"❌ Error: {error}"
                self.pagina.update()
            except Exception:
                pass

    async def _mostrar_exito(self, total: int):
        """Muestra la pantalla de éxito."""
        import asyncio
        await asyncio.sleep(0.5)

        self._limpiar_pagina()

        contenido = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=80, color=COLOR_EXITO),
                    ft.Text(
                        "¡Catálogo exportado exitosamente!",
                        size=26,
                        weight=ft.FontWeight.W_800,
                        color=COLOR_EXITO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        f"{total} imagen(es) guardada(s) en las carpetas finalizadas",
                        size=15,
                        color=COLOR_TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=30),
                    ft.ElevatedButton(
                        "🔄 Crear otro catálogo",
                        style=ft.ButtonStyle(
                            bgcolor=COLOR_ACENTO_PRIMARIO,
                            color=COLOR_TEXTO_PRINCIPAL,
                            padding=ft.padding.symmetric(horizontal=30, vertical=14),
                            shape=ft.RoundedRectangleBorder(radius=RADIO_BORDE),
                            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.W_600),
                        ),
                        on_click=lambda e: self._mostrar_vista_configuracion(),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

        self.pagina.add(contenido)
        self.pagina.update()


def main(pagina: ft.Page):
    """Punto de entrada de la aplicación Flet."""
    AplicacionCatalogo(pagina)


if __name__ == "__main__":
    ft.app(target=main)
