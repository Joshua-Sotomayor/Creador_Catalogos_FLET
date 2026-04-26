"""
Servicio para composición de imágenes.
Centra producto sobre fondo, agrega fondo de precio, etc.
"""
import os
from typing import Optional, Tuple

from PIL import Image

from configuracion.constantes import (
    FILAS_GRILLA_PRECIO,
    COLUMNAS_GRILLA_PRECIO,
)


class ServicioComposicion:
    """Gestiona la composición y superposición de imágenes."""

    @staticmethod
    def componer_producto_sobre_fondo(
        imagen_producto: Image.Image,
        imagen_fondo: Image.Image,
        escala_producto: float = 0.7,
    ) -> Image.Image:
        """
        Centra la imagen del producto sobre el fondo de categoría.

        Args:
            imagen_producto: Imagen PIL del producto (RGBA, sin fondo).
            imagen_fondo: Imagen PIL del fondo de categoría.
            escala_producto: Factor de escala del producto respecto al fondo (0.0 a 1.0).

        Returns:
            Imagen compuesta con el producto centrado sobre el fondo.
        """
        fondo = imagen_fondo.copy().convert("RGBA")
        ancho_fondo, alto_fondo = fondo.size

        # Redimensionar producto manteniendo proporción
        producto = imagen_producto.copy().convert("RGBA")
        ancho_producto, alto_producto = producto.size

        # Calcular dimensiones máximas del producto en el fondo
        max_ancho = int(ancho_fondo * escala_producto)
        max_alto = int(alto_fondo * escala_producto)

        # Escalar manteniendo relación de aspecto
        ratio_ancho = max_ancho / ancho_producto
        ratio_alto = max_alto / alto_producto
        ratio = min(ratio_ancho, ratio_alto)

        nuevo_ancho = int(ancho_producto * ratio)
        nuevo_alto = int(alto_producto * ratio)
        producto_redimensionado = producto.resize(
            (nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS
        )

        # Centrar producto en el fondo
        posicion_x = (ancho_fondo - nuevo_ancho) // 2
        posicion_y = (alto_fondo - nuevo_alto) // 2

        # Componer usando alpha del producto como máscara
        fondo.paste(producto_redimensionado, (posicion_x, posicion_y), producto_redimensionado)

        return fondo

    @staticmethod
    def agregar_fondo_precio(
        imagen_base: Image.Image,
        imagen_fondo_precio: Image.Image,
        posicion_celda: Tuple[int, int],
        filas_grilla: int = FILAS_GRILLA_PRECIO,
        columnas_grilla: int = COLUMNAS_GRILLA_PRECIO,
        escala_fondo_precio: float = 0.15,
    ) -> Image.Image:
        """
        Coloca la imagen de fondo del precio en la posición de la grilla indicada.

        Args:
            imagen_base: Imagen sobre la cual colocar el fondo del precio.
            imagen_fondo_precio: Imagen PNG del fondo para el precio.
            posicion_celda: Tupla (fila, columna) de la celda en la grilla.
            filas_grilla: Número de filas de la grilla.
            columnas_grilla: Número de columnas de la grilla.
            escala_fondo_precio: Escala del fondo de precio respecto al tamaño de la imagen base.

        Returns:
            Imagen con el fondo del precio colocado.
        """
        resultado = imagen_base.copy().convert("RGBA")
        fondo_precio = imagen_fondo_precio.copy().convert("RGBA")

        ancho_base, alto_base = resultado.size
        fila, columna = posicion_celda

        # Redimensionar fondo de precio
        tamano_fondo = int(min(ancho_base, alto_base) * escala_fondo_precio)
        fondo_precio_redim = fondo_precio.resize(
            (tamano_fondo, tamano_fondo), Image.Resampling.LANCZOS
        )

        # Calcular posición del centro de la celda
        ancho_celda = ancho_base / columnas_grilla
        alto_celda = alto_base / filas_grilla
        centro_x = int(columna * ancho_celda + ancho_celda / 2)
        centro_y = int(fila * alto_celda + alto_celda / 2)

        # Ajustar para centrar la imagen del fondo de precio
        pos_x = centro_x - tamano_fondo // 2
        pos_y = centro_y - tamano_fondo // 2

        # Asegurar que no se salga de los bordes
        pos_x = max(0, min(pos_x, ancho_base - tamano_fondo))
        pos_y = max(0, min(pos_y, alto_base - tamano_fondo))

        resultado.paste(fondo_precio_redim, (pos_x, pos_y), fondo_precio_redim)
        return resultado

    @staticmethod
    def guardar_imagen(imagen: Image.Image, ruta_destino: str) -> bool:
        """
        Guarda una imagen PIL en la ruta especificada.

        Args:
            imagen: Imagen PIL a guardar.
            ruta_destino: Ruta de destino.

        Returns:
            True si se guardó correctamente, False en caso contrario.
        """
        try:
            os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)

            if ruta_destino.lower().endswith(".png"):
                imagen.save(ruta_destino, "PNG")
            elif ruta_destino.lower().endswith((".jpg", ".jpeg")):
                # Convertir a RGB si estamos en RGBA
                if imagen.mode == "RGBA":
                    fondo_blanco = Image.new("RGB", imagen.size, (255, 255, 255))
                    fondo_blanco.paste(imagen, mask=imagen.split()[3])
                    fondo_blanco.save(ruta_destino, "JPEG", quality=95)
                else:
                    imagen.save(ruta_destino, "JPEG", quality=95)
            else:
                imagen.save(ruta_destino, "PNG")

            return True
        except Exception as error:
            print(f"Error al guardar imagen en '{ruta_destino}': {error}")
            return False
