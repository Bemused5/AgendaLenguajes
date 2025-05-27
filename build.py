import PyInstaller.__main__
import os

# Obtener la ruta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'src/main.py',  # Archivo principal de la aplicación
    '--name=AgendaLenguajes',  # Nombre del ejecutable
    '--onefile',  # Crear un solo archivo ejecutable
    '--windowed',  # No mostrar consola
    '--add-data=src:src',  # Incluir archivos de la carpeta src
    '--icon=src/assets/icon.icns',  # Icono de la aplicación (si existe)
    '--clean',  # Limpiar archivos temporales
    '--noconfirm',  # No pedir confirmación
]) 
