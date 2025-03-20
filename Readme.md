# Procesador de Facturas de Energía

Este proyecto proporciona un sistema para extraer, procesar y analizar datos de facturas de energía en formato PDF. La herramienta convierte PDFs a formato CSV, extrae información relevante, procesa los datos y los exporta a archivos Excel para su análisis.

## Características

- Extracción automatizada de datos de facturas de energía en PDF
- Conversión de PDF a CSV manteniendo la estructura
- Identificación de campos clave como fechas, montos y componentes de energía
- Procesamiento y limpieza de datos
- Validación de consistencia de datos
- Exportación a Excel con múltiples hojas (facturas, componentes, metadatos)
- Procesamiento por lotes de múltiples facturas
- Registro detallado de operaciones (logging)

## Requisitos

Para utilizar esta herramienta, necesitas:

- Python 3.6 o superior
- Las siguientes bibliotecas:
  - pdfminer.six (para extraer datos de PDFs)
  - openpyxl (para crear archivos Excel)



1. Instala las dependencias:

Desde una terminal ubicada en el directorio correcto

pip install pdfminer.six openpyxl

Alternativamente, si prefieres usar un entorno virtual:

Desde una terminal ubicada en el directorio correcto
### Crear entorno virtual
python -m venv venv

### Activar entorno virtual
### En Windows:
venv\Scripts\activate
### En macOS/Linux:
source venv/bin/activate

### Instalar dependencias
pip install pdfminer.six openpyxl


## Estructura del proyecto

El proyecto está organizado en los siguientes módulos:

- `main.py`: Punto de entrada del programa, maneja argumentos de línea de comandos
- `extractores.py`: Funciones para extraer datos de PDFs y CSVs
- `procesamiento.py`: Clases y funciones para procesar y transformar datos
- `exportacion.py`: Clases para exportar datos a Excel
- `utils.py`: Funciones auxiliares generales

## Uso

### Línea de comandos

El script principal (`main.py`) acepta varios argumentos:


- usage: main.py [-h] (-a ARCHIVO | -d DIRECTORIO) [-o OUTPUT] [--no-excel]

Procesador de facturas de energía

optional arguments:
  -h, --help            Muestra este mensaje de ayuda
  -a ARCHIVO, --archivo ARCHIVO
                        Ruta al archivo PDF de la factura
  -d DIRECTORIO, --directorio DIRECTORIO
                        Directorio con archivos PDF de facturas
  -o OUTPUT, --output OUTPUT
                        Directorio donde se guardarán los resultados
  --no-excel            No exportar a Excel


### Ejemplos de uso

Instalar dependencias usando "pip install -r requirements.txt"

Basta con ejecutar el archivo gui.py utilizando "python gui.py" desde consola una vez instaladas las dependencias

#### Procesar un archivo individual

Desde una terminal ubicada en el directorio correcto escribir: 

python main.py -a facturas/tuarchivodefactura.pdf


Esto procesará el archivo PDF especificado y generará un archivo Excel con los datos extraídos en el mismo directorio que el PDF.

#### Procesar un archivo y guardar resultados en directorio específico

Desde una terminal ubicada en el directorio correcto escribir:

python main.py -a facturas/tuarchivodefactura.pdf -o resultados


#### Procesar todos los PDFs en una carpeta:

Desde una terminal ubicada en el directorio correcto escribir: 

python main.py -d ./carpetaconpdfs


Esto procesará todos los archivos PDF en el directorio "carpetaconpdfs"(cambiar al nombre correcto de la carpeta) y generará archivos Excel correspondientes.


### Resultados

Por cada factura procesada, se generan los siguientes resultados:

1. **Archivo CSV**: Contiene el texto extraído del PDF, manteniendo la estructura.
2. **Archivo Excel**: Con tres hojas:
   - **Facturas**: Datos generales de la factura (fecha, montos, etc.)
   - **Conceptos**: Componentes de energía (generación, transmisión, etc.)
   - **Metadatos**: Descripción de los campos y su significado

Además, se genera un archivo de registro (`factura_processor.log`) que contiene información detallada sobre el procesamiento.

## Estructura de datos de salida

### Hoja "Facturas"

Contiene información general de la factura, incluyendo:

- ID_Factura
- Nombre_Archivo: Nombre del archivo PDF original
- Fecha vencimiento
- Período Facturación
- Factor M
- Código SIC
- subtotal_base_energia
- contribucion
- contribucion_otros_meses
- subtotal_energia_contribucion_kwh
- subtotal_energia_contribucion_pesos
- otros_cobros
- sobretasa
- ajustes_cargos_regulados
- compensaciones
- saldo_cartera
- interes_mora
- alumbrado_publico
- impuesto_alumbrado_publico
- ajuste_iap_otros_meses
- convivencia_ciudadana
- tasa_especial_convivencia
- ajuste_tasa_convivencia
- total_servicio_energia_impuestos
- ajuste_decena
- neto_pagar
- energia_reactiva_inductiva
- energia_reactiva_capacitiva
- total_energia_reactiva

### Hoja "Conceptos"

Contiene los diferentes componentes del cobro de energía:

- ID_Factura: Identificador que relaciona con la factura
- Concepto: Tipo de componente (Generación, Transmisión, etc.)
- KWh_KVArh: Cantidad de energía
- Precio_KWh: Precio unitario
- Mes_Corriente: Valor del mes actual
- Mes_Anteriores: Valor de meses anteriores
- Total: Valor total del componente

### Hoja "Metadatos"

Contiene descripciones detalladas de todos los campos, incluyendo:

- Campo: Nombre del campo
- Descripción: Explicación del campo
- Tipo de Dato: Integer, Decimal, String, etc.
- Unidad: Pesos$COP, kWh, etc.
- Observaciones: Notas adicionales

## Personalización

Si necesitas ajustar patrones específicos para la extracción de datos, puedes modificar las constantes en `extractores.py`:

- `PATRONES_CONCEPTO`: Patrones para extraer campos generales
- `COMPONENTES_ENERGIA`: Patrones para extraer componentes de energía

## Solución de problemas

### PDF no se procesa correctamente

Si un PDF no se procesa correctamente, verifica:

1. Que el PDF no esté protegido o encriptado
2. Que el texto sea seleccionable (no una imagen)
3. Que el formato sea similar al de facturas ya procesadas

Los errores se registran en el archivo `factura_processor.log`.

### Valores incorrectos o no encontrados

Si algunos valores aparecen como "No encontrado" o son incorrectos:

1. Verifica que los patrones en `extractores.py` coincidan con el formato de tu factura
2. Ajusta los patrones regex si es necesario
3. Verifica el archivo CSV generado para confirmar que los datos fueron extraídos correctamente del PDF

## Extendiendo el proyecto

Para añadir soporte para otros formatos de factura:

1. Modifica los patrones regex en `extractores.py`
2. Ajusta la clase `FacturaProcessor` en `procesamiento.py` si es necesario
3. Modifica `ExportadorExcel` en `exportacion.py` si necesitas cambiar el formato de salida



## Contacto

Para preguntas o soporte, contacta a Juan Pablo Céspedes de Transformación Digital.
jcespedes@gecelca.com.co
+57 301 529 4975