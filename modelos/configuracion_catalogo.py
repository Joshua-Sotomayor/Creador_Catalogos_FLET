"""
Modelo de configuración global del catálogo.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from modelos.categoria import Categoria


@dataclass
class ConfiguracionCatalogo:
    """Almacena toda la configuración del catálogo en proceso."""

    ruta_carpeta_madre: Optional[str] = None
    ruta_carpeta_fondos: Optional[str] = None
    ruta_carpeta_fondos_precio: Optional[str] = None
    ruta_fondo_precio_unico: Optional[str] = None
    ruta_archivo_precios: Optional[str] = None
    incluir_nombre: bool = True
    categorias: Dict[str, Categoria] = field(default_factory=dict)
    lista_precios: List[str] = field(default_factory=list)
    ruta_salida: Optional[str] = None
    imagenes_fondo_precio_manual: List[str] = field(default_factory=list)

    def obtener_todos_los_productos(self) -> list:
        """Retorna una lista plana de todos los productos de todas las categorías."""
        todos_los_productos = []
        for categoria in self.categorias.values():
            todos_los_productos.extend(categoria.productos)
        return todos_los_productos

    def cantidad_total_productos(self) -> int:
        """Retorna el número total de productos en todas las categorías."""
        return sum(cat.cantidad_productos() for cat in self.categorias.values())
