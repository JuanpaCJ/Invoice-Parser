#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script principal para el procesamiento de facturas de energía.
Este script coordina todo el proceso de extracción, procesamiento 
y exportación de datos de facturas.
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Importar módulos propios
import extractores
import procesamiento
import exportacion
import utils

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("factura_processor.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def procesar_factura(ruta_pdf, ruta_salida=None, exportar_excel=True):
    """
    Procesa una factura desde el PDF hasta la exportación.
    
    Args:
        ruta_pdf (str): Ruta al archivo PDF de la factura
        ruta_salida (str, optional): Directorio donde se guardarán los resultados
        exportar_excel (bool): Si debe exportar a Excel los resultados
        
    Returns:
        dict: Datos procesados de la factura
    """
    try:
        # Validar que el archivo exista
        if not os.path.exists(ruta_pdf):
            logger.error(f"El archivo {ruta_pdf} no existe.")
            return None
        
        # Crear directorio de salida si es necesario
        if ruta_salida:
            utils.crear_directorio_si_no_existe(ruta_salida)
        else:
            ruta_salida = os.path.dirname(os.path.abspath(ruta_pdf))
        
        # Obtener nombre base del archivo
        nombre_base = utils.obtener_nombre_archivo_sin_extension(ruta_pdf)
        
        # Paso 1: Convertir PDF a CSV
        logger.info(f"Convirtiendo PDF a CSV: {ruta_pdf}")
        ruta_csv = extractores.convertir_pdf_a_csv(ruta_pdf)
        
        # Paso 2: Extraer datos
        logger.info(f"Extrayendo datos del CSV: {ruta_csv}")
        datos_generales, datos_componentes = extractores.extraer_todos_datos_factura(ruta_csv)
        
        # Paso 3: Procesar datos
        logger.info("Procesando datos extraídos")
        processor = procesamiento.FacturaProcessor(datos_generales, datos_componentes)
        datos_procesados = processor.obtener_datos_procesados()
        
        # Validar los datos
        validacion = datos_procesados["validacion"]
        if not validacion["es_valida"]:
            logger.warning(f"La factura tiene errores de validación: {validacion['errores']}")
        
        # Paso 4: Exportar a Excel si se solicita
        if exportar_excel:
            ruta_excel = os.path.join(ruta_salida, f"{nombre_base}_analizado.xlsx")
            logger.info(f"Exportando a Excel: {ruta_excel}")
            exportador = exportacion.ExportadorExcel(datos_procesados, ruta_excel)
            ruta_excel_creada = exportador.exportar()
            logger.info(f"Archivo Excel creado: {ruta_excel_creada}")
        
        return datos_procesados
    
    except Exception as e:
        logger.error(f"Error al procesar la factura: {e}", exc_info=True)
        return None


def procesar_directorio(ruta_directorio, ruta_salida=None):
    """
    Procesa todos los archivos PDF en un directorio.
    Genera un único archivo Excel consolidado con los datos de todas las facturas.
    Guarda los archivos CSV en una subcarpeta separada.
    
    Args:
        ruta_directorio (str): Directorio con archivos PDF de facturas
        ruta_salida (str, optional): Directorio donde se guardarán los resultados
        
    Returns:
        str: Ruta del archivo Excel consolidado
    """
    # Validar que el directorio exista
    if not os.path.exists(ruta_directorio):
        logger.error(f"El directorio {ruta_directorio} no existe.")
        return None
    
    # Crear directorio de salida si es necesario
    if ruta_salida:
        utils.crear_directorio_si_no_existe(ruta_salida)
    else:
        ruta_salida = os.path.join(ruta_directorio, "resultados")
        utils.crear_directorio_si_no_existe(ruta_salida)
    
    # Crear directorio para archivos CSV
    directorio_csv = os.path.join(ruta_salida, "csv")
    utils.crear_directorio_si_no_existe(directorio_csv)
    
    # Obtener lista de archivos PDF
    archivos_pdf = [f for f in os.listdir(ruta_directorio) if f.lower().endswith('.pdf')]
    
    if not archivos_pdf:
        logger.warning(f"No se encontraron archivos PDF en {ruta_directorio}")
        return None
    
    logger.info(f"Se encontraron {len(archivos_pdf)} archivos PDF para procesar")
    
    # Usar la función de procesamiento múltiple del módulo exportación
    logger.info("Iniciando procesamiento consolidado de facturas")
    ruta_excel = exportacion.procesar_multiples_facturas(
        ruta_directorio, 
        ruta_salida=ruta_salida, 
        directorio_csv=directorio_csv
    )
    
    if ruta_excel:
        logger.info(f"Se ha creado el archivo Excel consolidado: {ruta_excel}")
    else:
        logger.error("No se pudo crear el archivo Excel consolidado")
    
    return ruta_excel


def main():
    """
    Función principal del script.
    Procesa argumentos de línea de comandos y ejecuta las operaciones correspondientes.
    """
    parser = argparse.ArgumentParser(description='Procesador de facturas de energía')
    
    # Definir argumentos
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--archivo', help='Ruta al archivo PDF de la factura')
    group.add_argument('-d', '--directorio', help='Directorio con archivos PDF de facturas')
    
    parser.add_argument('-o', '--output', help='Directorio donde se guardarán los resultados')
    parser.add_argument('--no-excel', action='store_true', help='No exportar a Excel')
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Mostrar información inicial
    logger.info("=== PROCESADOR DE FACTURAS DE ENERGÍA ===")
    logger.info(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar procesamiento según argumentos
    if args.archivo:
        logger.info(f"Procesando archivo individual: {args.archivo}")
        procesar_factura(args.archivo, args.output, not args.no_excel)
    elif args.directorio:
        logger.info(f"Procesando directorio: {args.directorio}")
        procesar_directorio(args.directorio, args.output)
    
    logger.info("Procesamiento finalizado.")


if __name__ == "__main__":
    main()