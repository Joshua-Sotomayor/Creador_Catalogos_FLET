# CatalogoCreator

Aplicacion de escritorio para la creacion automatizada de catalogos de productos con remocion de fondo, composicion sobre fondos decorativos, y edicion de texto (precio y nombre).

## Requisitos del sistema

| Requisito | Version minima |
|-----------|---------------|
| Python | 3.10 |
| Sistema operativo | Windows 10/11 |
| RAM | 4 GB (recomendado 8 GB) |
| Espacio en disco | 500 MB (dependencias + modelos IA) |

## Instalacion

1. Clonar o descargar el repositorio.
2. Crear un entorno virtual:
   ```
   python -m venv venv
   ```
3. Activar el entorno virtual:
   ```
   .\venv\Scripts\activate
   ```
4. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```
5. Ejecutar la aplicacion:
   ```
   python main.py
   ```

## Dependencias

| Paquete | Proposito |
|---------|-----------|
| flet | Framework de interfaz grafica |
| Pillow | Manipulacion de imagenes |
| rembg | Remocion de fondo con IA |
| numpy | Procesamiento numerico (dependencia de rembg) |

## Estructura de carpetas esperada

La aplicacion espera la siguiente estructura de carpetas como entrada:

```
carpeta_madre/
    categoria_1/
        producto_1.jpg
        producto_2.png
        ...
    categoria_2/
        producto_a.jpg
        ...

carpeta_fondos/
    categoria_1/
        fondo.jpg
    categoria_2/
        fondo.png
```

### Carpetas generadas automaticamente

| Carpeta | Contenido |
|---------|-----------|
| `categoria_png_convert` | Imagenes con fondo removido (PNG transparente) |
| `categoria_compuesto` | Imagenes compuestas sobre el fondo decorativo |
| `categoria_finalizado` | Imagenes finales con precio y nombre aplicados |

## Flujo de uso

1. **Pantalla de inicio**: Seleccionar carpetas de entrada, fondos, y opciones.
2. **Procesamiento**: La aplicacion remueve fondos y compone imagenes automaticamente.
3. **Edicion**: Configurar posicion, tamano y color del precio y nombre para cada producto.
4. **Previsualizacion**: Revisar todas las imagenes finales.
5. **Exportacion**: Guardar las imagenes en las carpetas finalizadas.

### Conversion rapida

Desde la pantalla de inicio es posible convertir imagenes individuales o carpetas completas a PNG sin fondo, sin necesidad de crear un catalogo completo. Las imagenes se guardan en una carpeta con el sufijo `_png_convert`.

## Caracteristicas

- Remocion de fondo automatica con inteligencia artificial (rembg)
- Composicion de producto sobre fondos decorativos por categoria
- Grilla de posicion 6x6 para ubicar precio y nombre
- Tamano independiente para texto de precio, etiqueta de fondo y nombre
- Selector de color con propuesta automatica de contraste
- Selector de fuente tipografica (sistema y personalizadas)
- Previsualizacion en tiempo real
- Exportacion por lotes a carpetas organizadas
- Conversion rapida de imagenes sin catalogo

## Estructura del codigo fuente

| Directorio | Descripcion |
|------------|-------------|
| `main.py` | Punto de entrada y orquestador principal |
| `configuracion/` | Constantes y configuracion global |
| `modelos/` | Clases de datos (Producto, Categoria, Configuracion) |
| `servicios/` | Logica de negocio (remocion de fondo, composicion, texto) |
| `componentes/` | Componentes de UI reutilizables |
| `vistas/` | Pantallas principales de la aplicacion |
| `utilidades/` | Funciones auxiliares (conversion de imagenes, colores) |
| `assets/` | Recursos estaticos (fuentes tipograficas) |

### Servicios

| Servicio | Funcion |
|----------|---------|
| `servicio_archivos.py` | Escaneo de carpetas y lectura de archivos |
| `servicio_remover_fondo.py` | Remocion de fondo con rembg |
| `servicio_composicion.py` | Composicion de producto sobre fondo |
| `servicio_texto.py` | Renderizado de texto sobre imagenes |
| `servicio_deteccion_color.py` | Deteccion de color de contraste optimo |

### Vistas

| Vista | Funcion |
|-------|---------|
| `vista_configuracion.py` | Pantalla de inicio con seleccion de carpetas y conversion rapida |
| `vista_edicion.py` | Editor de precio, nombre, posicion y estilo por producto |
| `vista_previsualizacion.py` | Galeria de previsualizacion con opciones de editar o guardar |

## Licencia

Proyecto academico. Uso interno.

## Generar Ejecutable (.exe)
Para convertir el proyecto en un ejecutable de Windows independiente:

`ash
flet pack main.py --name "CatalogoCreator" --pyinstaller-build-args "--copy-metadata" "pymatting" "--copy-metadata" "rembg"
``n
El archivo ejecutable se generará dentro de la carpeta dist/.
