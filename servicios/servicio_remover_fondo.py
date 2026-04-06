"""
Servicio para remoción de fondo de imágenes usando rembg.
"""
import os
from pathlib import Path
from typing import Callable, Optional

from PIL import Image
from rembg import remove


class ServicioRemoverFondo:
    """Gestiona la remoción de fondo de imágenes usando rembg (procesamiento local)."""

    @staticmethod
    def remover_fondo(ruta_imagen: str) -> Optional[Image.Image]:
        """
        Remueve el fondo de una imagen individual.

        Args:
            ruta_imagen: Ruta absoluta a la imagen.

        Returns:
            Imagen PIL en modo RGBA sin fondo, o None si falla.
        """
        if not ruta_imagen or not os.path.isfile(ruta_imagen):
            return None

        try:
            with open(ruta_imagen, "rb") as archivo_entrada:
                datos_entrada = archivo_entrada.read()

            datos_salida = remove(datos_entrada)

            from io import BytesIO
            imagen_resultado = Image.open(BytesIO(datos_salida)).convert("RGBA")
            return imagen_resultado

        except Exception as error:
            print(f"Error al remover fondo de '{ruta_imagen}': {error}")
            return None

    @staticmethod
    def remover_fondo_y_guardar(
        ruta_imagen: str,
        ruta_salida: str,
    ) -> Optional[str]:
        """
        Remueve el fondo y guarda la imagen resultante como PNG.

        Args:
            ruta_imagen: Ruta a la imagen original.
            ruta_salida: Ruta donde guardar la imagen sin fondo.

        Returns:
            Ruta del archivo guardado, o None si falla.
        """
        imagen_sin_fondo = ServicioRemoverFondo.remover_fondo(ruta_imagen)
        if imagen_sin_fondo is None:
            return None

        try:
            os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
            imagen_sin_fondo.save(ruta_salida, "PNG")
            return ruta_salida
        except Exception as error:
            print(f"Error al guardar imagen sin fondo: {error}")
            return None

    @staticmethod
    def procesar_lote(
        lista_rutas: list,
        ruta_carpeta_salida: str,
        callback_progreso: Optional[Callable[[int, int, str], None]] = None,
    ) -> list:
        """
        Procesa un lote de imágenes removiendo el fondo de cada una.

        Args:
            lista_rutas: Lista de tuplas (ruta_original, nombre_archivo).
            ruta_carpeta_salida: Carpeta donde guardar los resultados.
            callback_progreso: Función callback(actual, total, nombre) para reportar progreso.

        Returns:
            Lista de tuplas (ruta_original, ruta_salida) de las imágenes procesadas exitosamente.
        """
        resultados = []
        total = len(lista_rutas)

        for indice, (ruta_original, nombre_archivo) in enumerate(lista_rutas):
            if callback_progreso:
                callback_progreso(indice + 1, total, nombre_archivo)

            nombre_png = Path(nombre_archivo).stem + ".png"
            ruta_salida = os.path.join(ruta_carpeta_salida, nombre_png)

            ruta_guardada = ServicioRemoverFondo.remover_fondo_y_guardar(
                ruta_original, ruta_salida
            )

            if ruta_guardada:
                resultados.append((ruta_original, ruta_guardada))

        return resultados
