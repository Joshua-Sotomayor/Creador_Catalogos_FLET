"""
Modelo de datos para una categoría de productos.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from modelos.producto import Producto


@dataclass
class Categoria:
    """Representa una categoría de productos (corresponde a una subcarpeta)."""

    nombre: str
    ruta_fondo: Optional[str] = None
    productos: List[Producto] = field(default_factory=list)
    fondos_precio: List[str] = field(default_factory=list)
    _indice_fondo_precio: int = field(default=0, repr=False)

    def obtener_siguiente_fondo_precio(self) -> Optional[str]:
        """
        Retorna el siguiente fondo de precio de forma alternada.
        Si no hay fondos de precio disponibles, retorna None.
        """
        if not self.fondos_precio:
            return None

        fondo = self.fondos_precio[self._indice_fondo_precio % len(self.fondos_precio)]
        self._indice_fondo_precio += 1
        return fondo

    def cantidad_productos(self) -> int:
        """Retorna la cantidad de productos en esta categoría."""
        return len(self.productos)
