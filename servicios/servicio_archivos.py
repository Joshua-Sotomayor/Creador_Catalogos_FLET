"""
Servicio para gestión de archivos y carpetas.
Escaneo de carpetas, lectura de precios, creación de estructura de salida.
"""
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from configuracion.constantes import (
    EXTENSIONES_IMAGEN,
    EXTENSIONES_PRECIOS,
    SUFIJO_CONVERTIDO,
    SUFIJO_COMPUESTO,
    SUFIJO_FINALIZADO,
)
from modelos.producto import Producto
from modelos.categoria import Categoria


class ServicioArchivos:
    """Gestiona operaciones de lectura/escritura en el sistema de archivos."""

    @staticmethod
    def escanear_carpeta_madre(ruta_carpeta: str) -> Dict[str, Categoria]:
        """
        Escanea la carpeta madre y construye un diccionario de categorías.
        Cada subcarpeta es una categoría. Las imágenes dentro son productos.

        Args:
            ruta_carpeta: Ruta absoluta a la carpeta madre.

        Returns:
            Diccionario donde la clave es el nombre de categoría y el valor es un objeto Categoria.
        """
        if not ruta_carpeta or not os.path.isdir(ruta_carpeta):
            return {}

        categorias: Dict[str, Categoria] = {}
        ruta = Path(ruta_carpeta)

        for subcarpeta in sorted(ruta.iterdir()):
            if not subcarpeta.is_dir():
                # Si hay imágenes sueltas en la raíz, crear categoría "general"
                if subcarpeta.suffix.lower() in EXTENSIONES_IMAGEN:
                    nombre_categoria = "general"
                    if nombre_categoria not in categorias:
                        categorias[nombre_categoria] = Categoria(nombre=nombre_categoria)
                    producto = Producto(
                        nombre=subcarpeta.stem,
                        ruta_original=str(subcarpeta),
                        categoria=nombre_categoria,
                    )
                    categorias[nombre_categoria].productos.append(producto)
                continue

            nombre_categoria = subcarpeta.name.lower()
            categoria = Categoria(nombre=nombre_categoria)

            for archivo in sorted(subcarpeta.iterdir()):
                if archivo.is_file() and archivo.suffix.lower() in EXTENSIONES_IMAGEN:
                    producto = Producto(
                        nombre=archivo.stem,
                        ruta_original=str(archivo),
                        categoria=nombre_categoria,
                    )
                    categoria.productos.append(producto)

            if categoria.productos:
                categorias[nombre_categoria] = categoria

        return categorias

    @staticmethod
    def escanear_imagen_individual(ruta_imagen: str) -> Dict[str, Categoria]:
        """
        Crea una estructura de categoría para una imagen individual.

        Args:
            ruta_imagen: Ruta a la imagen individual.

        Returns:
            Diccionario con una categoría 'individual'.
        """
        if not ruta_imagen or not os.path.isfile(ruta_imagen):
            return {}

        archivo = Path(ruta_imagen)
        if archivo.suffix.lower() not in EXTENSIONES_IMAGEN:
            return {}

        categoria = Categoria(nombre="individual")
        producto = Producto(
            nombre=archivo.stem,
            ruta_original=str(archivo),
            categoria="individual",
        )
        categoria.productos.append(producto)
        return {"individual": categoria}

    @staticmethod
    def cargar_fondos_por_categoria(ruta_carpeta_fondos: str, categorias: Dict[str, Categoria]) -> None:
        """
        Asigna imágenes de fondo a cada categoría basándose en el nombre de subcarpeta.

        Args:
            ruta_carpeta_fondos: Ruta a la carpeta que contiene fondos organizados por subcarpetas.
            categorias: Diccionario de categorías a actualizar.
        """
        if not ruta_carpeta_fondos or not os.path.isdir(ruta_carpeta_fondos):
            return

        ruta = Path(ruta_carpeta_fondos)

        # Buscar en subcarpetas
        for subcarpeta in ruta.iterdir():
            if subcarpeta.is_dir():
                nombre_cat = subcarpeta.name.lower()
                if nombre_cat in categorias:
                    for archivo in subcarpeta.iterdir():
                        if archivo.is_file() and archivo.suffix.lower() in EXTENSIONES_IMAGEN:
                            categorias[nombre_cat].ruta_fondo = str(archivo)
                            break  # Usar la primera imagen encontrada

            # También buscar imágenes sueltas cuyo nombre coincida con categoría
            elif subcarpeta.is_file() and subcarpeta.suffix.lower() in EXTENSIONES_IMAGEN:
                nombre_sin_ext = subcarpeta.stem.lower()
                if nombre_sin_ext in categorias:
                    categorias[nombre_sin_ext].ruta_fondo = str(subcarpeta)

    @staticmethod
    def cargar_fondos_precio_por_categoria(
        ruta_carpeta: str, categorias: Dict[str, Categoria]
    ) -> None:
        """
        Carga imágenes de fondo para precios organizadas por categoría.

        Args:
            ruta_carpeta: Ruta a la carpeta con subcarpetas de fondos de precio.
            categorias: Diccionario de categorías a actualizar.
        """
        if not ruta_carpeta or not os.path.isdir(ruta_carpeta):
            return

        ruta = Path(ruta_carpeta)

        for subcarpeta in ruta.iterdir():
            if not subcarpeta.is_dir():
                continue

            nombre_cat = subcarpeta.name.lower()
            if nombre_cat in categorias:
                for archivo in sorted(subcarpeta.iterdir()):
                    if archivo.is_file() and archivo.suffix.lower() in EXTENSIONES_IMAGEN:
                        categorias[nombre_cat].fondos_precio.append(str(archivo))

    @staticmethod
    def leer_archivo_precios(ruta_archivo: str) -> List[str]:
        """
        Lee un archivo de precios (txt o csv) y retorna lista de precios.

        Args:
            ruta_archivo: Ruta al archivo de precios.

        Returns:
            Lista de strings con los precios.
        """
        if not ruta_archivo or not os.path.isfile(ruta_archivo):
            return []

        precios = []
        archivo = Path(ruta_archivo)

        if archivo.suffix.lower() not in EXTENSIONES_PRECIOS:
            return []

        try:
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                for linea in f:
                    precio_limpio = linea.strip()
                    if precio_limpio:
                        precios.append(precio_limpio)
        except Exception:
            return []

        return precios

    @staticmethod
    def crear_carpeta_salida(ruta_base: str, nombre_carpeta: str) -> str:
        """
        Crea una carpeta de salida y retorna su ruta.

        Args:
            ruta_base: Ruta base donde crear la carpeta.
            nombre_carpeta: Nombre de la carpeta a crear.

        Returns:
            Ruta absoluta de la carpeta creada.
        """
        ruta_salida = os.path.join(ruta_base, nombre_carpeta)
        os.makedirs(ruta_salida, exist_ok=True)
        return ruta_salida

    @staticmethod
    def crear_estructura_salida(
        ruta_base: str, categorias: Dict[str, Categoria]
    ) -> Dict[str, Dict[str, str]]:
        """
        Crea toda la estructura de carpetas de salida.

        Args:
            ruta_base: Ruta base del proyecto.
            categorias: Diccionario de categorías.

        Returns:
            Diccionario con rutas de salida organizadas por categoría y tipo.
        """
        rutas = {}
        for nombre_cat in categorias:
            rutas[nombre_cat] = {
                "convertido": ServicioArchivos.crear_carpeta_salida(
                    ruta_base, f"{nombre_cat}{SUFIJO_CONVERTIDO}"
                ),
                "compuesto": ServicioArchivos.crear_carpeta_salida(
                    ruta_base, f"{nombre_cat}{SUFIJO_COMPUESTO}"
                ),
                "finalizado": ServicioArchivos.crear_carpeta_salida(
                    ruta_base, f"{nombre_cat}{SUFIJO_FINALIZADO}"
                ),
            }
        return rutas

    @staticmethod
    def cargar_imagenes_sueltas(rutas_archivos: List[str]) -> List[str]:
        """
        Filtra y retorna rutas de archivos que sean imágenes válidas.

        Args:
            rutas_archivos: Lista de rutas de archivos.

        Returns:
            Lista filtrada de rutas a imágenes válidas.
        """
        imagenes_validas = []
        for ruta in rutas_archivos:
            if os.path.isfile(ruta) and Path(ruta).suffix.lower() in EXTENSIONES_IMAGEN:
                imagenes_validas.append(ruta)
        return imagenes_validas
