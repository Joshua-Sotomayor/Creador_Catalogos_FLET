"""
Modelo de datos para un producto del catálogo.
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass
class Producto:
    """Representa un producto individual dentro del catálogo."""

    nombre: str
    ruta_original: str
    categoria: str
    ruta_sin_fondo: Optional[str] = None
    ruta_compuesta: Optional[str] = None
    ruta_final: Optional[str] = None
    precio: Optional[str] = None
    posicion_precio: Optional[Tuple[int, int]] = None  # (fila, columna) en grilla 5x5
    posicion_nombre: Optional[Tuple[int, int]] = None   # (fila, columna) en grilla 3x3
    alineacion_nombre: str = "centro"
    color_texto_precio: Optional[Tuple[int, int, int]] = None  # RGB
    color_texto_nombre: Optional[Tuple[int, int, int]] = None  # RGB
    ruta_fondo_precio: Optional[str] = None
    incluir_nombre: bool = True
    aprobado: bool = False

    def obtener_nombre_limpio(self) -> str:
        """Retorna el nombre del producto sin extensión de archivo."""
        import os
        nombre_archivo = os.path.basename(self.nombre)
        nombre_sin_extension, _ = os.path.splitext(nombre_archivo)
        return nombre_sin_extension.replace("_", " ").replace("-", " ").title()

    def esta_completo(self) -> bool:
        """Verifica si el producto tiene toda la información necesaria para exportar."""
        return (
            self.ruta_compuesta is not None
            and self.precio is not None
            and self.posicion_precio is not None
        )
