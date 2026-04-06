"""
Servicio para detección de color dominante y propuesta de color de contraste.
"""
from typing import Tuple, Optional

from PIL import Image


class ServicioDeteccionColor:
    """Analiza imágenes para proponer colores de texto con buen contraste."""

    @staticmethod
    def obtener_color_dominante(
        imagen: Image.Image,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Tuple[int, int, int]:
        """
        Obtiene el color dominante de una imagen o región específica.

        Args:
            imagen: Imagen PIL a analizar.
            region: Tupla (x1, y1, x2, y2) para analizar solo esa región.
                    Si es None, analiza toda la imagen.

        Returns:
            Tupla RGB del color dominante.
        """
        if region:
            imagen_recortada = imagen.crop(region)
        else:
            imagen_recortada = imagen.copy()

        # Reducir imagen para acelerar el análisis
        imagen_pequena = imagen_recortada.resize((50, 50), Image.Resampling.LANCZOS)
        imagen_rgb = imagen_pequena.convert("RGB")

        # Obtener colores más frecuentes
        colores = imagen_rgb.getcolors(maxcolors=2500)
        if not colores:
            return (128, 128, 128)

        # Ordenar por frecuencia (descendente)
        colores_ordenados = sorted(colores, key=lambda x: x[0], reverse=True)

        # Retornar el más frecuente
        return colores_ordenados[0][1]

    @staticmethod
    def calcular_luminancia(color_rgb: Tuple[int, int, int]) -> float:
        """
        Calcula la luminancia relativa de un color RGB.

        Args:
            color_rgb: Tupla (R, G, B).

        Returns:
            Luminancia relativa (0.0 a 1.0).
        """
        r, g, b = color_rgb
        # Fórmula de luminancia relativa (BT.709)
        return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0

    @staticmethod
    def obtener_color_contraste(
        imagen: Image.Image,
        posicion_celda: Tuple[int, int],
        filas_grilla: int = 5,
        columnas_grilla: int = 5,
    ) -> Tuple[int, int, int]:
        """
        Propone un color de texto que contraste con la región donde se colocará.

        Args:
            imagen: Imagen base.
            posicion_celda: Tupla (fila, columna) de la celda.
            filas_grilla: Número de filas de la grilla.
            columnas_grilla: Número de columnas de la grilla.

        Returns:
            Tupla RGB del color propuesto (blanco o negro según contraste).
        """
        ancho, alto = imagen.size
        fila, columna = posicion_celda

        # Calcular la región de la celda
        ancho_celda = ancho / columnas_grilla
        alto_celda = alto / filas_grilla
        x1 = int(columna * ancho_celda)
        y1 = int(fila * alto_celda)
        x2 = int((columna + 1) * ancho_celda)
        y2 = int((fila + 1) * alto_celda)

        # Asegurar que la región es válida
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(ancho, x2)
        y2 = min(alto, y2)

        color_dominante = ServicioDeteccionColor.obtener_color_dominante(
            imagen, region=(x1, y1, x2, y2)
        )

        luminancia = ServicioDeteccionColor.calcular_luminancia(color_dominante)

        # Si la región es oscura, usar texto claro; si es clara, usar texto oscuro
        if luminancia < 0.5:
            return (255, 255, 255)  # Blanco
        else:
            return (30, 30, 30)  # Casi negro

    @staticmethod
    def obtener_color_contraste_avanzado(
        imagen: Image.Image,
        posicion_celda: Tuple[int, int],
        filas_grilla: int = 5,
        columnas_grilla: int = 5,
    ) -> Tuple[int, int, int]:
        """
        Propone un color de texto más sofisticado basado en los colores del fondo.
        Intenta ofrecer un color que sea estéticamente agradable y no solo blanco/negro.

        Args:
            imagen: Imagen base.
            posicion_celda: Tupla (fila, columna).
            filas_grilla: Filas de la grilla.
            columnas_grilla: Columnas de la grilla.

        Returns:
            Tupla RGB del color propuesto.
        """
        ancho, alto = imagen.size
        fila, columna = posicion_celda

        ancho_celda = ancho / columnas_grilla
        alto_celda = alto / filas_grilla
        x1 = max(0, int(columna * ancho_celda))
        y1 = max(0, int(fila * alto_celda))
        x2 = min(ancho, int((columna + 1) * ancho_celda))
        y2 = min(alto, int((fila + 1) * alto_celda))

        color_fondo = ServicioDeteccionColor.obtener_color_dominante(
            imagen, region=(x1, y1, x2, y2)
        )
        luminancia = ServicioDeteccionColor.calcular_luminancia(color_fondo)

        if luminancia < 0.3:
            # Fondo muy oscuro → texto dorado cálido
            return (255, 215, 0)
        elif luminancia < 0.5:
            # Fondo medio-oscuro → texto blanco
            return (255, 255, 255)
        elif luminancia < 0.7:
            # Fondo medio-claro → texto azul oscuro
            return (25, 25, 112)
        else:
            # Fondo claro → texto oscuro elegante
            return (40, 40, 40)
