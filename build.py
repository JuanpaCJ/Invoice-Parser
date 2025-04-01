# Modificación para build_exe.py
import os
import sys
import subprocess
import shutil
import platform
import base64
import tempfile

def instalar_dependencias():
    """Instala PyInstaller y otras dependencias necesarias si no están ya instaladas."""
    try:
        import PyInstaller
        print("PyInstaller ya está instalado.")
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
    
    # Asegurarse de que las dependencias del proyecto estén instaladas
    print("Instalando dependencias del proyecto...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def generar_icono_desde_base64(base64_data=None):
    """
    Genera un archivo de ícono a partir de un string en base64 o permite seleccionarlo.
    Retorna la ruta al archivo de ícono temporal.
    """
    if base64_data:
        # Usar el ícono proporcionado en base64
        try:
            # Crear un directorio temporal si no existe
            temp_dir = os.path.join(tempfile.gettempdir(), "factura_processor_temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Guardar el ícono decodificado en un archivo temporal
            icon_path = os.path.join(temp_dir, "app_icon.ico")
            with open(icon_path, "wb") as icon_file:
                icon_file.write(base64.b64decode(base64_data))
            
            print(f"Ícono generado en: {icon_path}")
            return icon_path
        except Exception as e:
            print(f"Error al generar el ícono desde base64: {e}")
            return None
    else:
        # Permitir al usuario seleccionar un archivo de ícono
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()  # Ocultar la ventana principal de Tkinter
            
            print("Por favor seleccione un archivo de ícono (.ico):")
            icon_path = filedialog.askopenfilename(
                title="Seleccionar archivo de ícono",
                filetypes=[("Archivo de ícono", "*.ico")]
            )
            
            if not icon_path:
                print("No se seleccionó ningún archivo de ícono.")
                return None
                
            print(f"Ícono seleccionado: {icon_path}")
            return icon_path
        except Exception as e:
            print(f"Error al seleccionar el ícono: {e}")
            return None

def convertir_a_base64(icon_path):
    """Convierte un archivo a base64 y lo imprime."""
    try:
        with open(icon_path, "rb") as icon_file:
            base64_data = base64.b64encode(icon_file.read()).decode('utf-8')
        
        print("\n=== ÍCONO EN FORMATO BASE64 (copia esto para uso futuro) ===")
        print(f"ICON_BASE64 = \"\"\"{base64_data}\"\"\"")
        print("=========================================================\n")
        
        return base64_data
    except Exception as e:
        print(f"Error al convertir el ícono a base64: {e}")
        return None

def crear_ejecutable(icon_path=None):
    """Crea el ejecutable utilizando PyInstaller."""
    print("Creando ejecutable...")
    
    # Nombre del archivo ejecutable
    nombre_ejecutable = "ProcesadorFacturas"
    
    # Opciones básicas de PyInstaller
    opciones = [
        "--onefile",               # Crear un solo archivo
        "--windowed",              # No mostrar consola en Windows
        "--clean",                 # Limpiar archivos temporales antes de construir
        "--name", nombre_ejecutable,
        "--hidden-import", "tkinter",
        "--hidden-import", "customtkinter",
        "--hidden-import", "PIL",
        "--hidden-import", "openpyxl",
        "--hidden-import", "pdfminer",
    ]
    
    # Añadir el ícono si está disponible
    if icon_path and os.path.exists(icon_path):
        opciones.extend(["--icon", icon_path])
        print(f"Usando ícono: {icon_path}")
    else:
        print("No se especificó un ícono válido. Se usará el ícono predeterminado.")
    
    # Añadir el punto de entrada
    opciones.append("gui.py")
    
    # Ejecutar PyInstaller
    subprocess.check_call([sys.executable, "-m", "PyInstaller"] + opciones)
    
    # Limpiar dirección de salida
    print(f"Ejecutable creado: {os.path.abspath(os.path.join('dist', nombre_ejecutable + '.exe' if platform.system() == 'Windows' else nombre_ejecutable))}")

def limpiar_archivos_temporales():
    """Limpia archivos temporales generados durante el proceso de construcción."""
    nombre_ejecutable = "ProcesadorFacturas"
    directorios_a_limpiar = ["build", "__pycache__"]
    archivos_a_limpiar = [f"{nombre_ejecutable}.spec"]
    
    for directorio in directorios_a_limpiar:
        if os.path.exists(directorio):
            try:
                shutil.rmtree(directorio)
                print(f"Directorio {directorio} eliminado.")
            except Exception as e:
                print(f"Error al eliminar {directorio}: {e}")
    
    for archivo in archivos_a_limpiar:
        if os.path.exists(archivo):
            try:
                os.remove(archivo)
                print(f"Archivo {archivo} eliminado.")
            except Exception as e:
                print(f"Error al eliminar {archivo}: {e}")

def main():
    """Función principal."""
    print("=== CREADOR DE EJECUTABLE PARA PROCESADOR DE FACTURAS ===")
    
    # Instalar dependencias necesarias
    instalar_dependencias()
    
    # Ícono predefinido en base64 (puedes reemplazar este valor con tu propio ícono codificado)
    # Nota: Esta es solo una variable de ejemplo. Si está vacía, se solicitará un archivo de ícono.
    ICON_BASE64 = ""
    
    # Preguntar cómo quiere proporcionar el ícono
    print("\n=== CONFIGURACIÓN DEL ÍCONO DE LA APLICACIÓN ===")
    print("1. Usar ícono codificado en base64 predefinido")
    print("2. Seleccionar un archivo de ícono (.ico)")
    print("3. No usar ícono personalizado")
    
    opcion = input("Seleccione una opción (1-3): ").strip()
    
    icon_path = None
    if opcion == "1":
        if ICON_BASE64:
            icon_path = generar_icono_desde_base64(ICON_BASE64)
        else:
            print("No hay un ícono base64 predefinido. Por favor, ingrese el string base64:")
            base64_input = input().strip()
            if base64_input:
                icon_path = generar_icono_desde_base64(base64_input)
            else:
                print("No se proporcionó ningún ícono en base64.")
    elif opcion == "2":
        icon_path = generar_icono_desde_base64()  # Llama sin argumentos para solicitar selección de archivo
        if icon_path:
            # Ofrecer convertir el ícono seleccionado a base64 para uso futuro
            convertir = input("¿Desea convertir este ícono a base64 para uso futuro? (s/n): ").strip().lower()
            if convertir == "s":
                convertir_a_base64(icon_path)
    elif opcion == "3":
        print("No se usará un ícono personalizado.")
    else:
        print("Opción no válida. No se usará un ícono personalizado.")
    
    # Crear el ejecutable con el ícono (si está disponible)
    crear_ejecutable(icon_path)
    
    # Preguntar al usuario si desea limpiar los archivos temporales
    respuesta = input("¿Desea eliminar los archivos temporales de la construcción? (s/n): ").strip().lower()
    if respuesta == "s":
        limpiar_archivos_temporales()
    
    print("Proceso completado exitosamente.")

if __name__ == "__main__":
    main()