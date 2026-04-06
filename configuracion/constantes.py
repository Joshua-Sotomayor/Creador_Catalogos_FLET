"""
Constantes globales para la aplicación CatalogoCreator.
"""

# === Extensiones de archivo soportadas ===
EXTENSIONES_IMAGEN = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff'}
EXTENSIONES_PRECIOS = {'.txt', '.csv'}

# === Sufijos de carpetas ===
SUFIJO_CONVERTIDO = "_png_convert"
SUFIJO_COMPUESTO = "_compuesto"
SUFIJO_FINALIZADO = "_finalizado"

# === Dimensiones de grilla ===
FILAS_GRILLA_PRECIO = 5
COLUMNAS_GRILLA_PRECIO = 5
FILAS_GRILLA_NOMBRE = 3
COLUMNAS_GRILLA_NOMBRE = 3

# === Configuración de fuente ===
TAMANO_FUENTE_PRECIO = 48
TAMANO_FUENTE_NOMBRE = 36
NOMBRE_FUENTE_PREDETERMINADA = "Roboto-Bold.ttf"
RUTA_FUENTES = "assets/fuentes"

# === Colores de la interfaz (tema oscuro) ===
COLOR_FONDO_PRINCIPAL = "#1a1a2e"
COLOR_FONDO_SECUNDARIO = "#16213e"
COLOR_FONDO_TARJETA = "#0f3460"
COLOR_ACENTO_PRIMARIO = "#e94560"
COLOR_ACENTO_SECUNDARIO = "#533483"
COLOR_TEXTO_PRINCIPAL = "#ffffff"
COLOR_TEXTO_SECUNDARIO = "#a0a0b0"
COLOR_BORDE = "#2a2a4a"
COLOR_EXITO = "#4caf50"
COLOR_ADVERTENCIA = "#ff9800"
COLOR_ERROR = "#f44336"
COLOR_CELDA_SELECCIONADA = "#e94560"
COLOR_CELDA_NORMAL = "#16213e"
COLOR_CELDA_HOVER = "#533483"

# === Tamaños de UI ===
ANCHO_PANEL_LATERAL = 400
ALTO_VISTA_PREVIA = 500
ANCHO_VISTA_PREVIA = 500
TAMANO_CELDA_GRILLA = 40
RADIO_BORDE = 12
ESPACIADO_GENERAL = 16

# === Modos de asignación de precio ===
MODO_AUTOMATICO = "automatico"
MODO_MANUAL = "manual"
MODO_SELECCION_FONDO = "seleccion_fondo"

# === Alineaciones de texto ===
ALINEACION_IZQUIERDA = "izquierda"
ALINEACION_CENTRO = "centro"
ALINEACION_DERECHA = "derecha"
