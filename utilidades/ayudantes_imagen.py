"""
Funciones auxiliares para trabajar con imágenes en la aplicación.
"""
import base64
import io
import os
from typing import Optional, Tuple

from PIL import Image


def imagen_a_base64(imagen: Image.Image, formato: str = "PNG") -> str:
    """
    Convierte una imagen PIL a string base64 para mostrar en Flet.

    Args:
        imagen: Imagen PIL.
        formato: Formato de salida ('PNG' o 'JPEG').

    Returns:
        String base64 de la imagen.
    """
    buffer = io.BytesIO()
    if imagen.mode == "RGBA" and formato.upper() == "JPEG":
        fondo = Image.new("RGB", imagen.size, (255, 255, 255))
        fondo.paste(imagen, mask=imagen.split()[3])
        fondo.save(buffer, format="JPEG", quality=85)
    else:
        imagen.save(buffer, format=formato)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def cargar_imagen(ruta: str) -> Optional[Image.Image]:
    """
    Carga una imagen desde una ruta de archivo.

    Args:
        ruta: Ruta absoluta al archivo de imagen.

    Returns:
        Imagen PIL o None si no se puede cargar.
    """
    if not ruta or not os.path.isfile(ruta):
        return None

    try:
        return Image.open(ruta).convert("RGBA")
    except Exception as error:
        print(f"Error al cargar imagen '{ruta}': {error}")
        return None


def redimensionar_para_vista_previa(
    imagen: Image.Image,
    ancho_maximo: int = 500,
    alto_maximo: int = 500,
) -> Image.Image:
    """
    Redimensiona una imagen manteniendo proporciones para vista previa.

    Args:
        imagen: Imagen PIL original.
        ancho_maximo: Ancho máximo para la vista previa.
        alto_maximo: Alto máximo para la vista previa.

    Returns:
        Imagen redimensionada.
    """
    ancho_original, alto_original = imagen.size

    ratio = min(ancho_maximo / ancho_original, alto_maximo / alto_original)
    if ratio >= 1.0:
        return imagen.copy()

    nuevo_ancho = int(ancho_original * ratio)
    nuevo_alto = int(alto_original * ratio)

    return imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)


def rgb_a_hex(color_rgb: Tuple[int, int, int]) -> str:
    """Convierte un color RGB a formato hexadecimal."""
    return "#{:02x}{:02x}{:02x}".format(*color_rgb)


def hex_a_rgb(color_hex: str) -> Tuple[int, int, int]:
    """Convierte un color hexadecimal a formato RGB."""
    color_hex = color_hex.lstrip("#")
    return tuple(int(color_hex[i:i + 2], 16) for i in (0, 2, 4))
