import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Importar las funciones del archivo main.py
from main import procesar_factura, procesar_directorio

# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")  # Modos: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

class FacturaProcessorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal - tamaño reducido
        self.title("Procesador de Facturas")
        self.geometry("500x630")  # Tamaño reducido para laptop
        
        # Variables para almacenar las selecciones del usuario
        self.has_selection = False
        self.selected_path = ""
        self.output_path = ""
        self.export_excel = True
        
        # Inicializar status_var (solo para uso interno)
        self.status_var = ctk.StringVar()
        
        # Crear el contenedor principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Título con logo
        self.title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, padx=15, pady=(15, 20), sticky="ew")
        self.title_frame.grid_columnconfigure(1, weight=1)
        
        # Cargar y mostrar el logo personalizado
        self.load_and_display_logo()
        
        # Título
        self.title_label = ctk.CTkLabel(
            self.title_frame, 
            text="Procesador de Facturas",
            font=ctk.CTkFont(size=20, weight="bold")  # Tamaño de fuente reducido
        )
        self.title_label.grid(row=0, column=1, sticky="w")
        
        # Sección de selección de archivos
        self.selection_frame = ctk.CTkFrame(self.main_frame)
        self.selection_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.selection_frame.grid_columnconfigure(0, weight=1)
        self.selection_frame.grid_columnconfigure(1, weight=1)
        
        # Botones para seleccionar archivo o carpeta
        self.folder_button = ctk.CTkButton(
            self.selection_frame,
            text="Seleccionar carpeta",
            command=self.select_folder,
            height=32,  # Altura reducida
            font=ctk.CTkFont(size=12),  # Tamaño de fuente reducido
            fg_color="#3a7ebf",
            hover_color="#2b5d8b"
        )
        self.folder_button.grid(row=0, column=0, padx=(15, 8), pady=15, sticky="ew")
        
        self.pdf_button = ctk.CTkButton(
            self.selection_frame,
            text="Seleccionar archivo PDF",
            command=self.select_pdf,
            height=32,  # Altura reducida
            font=ctk.CTkFont(size=12),  # Tamaño de fuente reducido
            fg_color="#3a7ebf",
            hover_color="#2b5d8b"
        )
        self.pdf_button.grid(row=0, column=1, padx=(8, 15), pady=15, sticky="ew")
        
        # Mostrar ruta seleccionada
        self.path_frame = ctk.CTkFrame(self.main_frame)
        self.path_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.path_frame.grid_columnconfigure(0, weight=1)
        
        self.path_label_title = ctk.CTkLabel(
            self.path_frame,
            text="Ruta seleccionada:",
            font=ctk.CTkFont(size=12, weight="bold"),  # Tamaño de fuente reducido
            anchor="w"
        )
        self.path_label_title.grid(row=0, column=0, padx=15, pady=(10, 3), sticky="w")
        
        self.path_var = ctk.StringVar()
        self.path_var.set("No hay un archivo o carpeta seleccionada")
        
        self.path_label = ctk.CTkLabel(
            self.path_frame, 
            textvariable=self.path_var,
            wraplength=700,  # Ancho reducido
            font=ctk.CTkFont(size=11),  # Tamaño de fuente reducido
            anchor="w",
            justify="left"
        )
        self.path_label.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        # Opciones adicionales
        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.options_frame.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.options_frame.grid_columnconfigure(0, weight=1)
        
        self.options_label = ctk.CTkLabel(
            self.options_frame,
            text="Opciones",
            font=ctk.CTkFont(size=14, weight="bold"),  # Tamaño de fuente reducido
            anchor="w"
        )
        self.options_label.grid(row=0, column=0, padx=15, pady=(10, 10), sticky="w")
        
        # Opción para seleccionar carpeta de salida
        self.output_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.output_frame.grid(row=1, column=0, padx=15, pady=(0, 8), sticky="ew")
        self.output_frame.grid_columnconfigure(1, weight=1)
        
        self.output_button = ctk.CTkButton(
            self.output_frame,
            text="Seleccionar carpeta de salida",
            command=self.select_output_folder,
            width=180,  # Ancho reducido
            height=28,  # Altura reducida
            font=ctk.CTkFont(size=11),  # Tamaño de fuente reducido
            fg_color="#3a7ebf",
            hover_color="#2b5d8b"
        )
        self.output_button.grid(row=0, column=0, padx=(0, 10), pady=3)
        
        self.output_var = ctk.StringVar()
        self.output_var.set("Usar carpeta predeterminada")
        
        self.output_label = ctk.CTkLabel(
            self.output_frame,
            textvariable=self.output_var,
            wraplength=350,  # Ancho reducido
            font=ctk.CTkFont(size=11),  # Tamaño de fuente reducido
            anchor="w"
        )
        self.output_label.grid(row=0, column=1, padx=0, pady=3, sticky="w")
        
        # Opción para exportar a Excel
        self.excel_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.excel_frame.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")
        
        self.excel_var = ctk.BooleanVar(value=True)
        
        self.excel_check = ctk.CTkCheckBox(
            self.excel_frame,
            text="Exportar a Excel",
            variable=self.excel_var,
            command=self.toggle_excel,
            font=ctk.CTkFont(size=11),  # Tamaño de fuente reducido
            checkbox_width=20,  # Tamaño reducido
            checkbox_height=20  # Tamaño reducido
        )
        self.excel_check.grid(row=0, column=0, padx=0, pady=3, sticky="w")
        
        # Área de estado y progreso
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.grid(row=4, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label_title = ctk.CTkLabel(
            self.status_frame,
            text="Estado:",
            font=ctk.CTkFont(size=12, weight="bold"),  # Tamaño de fuente reducido
            anchor="w"
        )
        self.status_label_title.grid(row=0, column=0, padx=15, pady=(10, 3), sticky="w")
        
        self.status_text = ctk.StringVar()
        self.status_text.set("Listo para procesar")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            textvariable=self.status_text,
            font=ctk.CTkFont(size=11),  # Tamaño de fuente reducido
            anchor="w"
        )
        self.status_label.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        # Barra de progreso (inicialmente oculta)
        self.progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()  # Ocultar hasta que se necesite
        
        # Botones de acción y selector de tema en el mismo frame
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.grid(row=5, column=0, padx=15, pady=(5, 15), sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)
        
        # Selector de tema (ahora en el frame de acción)
        self.theme_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        self.theme_frame.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.theme_label = ctk.CTkLabel(
            self.theme_frame,
            text="Tema:",
            font=ctk.CTkFont(size=12),  # Tamaño de fuente reducido
        )
        self.theme_label.grid(row=0, column=0, padx=(0, 8))
        
        self.theme_option = ctk.CTkOptionMenu(
            self.theme_frame,
            values=["Oscuro", "Claro"],
            command=self.change_appearance_mode,
            width=100,  # Ancho reducido
            height=28,  # Altura reducida
            font=ctk.CTkFont(size=11)  # Tamaño de fuente reducido
        )
        self.theme_option.grid(row=0, column=1)
        self.theme_option.set("Oscuro")
        
        # Botón de salir
        self.cancel_button = ctk.CTkButton(
            self.action_frame,
            text="Salir",
            command=self.destroy,
            width=120,  # Ancho reducido
            height=35,  # Altura reducida
            font=ctk.CTkFont(size=13),  # Tamaño de fuente reducido
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.cancel_button.grid(row=0, column=1, padx=(0, 8), pady=5)
        
        # Botón de procesar
        self.process_button = ctk.CTkButton(
            self.action_frame,
            text="Procesar",
            command=self.process_selection,
            width=120,  # Ancho reducido
            height=35,  # Altura reducida
            font=ctk.CTkFont(size=13, weight="bold"),  # Tamaño de fuente reducido
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.process_button.grid(row=0, column=2, padx=(0, 0), pady=5)
        self.process_button.configure(state="disabled")
    
    def load_and_display_logo(self):
        """Carga y muestra el logo personalizado según el tema actual"""
        try:
            # Crear directorio para recursos si no existe
            resources_dir = "resources"
            if not os.path.exists(resources_dir):
                os.makedirs(resources_dir)
            
            # Rutas para los logos
            logo_dark_path = os.path.join(resources_dir, "logo_dark.png")  # Logo blanco para modo oscuro
            logo_light_path = os.path.join(resources_dir, "logo_light.png")  # Logo azul para modo claro
            
            # URLs de los logos
            logo_dark_url = "https://lh3.googleusercontent.com/d/1gbCShPnlbhAY3p1DIWijFQSF8BbVrTN3=w1001"  # Logo blanco
            logo_light_url = "https://lh3.googleusercontent.com/d/1KC9qOMhPBjX45zahNTQqNGJUbjLiQe9O=w1001"  # Logo azul
            
            # Descargar los logos si no existen
            if not os.path.exists(logo_dark_path):
                try:
                    import urllib.request
                    urllib.request.urlretrieve(logo_dark_url, logo_dark_path)
                    print(f"Logo para modo oscuro descargado en: {logo_dark_path}")
                except Exception as e:
                    print(f"Error al descargar el logo para modo oscuro: {e}")
            
            if not os.path.exists(logo_light_path):
                try:
                    import urllib.request
                    urllib.request.urlretrieve(logo_light_url, logo_light_path)
                    print(f"Logo para modo claro descargado en: {logo_light_path}")
                except Exception as e:
                    print(f"Error al descargar el logo para modo claro: {e}")
            
            # Verificar si los logos existen
            dark_logo_exists = os.path.exists(logo_dark_path)
            light_logo_exists = os.path.exists(logo_light_path)
            
            if dark_logo_exists and light_logo_exists:
                # Cargar ambos logos
                dark_image = Image.open(logo_dark_path)
                dark_image = dark_image.resize((140, 70))  # Tamaño reducido
                
                light_image = Image.open(logo_light_path)
                light_image = light_image.resize((140, 70))  # Tamaño reducido
                
                # Crear CTkImage con ambos logos
                self.logo_ctk = ctk.CTkImage(
                    light_image=light_image,  # Logo azul para modo claro
                    dark_image=dark_image,    # Logo blanco para modo oscuro
                    size=(140, 70)  # Tamaño reducido
                )
                
                # Mostrar el logo
                self.logo_label = ctk.CTkLabel(
                    self.title_frame,
                    image=self.logo_ctk,
                    text=""
                )
                self.logo_label.grid(row=0, column=0, padx=(0, 10))
                
            elif dark_logo_exists:
                # Solo tenemos el logo para modo oscuro
                dark_image = Image.open(logo_dark_path)
                dark_image = dark_image.resize((140, 70))  # Tamaño reducido
                
                self.logo_ctk = ctk.CTkImage(
                    light_image=dark_image,  # Usar el mismo logo como fallback
                    dark_image=dark_image,
                    size=(140, 70)  # Tamaño reducido
                )
                
                self.logo_label = ctk.CTkLabel(
                    self.title_frame,
                    image=self.logo_ctk,
                    text=""
                )
                self.logo_label.grid(row=0, column=0, padx=(0, 10))
                
            elif light_logo_exists:
                # Solo tenemos el logo para modo claro
                light_image = Image.open(logo_light_path)
                light_image = light_image.resize((140, 70))  # Tamaño reducido
                
                self.logo_ctk = ctk.CTkImage(
                    light_image=light_image,
                    dark_image=light_image,  # Usar el mismo logo como fallback
                    size=(140, 70)  # Tamaño reducido
                )
                
                self.logo_label = ctk.CTkLabel(
                    self.title_frame,
                    image=self.logo_ctk,
                    text=""
                )
                self.logo_label.grid(row=0, column=0, padx=(0, 10))
                
            else:
                # No tenemos ningún logo, mostrar texto
                self._show_text_logo()
                
                # Mostrar instrucciones
                print("\n" + "="*50)
                print("INSTRUCCIONES PARA AÑADIR LOS LOGOS:")
                print("1. Descarga los logos desde las fuentes originales:")
                print(f"   - Logo para modo oscuro (blanco): {logo_dark_url}")
                print(f"   - Logo para modo claro (azul): {logo_light_url}")
                print("2. Guárdalos en la carpeta 'resources' como:")
                print(f"   - {os.path.basename(logo_dark_path)}")
                print(f"   - {os.path.basename(logo_light_path)}")
                print(f"   (La carpeta se ha creado en: {os.path.abspath(resources_dir)})")
                print("3. Reinicia la aplicación para ver los logos")
                print("="*50 + "\n")
                
        except Exception as e:
            print(f"Error al cargar los logos: {e}")
            self._show_text_logo()
    
    def _show_text_logo(self):
        """Muestra un logo de texto como alternativa"""
        self.logo_label = ctk.CTkLabel(
            self.title_frame, 
            text="GE",  # Iniciales de Gecelca
            font=ctk.CTkFont(size=22, weight="bold"),  # Tamaño de fuente reducido
            width=50,  # Tamaño reducido
            height=50,  # Tamaño reducido
            fg_color="#004a9f",  # Color azul similar al logo
            corner_radius=25,    # Hacer un círculo
            text_color="white"
        )
        self.logo_label.grid(row=0, column=0, padx=(0, 10))
    
    def select_folder(self):
        """Seleccionar una carpeta con facturas"""
        folder_path = filedialog.askdirectory(
            title="Seleccione una carpeta"
        )
        
        if folder_path:
            self.path_var.set(folder_path)
            self.has_selection = True
            self.selected_path = folder_path
            self.process_button.configure(state="normal")
            self.status_text.set("Carpeta seleccionada. Listo para procesar.")
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
                self.process_button.configure(state="normal")
                self.status_text.set("Archivo PDF seleccionado. Listo para procesar.")
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
        self.process_button.configure(state="disabled")
        self.status_text.set("Procesando...")
        
        # Mostrar barra de progreso
        self.progress_bar.grid()
        self.progress_bar.set(0)
        self.update_idletasks()
        
        # Crear un hilo para el procesamiento para no bloquear la interfaz
        thread = threading.Thread(target=self.run_processing)
        thread.daemon = True
        thread.start()
        
        # Iniciar animación de progreso
        self.update_progress(0)
    
    def update_progress(self, value):
        """Actualiza la barra de progreso con animación"""
        if value < 1:
            self.progress_bar.set(value)
            value += 0.01
            if value > 1:
                value = 0
            self.after(50, lambda: self.update_progress(value))
    
    def run_processing(self):
        """Ejecuta el procesamiento en un hilo separado"""
        try:
            # Verificar si es archivo o carpeta
            if os.path.isfile(self.selected_path):
                # Es un archivo PDF
                self.status_text.set("Procesando archivo PDF...")
                resultado = procesar_factura(
                    self.selected_path,
                    self.output_path if self.output_path else None,
                    self.export_excel
                )
                
                if resultado:
                    self.show_success_message("El archivo ha sido procesado correctamente.")
                    self.status_text.set("Archivo procesado correctamente.")
                else:
                    self.show_error_message("No se pudo procesar el archivo.")
                    self.status_text.set("Error al procesar el archivo.")
            
            elif os.path.isdir(self.selected_path):
                # Es un directorio
                self.status_text.set("Procesando carpeta...")
                resultado = procesar_directorio(
                    self.selected_path,
                    self.output_path if self.output_path else None
                )
                
                if resultado:
                    self.show_success_message(f"Carpeta procesada correctamente.\nExcel generado en: {resultado}")
                    self.status_text.set("Carpeta procesada correctamente.")
                else:
                    self.show_error_message("No se pudo procesar la carpeta seleccionada.")
                    self.status_text.set("Error al procesar la carpeta.")
            
            else:
                self.show_error_message("La ruta seleccionada no es válida.")
                self.status_text.set("Error: ruta no válida.")
        
        except Exception as e:
            self.show_error_message(f"Ocurrió un error durante el procesamiento:\n{str(e)}")
            self.status_text.set(f"Error: {str(e)[:50]}...")
        
        # Ocultar barra de progreso
        self.after(0, lambda: self.progress_bar.grid_remove())
        
        # Rehabilitar el botón de procesar cuando termine
        self.after(0, lambda: self.process_button.configure(state="normal"))
    
    def show_success_message(self, message):
        """Muestra un mensaje de éxito"""
        self.after(0, lambda: messagebox.showinfo("Éxito", message))
    
    def show_error_message(self, message):
        """Muestra un mensaje de error"""
        self.after(0, lambda: messagebox.showerror("Error", message))
    
    def change_appearance_mode(self, new_appearance_mode):
        """Cambia el modo de apariencia (claro/oscuro)"""
        # Convertir nombres en español a los valores esperados por customtkinter
        mode_mapping = {
            "Oscuro": "dark",
            "Claro": "light"
        }
        ctk.set_appearance_mode(mode_mapping.get(new_appearance_mode, "dark"))

# Para cuando se ejecute este script directamente
if __name__ == "__main__":
    app = FacturaProcessorGUI()
    app.mainloop()