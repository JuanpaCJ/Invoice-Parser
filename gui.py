import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import threading

# Importar las funciones del archivo main.py
from main import procesar_factura, procesar_directorio

class FacturaProcessorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal - tamaño significativamente mayor
        self.title("Procesador de Facturas de Energía")
        self.geometry("800x600")  # Tamaño mucho más grande
        self.configure(padx=30, pady=30)  # Mayor padding
        
        # Variables para almacenar las selecciones del usuario
        self.has_selection = False
        self.selected_path = ""
        self.output_path = ""
        self.export_excel = True
        
        # Inicializar status_var (solo para uso interno, no se muestra)
        self.status_var = tk.StringVar()
        
        # Marco principal con padding
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Procesador de Facturas de Energía",
            font=("Arial", 20, "bold")  # Fuente aún más grande
        )
        title_label.pack(pady=(0, 30))
        
        # Botones para seleccionar archivo o carpeta
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        self.folder_button = ttk.Button(
            buttons_frame,
            text="Seleccionar carpeta",
            command=self.select_folder,
            width=30  # Botón más ancho
        )
        self.folder_button.pack(side=tk.LEFT, padx=(0, 30))
        
        self.pdf_button = ttk.Button(
            buttons_frame,
            text="Seleccionar archivo PDF",
            command=self.select_pdf,
            width=30  # Botón más ancho
        )
        self.pdf_button.pack(side=tk.LEFT)
        
        # Mostrar ruta seleccionada
        result_frame = ttk.LabelFrame(main_frame, text="Ruta seleccionada")
        result_frame.pack(fill=tk.X, expand=True, pady=20)
        
        self.path_var = tk.StringVar()
        self.path_var.set("No hay un archivo o carpeta seleccionada")
        
        self.path_label = ttk.Label(
            result_frame, 
            textvariable=self.path_var,
            wraplength=750,  # Permitir texto muy largo
            font=("Arial", 11)  # Fuente mejorada
        )
        self.path_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Opciones adicionales
        options_frame = ttk.LabelFrame(main_frame, text="Opciones")
        options_frame.pack(fill=tk.X, pady=20)
        
        # Opción para seleccionar carpeta de salida
        output_frame = ttk.Frame(options_frame)
        output_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        self.output_button = ttk.Button(
            output_frame,
            text="Seleccionar carpeta de salida",
            command=self.select_output_folder,
            width=35
        )
        self.output_button.pack(side=tk.LEFT)
        
        self.output_var = tk.StringVar()
        self.output_var.set("Usar carpeta predeterminada")
        
        ttk.Label(
            output_frame,
            textvariable=self.output_var,
            wraplength=400,
            font=("Arial", 11)
        ).pack(side=tk.LEFT, padx=20)
        
        # Opción para exportar a Excel
        excel_frame = ttk.Frame(options_frame)
        excel_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        self.excel_var = tk.BooleanVar(value=True)
        
        excel_check = ttk.Checkbutton(
            excel_frame,
            text="Exportar a Excel",
            variable=self.excel_var,
            command=self.toggle_excel
        )
        excel_check.pack(side=tk.LEFT)
        
        # Botones de acción (con más espacio y ubicados más abajo)
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(30, 0))
        
        self.process_button = ttk.Button(
            action_frame,
            text="Procesar",
            command=self.process_selection,
            width=25  # Botón aún más ancho
        )
        self.process_button.pack(side=tk.RIGHT, padx=(20, 0))
        
        cancel_button = ttk.Button(
            action_frame,
            text="Salir",
            command=self.destroy,
            width=25  # Botón aún más ancho
        )
        cancel_button.pack(side=tk.RIGHT, padx=20)
    
    def select_folder(self):
        """Seleccionar una carpeta con facturas"""
        folder_path = filedialog.askdirectory(
            title="Seleccione una carpeta"
        )
        
        if folder_path:
            self.path_var.set(folder_path)
            self.has_selection = True
            self.selected_path = folder_path
            self.process_button.config(state=tk.NORMAL)
        else:
            self.path_var.set("No hay un archivo o carpeta seleccionada")
    
    def select_pdf(self):
        """Seleccionar un archivo PDF"""
        file_path = filedialog.askopenfilename(
            title="Escoger archivo .PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )
        
        if file_path:
            if file_path.lower().endswith('.pdf'):
                self.path_var.set(file_path)
                self.has_selection = True
                self.selected_path = file_path
                self.process_button.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Error", "El archivo seleccionado no está en formato .PDF")
                self.path_var.set("No hay un archivo o carpeta seleccionada")
        else:
            self.path_var.set("No hay un archivo o carpeta seleccionada")
    
    def select_output_folder(self):
        """Seleccionar carpeta de salida"""
        output_path = filedialog.askdirectory(
            title="Seleccione carpeta de salida"
        )
        
        if output_path:
            self.output_var.set(f"Salida: {os.path.basename(output_path)}")
            self.output_path = output_path
        else:
            self.output_var.set("Usar carpeta predeterminada")
            self.output_path = ""
    
    def toggle_excel(self):
        """Cambiar la opción de exportar a Excel"""
        self.export_excel = self.excel_var.get()
    
    def process_selection(self):
        """Procesar la selección (archivo o carpeta)"""
        if not self.has_selection:
            messagebox.showwarning("Advertencia", "No hay una selección válida")
            return
        
        # Deshabilitar botón durante el procesamiento
        self.process_button.config(state=tk.DISABLED)
        
        # Crear un hilo para el procesamiento para no bloquear la interfaz
        thread = threading.Thread(target=self.run_processing)
        thread.daemon = True
        thread.start()
    
    def run_processing(self):
        """Ejecuta el procesamiento en un hilo separado"""
        try:
            # Verificar si es archivo o carpeta
            if os.path.isfile(self.selected_path):
                # Es un archivo PDF
                resultado = procesar_factura(
                    self.selected_path,
                    self.output_path if self.output_path else None,
                    self.export_excel
                )
                
                if resultado:
                    self.show_success_message("El archivo ha sido procesado correctamente.")
                else:
                    self.show_error_message("No se pudo procesar el archivo.")
            
            elif os.path.isdir(self.selected_path):
                # Es un directorio
                resultado = procesar_directorio(
                    self.selected_path,
                    self.output_path if self.output_path else None
                )
                
                if resultado:
                    self.show_success_message(f"Carpeta procesada correctamente.\nExcel generado en: {resultado}")
                else:
                    self.show_error_message("No se pudo procesar la carpeta seleccionada.")
            
            else:
                self.show_error_message("La ruta seleccionada no es válida.")
        
        except Exception as e:
            self.show_error_message(f"Ocurrió un error durante el procesamiento:\n{str(e)}")
        
        # Rehabilitar el botón de procesar cuando termine
        self.after(0, lambda: self.process_button.config(state=tk.NORMAL))
    
    def show_success_message(self, message):
        """Muestra un mensaje de éxito"""
        self.after(0, lambda: messagebox.showinfo("Éxito", message))
    
    def show_error_message(self, message):
        """Muestra un mensaje de error"""
        self.after(0, lambda: messagebox.showerror("Error", message))

# Para cuando se ejecute este script directamente
if __name__ == "__main__":
    app = FacturaProcessorGUI()
    app.mainloop()