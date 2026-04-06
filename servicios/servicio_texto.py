"""
Servicio para agregar texto (precio y nombre) sobre imágenes.
"""
import os
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from configuracion.constantes import (
    TAMANO_FUENTE_PRECIO,
    TAMANO_FUENTE_NOMBRE,
    RUTA_FUENTES,
    NOMBRE_FUENTE_PREDETERMINADA,
    ALINEACION_CENTRO,
    ALINEACION_IZQUIERDA,
    ALINEACION_DERECHA,
)


class ServicioTexto:
    """Agrega texto (precio, nombre) sobre imágenes en posiciones específicas."""

    def __init__(self):
        self._fuente_cache = {}

    def _obtener_fuente(self, tamano: int) -> ImageFont.FreeTypeFont:
        """
        Obtiene una fuente del caché o la carga del sistema de archivos.

        Args:
            tamano: Tamaño de la fuente en píxeles.

        Returns:
            Objeto ImageFont.
        """
        if tamano in self._fuente_cache:
            return self._fuente_cache[tamano]

        ruta_fuente = os.path.join(RUTA_FUENTES, NOMBRE_FUENTE_PREDETERMINADA)

        try:
            if os.path.isfile(ruta_fuente):
                fuente = ImageFont.truetype(ruta_fuente, tamano)
            else:
                # Intentar con fuentes del sistema
                fuentes_sistema = [
                    "arial.ttf",
                    "Arial.ttf",
                    "arialbd.ttf",
                    "Roboto-Bold.ttf",
                    "DejaVuSans-Bold.ttf",
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/arialbd.ttf",
                ]
                fuente = None
                for fuente_sistema in fuentes_sistema:
                    try:
                        fuente = ImageFont.truetype(fuente_sistema, tamano)
                        break
                    except OSError:
                        continue

                if fuente is None:
                    fuente = ImageFont.load_default()

        except OSError:
            fuente = ImageFont.load_default()

        self._fuente_cache[tamano] = fuente
        return fuente

    @staticmethod
    def _calcular_posicion_celda(
        ancho_imagen: int,
        alto_imagen: int,
        fila: int,
        columna: int,
        filas_total: int,
        columnas_total: int,
    ) -> Tuple[int, int]:
        """
        Calcula las coordenadas (x, y) del centro de una celda en la grilla.

        Args:
            ancho_imagen: Ancho de la imagen en píxeles.
            alto_imagen: Alto de la imagen en píxeles.
            fila: Fila de la celda (0-indexed).
            columna: Columna de la celda (0-indexed).
            filas_total: Número total de filas.
            columnas_total: Número total de columnas.

        Returns:
            Tupla (x, y) del centro de la celda.
        """
        ancho_celda = ancho_imagen / columnas_total
        alto_celda = alto_imagen / filas_total

        centro_x = int(columna * ancho_celda + ancho_celda / 2)
        centro_y = int(fila * alto_celda + alto_celda / 2)

        return (centro_x, centro_y)

    def agregar_precio(
        self,
        imagen: Image.Image,
        texto_precio: str,
        posicion_celda: Tuple[int, int],
        color: Tuple[int, int, int] = (255, 255, 255),
        tamano_fuente: Optional[int] = None,
        filas_grilla: int = 5,
        columnas_grilla: int = 5,
    ) -> Image.Image:
        """
        Agrega el texto del precio sobre la imagen en la posición de grilla indicada.

        Args:
            imagen: Imagen PIL sobre la cual colocar el precio.
            texto_precio: Texto del precio (ej: "$29.99").
            posicion_celda: Tupla (fila, columna) de la celda en la grilla.
            color: Color RGB del texto.
            tamano_fuente: Tamaño de la fuente (usa predeterminado si es None).
            filas_grilla: Número de filas de la grilla.
            columnas_grilla: Número de columnas de la grilla.

        Returns:
            Imagen con el precio agregado.
        """
        resultado = imagen.copy().convert("RGBA")
        dibujo = ImageDraw.Draw(resultado)

        if tamano_fuente is None:
            # Escalar fuente según tamaño de imagen
            tamano_fuente = max(20, int(min(resultado.size) * 0.06))

        fuente = self._obtener_fuente(tamano_fuente)
        fila, columna = posicion_celda

        centro_x, centro_y = self._calcular_posicion_celda(
            resultado.width, resultado.height,
            fila, columna, filas_grilla, columnas_grilla,
        )

        # Agregar sombra sutil para legibilidad
        color_sombra = (0, 0, 0, 150)
        desplazamiento_sombra = max(1, tamano_fuente // 20)

        dibujo.text(
            (centro_x + desplazamiento_sombra, centro_y + desplazamiento_sombra),
            texto_precio,
            fill=color_sombra,
            font=fuente,
            anchor="mm",
        )

        dibujo.text(
            (centro_x, centro_y),
            texto_precio,
            fill=color + (255,),
            font=fuente,
            anchor="mm",
        )

        return resultado

    def agregar_nombre(
        self,
        imagen: Image.Image,
        nombre: str,
        posicion_celda: Tuple[int, int],
        alineacion: str = ALINEACION_CENTRO,
        color: Tuple[int, int, int] = (255, 255, 255),
        tamano_fuente: Optional[int] = None,
        filas_grilla: int = 3,
        columnas_grilla: int = 3,
    ) -> Image.Image:
        """
        Agrega el nombre del producto sobre la imagen.

        Args:
            imagen: Imagen PIL.
            nombre: Nombre del producto.
            posicion_celda: Tupla (fila, columna) en grilla 3x3.
            alineacion: 'izquierda', 'centro', o 'derecha'.
            color: Color RGB del texto.
            tamano_fuente: Tamaño de la fuente.
            filas_grilla: Filas de la grilla.
            columnas_grilla: Columnas de la grilla.

        Returns:
            Imagen con el nombre agregado.
        """
        resultado = imagen.copy().convert("RGBA")
        dibujo = ImageDraw.Draw(resultado)

        if tamano_fuente is None:
            tamano_fuente = max(16, int(min(resultado.size) * 0.045))

        fuente = self._obtener_fuente(tamano_fuente)
        fila, columna = posicion_celda

        centro_x, centro_y = self._calcular_posicion_celda(
            resultado.width, resultado.height,
            fila, columna, filas_grilla, columnas_grilla,
        )

        # Mapear alineación a anchor de Pillow
        mapa_alineacion = {
            ALINEACION_IZQUIERDA: "lm",   # left-middle
            ALINEACION_CENTRO: "mm",       # middle-middle
            ALINEACION_DERECHA: "rm",      # right-middle
        }
        anchor = mapa_alineacion.get(alineacion, "mm")

        # Ajustar posición x según alineación
        ancho_celda = resultado.width / columnas_grilla
        if alineacion == ALINEACION_IZQUIERDA:
            centro_x = int(columna * ancho_celda + ancho_celda * 0.1)
        elif alineacion == ALINEACION_DERECHA:
            centro_x = int((columna + 1) * ancho_celda - ancho_celda * 0.1)

        # Sombra
        color_sombra = (0, 0, 0, 150)
        desplazamiento = max(1, tamano_fuente // 20)

        dibujo.text(
            (centro_x + desplazamiento, centro_y + desplazamiento),
            nombre,
            fill=color_sombra,
            font=fuente,
            anchor=anchor,
        )

        dibujo.text(
            (centro_x, centro_y),
            nombre,
            fill=color + (255,),
            font=fuente,
            anchor=anchor,
        )

        return resultado

    def generar_vista_previa(
        self,
        imagen_base: Image.Image,
        texto_precio: Optional[str] = None,
        posicion_precio: Optional[Tuple[int, int]] = None,
        color_precio: Tuple[int, int, int] = (255, 255, 255),
        nombre_producto: Optional[str] = None,
        posicion_nombre: Optional[Tuple[int, int]] = None,
        alineacion_nombre: str = ALINEACION_CENTRO,
        color_nombre: Tuple[int, int, int] = (255, 255, 255),
        imagen_fondo_precio: Optional[Image.Image] = None,
    ) -> Image.Image:
        """
        Genera una vista previa completa con todos los elementos aplicados.

        Args:
            imagen_base: Imagen compuesta (producto + fondo).
            texto_precio: Texto del precio.
            posicion_precio: Posición del precio en grilla 5x5.
            color_precio: Color del precio.
            nombre_producto: Nombre del producto.
            posicion_nombre: Posición del nombre en grilla 3x3.
            alineacion_nombre: Alineación del nombre.
            color_nombre: Color del nombre.
            imagen_fondo_precio: Imagen de fondo para el precio.

        Returns:
            Imagen de vista previa completa.
        """
        from servicios.servicio_composicion import ServicioComposicion

        resultado = imagen_base.copy()

        # 1. Agregar fondo de precio si existe
        if imagen_fondo_precio and posicion_precio:
            resultado = ServicioComposicion.agregar_fondo_precio(
                resultado, imagen_fondo_precio, posicion_precio
            )

        # 2. Agregar nombre si existe
        if nombre_producto and posicion_nombre:
            resultado = self.agregar_nombre(
                resultado, nombre_producto, posicion_nombre,
                alineacion_nombre, color_nombre,
            )

        # 3. Agregar precio si existe
        if texto_precio and posicion_precio:
            resultado = self.agregar_precio(
                resultado, texto_precio, posicion_precio, color_precio,
            )

        return resultado
