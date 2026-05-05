import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--name', 'CatalogoCreator',
    # Incluir metadata de paquetes que la necesitan
    '--copy-metadata', 'pymatting',
    '--copy-metadata', 'rembg',
    '--copy-metadata', 'pooch',
    # Recolectar TODO de rembg y flet (modelos, assets, DLLs)
    '--collect-all', 'rembg',
    '--collect-all', 'flet',
    '--collect-all', 'flet_runtime',
    # Imports ocultos que PyInstaller no detecta
    '--hidden-import', 'pymatting',
    '--hidden-import', 'pooch',
    '--hidden-import', 'scipy',
    '--hidden-import', 'PIL',
    # Modo carpeta (mas compatible entre computadoras)
    '--onedir',
    '--windowed',
    '--clean',
    '-y',
])
