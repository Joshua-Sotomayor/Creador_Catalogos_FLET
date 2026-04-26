import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--name', 'CatalogoCreator',
    '--copy-metadata', 'pymatting',
    '--copy-metadata', 'rembg',
    '--copy-metadata', 'pooch',
    '--windowed',
    '--clean',
    '-y'
])
