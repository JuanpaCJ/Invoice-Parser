"""
Módulo para extracción de datos de facturas en formato PDF y CSV.
Este módulo contiene funciones para convertir archivos PDF a CSV y
extraer información estructurada de las facturas.
"""

import os
import re
import csv
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser

# Patrones regex centralizados para extracción de datos
PATRONES_CONCEPTO = {
    'subtotal_base_energia': [r'Subtotal base energía.*?"([\d,]+)"', r'Subtotal\tbase\tenergía.*?"([\d,]+)"'],
    'contribucion': [r'Contribución.*?"([\d,]+)"'],
    'contribucion_otros_meses': [r'Contribución de otros meses.*?([\d,]+)', r'Contribución\tde\totros\tmeses.*?([\d,]+)'],
    'subtotal_energia_contribucion_kwh': [r'\$\/kWh,\$\s*Subtotal\s*energia\s*\+\s*contribución,\s*([\d.,]+)', r'\$\/kWh,\$\s*Subtotal\tenerg[ií]a\t\+\tcontribución,\s*([\d.,]+)'],
    'subtotal_energia_contribucion_pesos': [r'\$\/kWh,\$\s*Subtotal\s*energia\s*\+\s*contribución,\s*[\d.,]+,\s*"([\d,]+)"', r'\$\/kWh,\$\s*Subtotal\tenerg[ií]a\t\+\tcontribución,\s*[\d.,]+,\s*"([\d,]+)"'],
    'otros_cobros': [r'Otros cobros.*?"([\d,]+)"', r'Otros\tcobros.*?"([\d,]+)"'],
    'sobretasa': [r'Sobretasa.*?([\d,]+)'],
    'ajustes_cargos_regulados': [r'Ajustes cargos regulados.*?"([\d,]+)"', r'Ajustes\tcargos\tregulados.*?"([\d,]+)"'],
    'compensaciones': [r'Compensaciones.*?([\d,]+)'],
    'saldo_cartera': [r'Saldo cartera.*?([\d,]+)', r'Saldo\tcartera.*?([\d,]+)'],
    'interes_mora': [r'Interés por Mora.*?([\d,]+)', r'Interés\tpor\tMora.*?([\d,]+)'],
    'alumbrado_publico': [r'Alumbrado público.*?"([\d,]+)"', r'Alumbrado\tpúblico.*?"([\d,]+)"'],
    'impuesto_alumbrado_publico': [r'Impuesto alumbrado público.*?"([\d,]+)"', r'Impuesto\talumbrado\tpúblico.*?"([\d,]+)"'],
    'ajuste_iap_otros_meses': [r'Ajuste IAP otros meses.*?([\d,]+)', r'Ajuste\tIAP\totros\tmeses.*?([\d,]+)'],
    'convivencia_ciudadana': [r'Convivencia ciudadana.*?"([\d,]+)"', r'Convivencia\tciudadana.*?"([\d,]+)"'],
    'tasa_especial_convivencia': [r'Tasa especial convivencia ciudadana.*?"([\d,]+)"', r'Tasa\tespecial\tconvivencia\tciudadana.*?"([\d,]+)"'],
    'ajuste_tasa_convivencia': [r'Ajuste tasa convivencia otros meses.*?([\d,]+)', r'Ajuste\ttasa\tconvivencia\totros\tmeses.*?([\d,]+)'],
    'total_servicio_energia_impuestos': [r'Total servicio energía \+ impuestos.*?"([\d,]+)"', r'Total\tservicio\tenergía\t\+\timpuestos.*?"([\d,]+)"', r'Total\tservicio\tenergía\t\\\+\timpuestos.*?"([\d,]+)"'],
    'ajuste_decena': [r'Ajuste a la decena.*?([\d,]+)', r'Ajuste\ta\tla\tdecena.*?([\d,]+)'],
    'neto_pagar': [r'Neto a pagar.*?"([\d,]+)"', r'Neto\ta\tpagar.*?"([\d,]+)"'],
    'energia_reactiva_inductiva': [r'Energía\s*reactiva\s*inductiva,\s*"([\d,]+)"', r'Energía\treactiva\tinductiva,\s*"([\d,]+)"'],
    'energia_reactiva_capacitiva': [r'Energía\s*reactiva\s*capacitiva,\s*([\d,]+)', r'Energía\treactiva\tcapacitiva,\s*([\d,]+)'],
    'total_energia_reactiva': [r'Total\s*energía\s*reactiva,\s*"([\d,]+)"', r'Total\tenergía\treactiva,\s*"([\d,]+)"']
}

# Patrones para componentes de energía 
COMPONENTES_ENERGIA = [
    {
        "name": "Generación",
        "pattern": r'1\.\s+Generación,"([\d,]+)",([\d\.]+),"([\d,]+)","([\d,]+)","([\d,]+)"'
    },
    {
        "name": "Comercialización",
        "pattern": r'2\.\s+Comercialización,([\d\.]+),"([\d,]+)","([-\d,]+)","([\d,]+)"'
    },
    {
        "name": "Transmisión",
        "pattern": r'3\.\s+Transmisión,([\d\.]+),"([\d,]+)","([-\d,]+)","([\d,]+)"'
    },
    {
        "name": "Distribución",
        "pattern": r'4\.\s+Distribución,([\d\.]+),"([\d,]+)","([-\d,]+)","([\d,]+)"'
    },
    {
        "name": "Pérdidas",
        "pattern": r'5\.\s+Perdidas\s+\(\*\),([\d\.]+),"([\d,]+)","([-\d,]+)","([\d,]+)"'
    },
    {
        "name": "Restricciones",
        "pattern": r'6\.\s+Restricciones,([-\d\.]+),"([-\d,]+)","([-\d,]+)","([-\d,]+)"'
    },
    {
        "name": "Otros cargos",
        "pattern": r'7\.\s+Otros\s+cargos,([\d\.]+),"([\d,]+)","([-\d,]+)","([\d,]+)"'
    },
    {
        "name": "Energía inductiva + capacitiva",
        "pattern": r'8\.\s+Energía\s+inductiva\s+\+\s+capacitiva\s+facturada,"([\d,]+)",([\d\.]+),"([\d,]+)",(\d+),"([\d,]+)"'
    }
]


def convertir_pdf_a_csv(ruta_pdf, ruta_salida=None):
    """
    Convierte un archivo PDF a formato CSV, preservando la estructura de columnas.
    
    Args:
        ruta_pdf (str): Ruta al archivo PDF
        ruta_salida (str, optional): Ruta donde se guardará el archivo CSV.
                                     Si es None, se usará el nombre del PDF con .csv.
    
    Returns:
        str: Ruta del archivo CSV creado
    """
    if ruta_salida is None:
        nombre_base = os.path.splitext(os.path.basename(ruta_pdf))[0]
        directorio = os.path.dirname(os.path.abspath(ruta_pdf))
        ruta_salida = os.path.join(directorio, f"{nombre_base}.csv")
    
    # Extraer datos organizados por filas y columnas
    datos_estructurados = extraer_datos_estructurados(ruta_pdf)
    
    # Guardar en archivo CSV
    with open(ruta_salida, 'w', encoding='utf-8', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        
        # Escribir datos
        for pagina, filas in datos_estructurados.items():
            # Escribir encabezado de página
            writer.writerow([f"PÁGINA {pagina}"])
            writer.writerow([])  # Línea vacía para separar
            
            # Escribir filas de datos
            for fila in filas:
                writer.writerow(fila)
            
            # Separador entre páginas
            writer.writerow([])
            writer.writerow([])
    
    return ruta_salida


def procesar_texto(texto):
    """
    Procesa el texto para separar números y valores que podrían estar juntos.
    
    Args:
        texto (str): Texto a procesar
        
    Returns:
        list: Lista de elementos separados
    """
    # Patrones para buscar en el texto
    patrones = [
        # Patrón para separar números con comas seguidos de otros números
        r'(\d[\d,.]+)\s+(\d[\d,.]+)',
        # Patrón para separar texto de números
        r'([a-zA-Z]+[a-zA-Z\s]+)(\d[\d,.]+)'
    ]
    
    elementos = [texto]
    
    # Aplicar cada patrón
    for patron in patrones:
        nuevos_elementos = []
        for elem in elementos:
            # Verificar si el patrón coincide
            coincidencia = re.search(patron, elem)
            if coincidencia:
                # Separar el elemento según el patrón
                partes = re.split(patron, elem)
                # Filtrar elementos vacíos y agregar a la lista
                nuevos_elementos.extend([p.strip() for p in partes if p and p.strip()])
            else:
                nuevos_elementos.append(elem)
        elementos = nuevos_elementos
    
    # Eliminar duplicados y elementos vacíos
    return [e for e in elementos if e and e.strip()]


def extraer_datos_estructurados(ruta_pdf):
    """
    Extrae datos del PDF y los organiza en una estructura adecuada para CSV
    
    Args:
        ruta_pdf (str): Ruta al archivo PDF
    
    Returns:
        dict: Diccionario con páginas como claves y listas de filas como valores
    """
    datos_por_pagina = {}
    
    with open(ruta_pdf, 'rb') as f:
        parser = PDFParser(f)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        
        device = PDFPageAggregator(rsrcmgr, laparams=LAParams(
            line_margin=0.5,
            word_margin=0.1,
            boxes_flow=-1.0,  # Valor negativo para favorecer columnas
            detect_vertical=True
        ))
        
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        
        page_num = 0
        for page in PDFPage.create_pages(doc):
            page_num += 1
            
            interpreter.process_page(page)
            layout = device.get_result()
            
            # Organizar elementos por posición Y para preservar filas
            elementos_por_y = {}
            
            for element in layout:
                if hasattr(element, 'get_text'):
                    # Redondeamos para agrupar líneas cercanas (en grupos de 10 unidades)
                    y = int(element.y0 / 10) * 10
                    if y not in elementos_por_y:
                        elementos_por_y[y] = []
                    elementos_por_y[y].append(element)
            
            # Lista de filas para esta página
            filas_pagina = []
            
            # Ordenar por y descendente (de arriba a abajo)
            for y in sorted(elementos_por_y.keys(), reverse=True):
                # Ordenar elementos de izquierda a derecha en cada fila
                elementos = sorted(elementos_por_y[y], key=lambda e: e.x0)
                
                # Lista para almacenar todos los elementos procesados de la fila
                elementos_procesados = []
                
                for element in elementos:
                    texto = element.get_text().strip()
                    if texto:
                        # Procesar el texto para separar posibles números juntos
                        sub_elementos = procesar_texto(texto)
                        elementos_procesados.extend(sub_elementos)
                
                # Añadir fila si tiene elementos
                if elementos_procesados:
                    filas_pagina.append(elementos_procesados)
            
            # Guardar filas de esta página
            datos_por_pagina[page_num] = filas_pagina
    
    return datos_por_pagina


def analizar_estructura_columnas(datos_por_pagina):
    """
    Analiza la estructura de las columnas para intentar normalizar el número de columnas.
    Útil para determinar un encabezado si es necesario.
    
    Args:
        datos_por_pagina (dict): Datos estructurados por página
        
    Returns:
        int: Número máximo de columnas encontrado
    """
    max_columnas = 0
    
    for pagina, filas in datos_por_pagina.items():
        for fila in filas:
            max_columnas = max(max_columnas, len(fila))
    
    return max_columnas


def leer_archivo(file_path):
    """
    Lee el contenido de un archivo con manejo de codificaciones.
    
    Args:
        file_path (str): Ruta al archivo
        
    Returns:
        str: Contenido del archivo
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        # Try another encoding if utf-8 fails
        with open(file_path, 'r', encoding='latin-1') as file:
            content = file.read()
    return content


def extraer_datos_factura(file_path):
    """
    Extrae los datos generales de la factura desde un archivo CSV.
    
    Args:
        file_path (str): Ruta al archivo CSV de la factura
        
    Returns:
        dict: Diccionario con los datos extraídos de la factura
    """
    content = leer_archivo(file_path)
    
    # Extraer información principal
    fecha_vencimiento_match = re.search(r'Fecha\s+vencimiento:\s+(\d{4}-\d{2}-\d{2})', content)
    fecha_vencimiento = fecha_vencimiento_match.group(1) if fecha_vencimiento_match else "No encontrado"
    
    periodo_facturacion_match = re.search(r'Período\s+Facturación:\s+(\d{4}-\d{2}-\d{2}).*?(\d{4}-\d{2}-\d{2})', content)
    if periodo_facturacion_match:
        periodo_facturacion = f"{periodo_facturacion_match.group(1)} a {periodo_facturacion_match.group(2)}"
    else:
        # Try alternative format
        alt_match = re.search(r'Período\s+Facturación:\s+(\d{4}-\d{2}-\d{2})', content)
        periodo_facturacion = alt_match.group(1) if alt_match else "No encontrado"
    
    factor_m_match = re.search(r'Factor\s+M:\s+(\d+)', content)
    factor_m = factor_m_match.group(1) if factor_m_match else "No encontrado"
    
    codigo_sic_match = re.search(r'Código\s+SIC:.*?Frt.*?(\d+)', content)
    if codigo_sic_match:
        codigo_sic = f"Frt{codigo_sic_match.group(1)}"
    else:
        codigo_sic = "No encontrado"
    
    # Initialize results dictionary with the main variables
    results = {
        "fecha_vencimiento": fecha_vencimiento,
        "periodo_facturacion": periodo_facturacion,
        "factor_m": factor_m,
        "codigo_sic": codigo_sic,
    }
    
    # Extract all the financial variables
    for var_name, patterns in PATRONES_CONCEPTO.items():
        value = "No encontrado"
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                # Limpiar el valor capturado
                captured_value = match.group(1)
                # Eliminar comas al inicio del valor
                if captured_value.startswith(','):
                    captured_value = captured_value[1:]
                value = captured_value
                break
        results[var_name] = value
    
    return results


def extraer_tabla_componentes(file_path):
    """
    Extrae los datos de la tabla de componentes de energía.
    
    Args:
        file_path (str): Ruta al archivo CSV de la factura
        
    Returns:
        list: Lista de diccionarios con los datos de los componentes
    """
    content = leer_archivo(file_path)
    
    # Define the pattern to find the energy components table
    table_pattern = r'Componentes,kWh\s+-\s+kVArh,\$/kWh.*?Subtotal\s+energía,.*?"([\d,]+)"'
    table_match = re.search(table_pattern, content, re.DOTALL)
    
    concepto_data = []
    
    if table_match:
        table_content = table_match.group(0)
        
        # Extract data for each component
        for component in COMPONENTES_ENERGIA:
            match = re.search(component["pattern"], table_content)
            
            if match:
                concepto = {}
                concepto["concepto"] = component["name"]
                
                if component["name"] == "Generación" or component["name"] == "Energía inductiva + capacitiva":
                    concepto["kwh_kvarh"] = match.group(1).replace(',', '') if match.group(1) else "0"
                    concepto["precio_kwh"] = match.group(2).replace(',', '') if match.group(2) else "0"
                    concepto["mes_corriente"] = match.group(3).replace(',', '') if match.group(3) else "0"
                    concepto["mes_anteriores"] = match.group(4).replace(',', '') if match.group(4) else "0"
                    concepto["total"] = match.group(5).replace(',', '') if match.group(5) else "0"
                else:
                    concepto["kwh_kvarh"] = "N/A"
                    concepto["precio_kwh"] = match.group(1).replace(',', '') if match.group(1) else "0"
                    concepto["mes_corriente"] = match.group(2).replace(',', '') if match.group(2) else "0"
                    concepto["mes_anteriores"] = match.group(3).replace(',', '') if match.group(3) else "0"
                    concepto["total"] = match.group(4).replace(',', '') if match.group(4) else "0"
                
                # Limpiar valores negativos, mantener el signo
                if concepto["mes_anteriores"] != "N/A" and concepto["mes_anteriores"].startswith('-'):
                    concepto["mes_anteriores"] = "-" + concepto["mes_anteriores"].replace('-', '')
                if concepto["total"] != "N/A" and concepto["total"].startswith('-'):
                    concepto["total"] = "-" + concepto["total"].replace('-', '')
                    
                concepto_data.append(concepto)
    
    # Si no se encontró la tabla usando el primer método, intentar con el método alternativo
    if not concepto_data:
        # Patrones para extraer diferentes conceptos (Generación, Comercialización, etc.)
        patrones_concepto = [
            r'Generación:[\s\S]*?kWh-kVArh:\s*([\d,]+)[\s\S]*?\$/kWh:\s*([\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([\d,-]+)"?[\s\S]*?Total \$:\s*"?([\d,]+)"?',
            r'Comercialización:[\s\S]*?\$/kWh:\s*([\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([\d,-]+)"?[\s\S]*?Total \$:\s*"?([\d,]+)"?',
            r'Transmisión:[\s\S]*?\$/kWh:\s*([\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([\d,-]+)"?[\s\S]*?Total \$:\s*"?([\d,]+)"?',
            r'Distribución:[\s\S]*?\$/kWh:\s*([\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([\d,-]+)"?[\s\S]*?Total \$:\s*"?([\d,]+)"?',
            r'Pérdidas:[\s\S]*?\$/kWh:\s*([\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([\d,-]+)"?[\s\S]*?Total \$:\s*"?([\d,]+)"?',
            r'Restricciones:[\s\S]*?\$/kWh:\s*([\d.,-]+)[\s\S]*?Mes corriente \$:\s*"?([\d,-]+)"?[\s\S]*?Mes anteriores \$:\s*"?([\d,-]+)"?[\s\S]*?Total \$:\s*"?([\d,-]+)"?',
            r'Otros cargos:[\s\S]*?\$/kWh:\s*([\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([\d,-]+)"?[\s\S]*?Total \$:\s*"?([\d,]+)"?',
            r'Energía inductiva \+ capacitiva:[\s\S]*?kWh-kVArh:\s*([\d,]+)[\s\S]*?\$/kWh:\s*([\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([\d,]+)"?[\s\S]*?Total \$:\s*"?([\d,]+)"?'
        ]
        
        nombres_conceptos = [
            'Generación', 'Comercialización', 'Transmisión', 'Distribución', 
            'Pérdidas', 'Restricciones', 'Otros cargos', 'Energía inductiva + capacitiva'
        ]
        
        for i, pattern in enumerate(patrones_concepto):
            match = re.search(pattern, content)
            if match:
                concepto = {}
                concepto['concepto'] = nombres_conceptos[i]
                
                # Para la Generación y Energía inductiva + capacitiva que tienen kWh-kVArh
                if i == 0 or i == 7:
                    concepto['kwh_kvarh'] = match.group(1).replace(',', '') if match.group(1) else "0"
                    concepto['precio_kwh'] = match.group(2).replace(',', '') if match.group(2) else "0"
                    concepto['mes_corriente'] = match.group(3).replace(',', '') if match.group(3) else "0"
                    concepto['mes_anteriores'] = match.group(4).replace(',', '') if match.group(4) else "0"
                    concepto['total'] = match.group(5).replace(',', '') if match.group(5) else "0"
                else:
                    concepto['kwh_kvarh'] = "N/A"
                    concepto['precio_kwh'] = match.group(1).replace(',', '') if match.group(1) else "0"
                    concepto['mes_corriente'] = match.group(2).replace(',', '') if match.group(2) else "0"
                    concepto['mes_anteriores'] = match.group(3).replace(',', '') if match.group(3) else "0"
                    concepto['total'] = match.group(4).replace(',', '') if match.group(4) else "0"
                
                # Limpiar cualquier coma al inicio
                for key in concepto:
                    if isinstance(concepto[key], str) and concepto[key].startswith(','):
                        concepto[key] = concepto[key][1:]
                        
                concepto_data.append(concepto)
    
    return concepto_data


def extraer_todos_datos_factura(file_path):
    """
    Extrae todos los datos de la factura, combinando datos generales y tabla de componentes.
    
    Args:
        file_path (str): Ruta al archivo CSV de la factura
        
    Returns:
        tuple: Tupla con (datos_generales, datos_componentes)
    """
    datos_generales = extraer_datos_factura(file_path)
    datos_componentes = extraer_tabla_componentes(file_path)
    
    return datos_generales, datos_componentes