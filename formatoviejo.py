# Importamos las librerías necesarias para nuestro programa

import os  # Librería para manipular el sistema operativo
import re  # Librería para trabajar con expresiones regulares
from PyPDF2 import PdfReader  # Librería para trabajar con archivos PDF
import openpyxl  # Librería para trabajar con archivos Excel
from openpyxl import Workbook  # Módulo de openpyxl para crear libros de Excel
import pandas as pd
import psycopg2
import locale
import unidecode
from bs4 import BeautifulSoup
def quitar_tildes(texto):
    if isinstance(texto, str):
        return unidecode.unidecode(texto)
    else:
        return texto
# Ruta donde se encuentran las facturas en formato PDF
ruta_facturas = r"\\ENERGON\Publico\Gecelca\01. Comercialización\2. Automatizaciones\11. Automatización Cuentas\Facturas"
# Configurar la localización para usar el formato de comas
locale.setlocale(locale.LC_ALL, '')

# Supongamos que df es tu DataFrame
# Establecer el formato de visualización para evitar la notación científica y agregar comas como separadores de miles
pd.options.display.float_format = lambda x: locale.format_string('%d', x, grouping=True) if float(x).is_integer() else locale.format_string('%f', x, grouping=True)
# Definimos una función para extraer los campos específicos de una factura PDF
def extraer_campos_factura(pdf_file):
    # Inicializamos un diccionario para almacenar los campos extraídos
    campos_extraidos = {}
    encabezados = ['Energía\tActiva','Factor\tM',"Energía\tReactiva\tInductiva\tFacturada","Energía\tReactiva\tCapacitiva\tFacturada",'Contribución','Subtotal\tBase\tEnergía', 'Otros\tcobros','Recobros', 'Ajustes\tcargos\tregulados','Compensaciones','Amortizacion','Interés\tpor\tMora','Total\tServicio\tEnergía','Alumbrado\tPúblico','Impuesto\tAlumbrado\tPúblico','Ajuste\tIAP\tOtros\tMeses', 'Convivencia\tCiudadana', 'Tasa\tEspecial\tConvivencia\tCiudadana',
                   'Ajuste\tTasa\tConvivencia\tOtros\tMeses', 'Total\tServicio\tEnergía\t\+\tImpuestos','Ajuste\ta\tla\tdecena','Neto\ta\tpagar', ]
    # Abrimos el archivo PDF en modo de lectura binaria
    with open(pdf_file, 'rb') as file:
        # Creamos un objeto PdfReader para leer el contenido del archivo PDF
        reader = PdfReader(file)
        # Extraemos el texto de la primera página del PDF
        texto_pagina = reader.pages[0].extract_text()

        #Buscamos los campos de indentificación de la factura y la frontera.
        encabezado=['Frt', 'CFP','No.\tE']
        for encabezado in encabezado:
            globals()["match_"+ encabezado] = re.search(encabezado + r'\d*', texto_pagina)
            if globals()["match_"+ encabezado]:
                if encabezado == 'CFP':
                    campos_extraidos['Frt']=(globals()["match_"+ encabezado].group(0).replace(",", "").replace('\t', ' '))
                else:
                    campos_extraidos[encabezado]=(globals()["match_"+ encabezado].group(0).replace(",", "").replace('\t', ' '))

        encabezado=['Subtotal\tEnergía\t\+\tContribución']
        tabladatos=[]
        for encabezado in encabezado:
            globals()["match_"+ encabezado] = re.search(encabezado + r'\s?+.*?(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)+\s+(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)+\s+(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)?', texto_pagina)
            if globals()["match_"+ encabezado]:
                tabladatos.append(globals()["match_"+ encabezado].group(1).replace(",", ""))
                tabladatos.append(globals()["match_"+ encabezado].group(2).replace(",", ""))
                campos_extraidos[encabezado] = tabladatos
            tabladatos=[]
        
        # Buscamos los campos específicos de datos unico en el texto extraído usando expresiones regulares
        for encabezado in encabezados:
            globals()["match_"+ encabezado] = re.search(encabezado + r'.*?\s?.*?(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)', texto_pagina)
            if globals()["match_"+ encabezado]:
                campos_extraidos[encabezado] = globals()["match_"+ encabezado].group(1).replace(",", "")
                  
        
        encabezados=['Generación','Comercialización', 'Transmisión', 'Distribución', 'Pérdidas', 'Restricciones', 'Otros\tCargos','Subtotal\tEnergía']
        tabladatos=[]
        # Buscamos los campos específicos de datos en formato tabla en el texto extraído usando expresiones regulares
        for encabezado in encabezados:
            globals()["match_"+ encabezado] = re.search(encabezado + r'.*?\s?.*?(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)+\s+(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)+\s+(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)+\s+(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)', texto_pagina)
            if globals()["match_"+ encabezado]:
                for i in range(1,len(globals()["match_"+ encabezado].groups())+1):
                    tabladatos.append(globals()["match_"+ encabezado].group(i).replace(",", ""))
                    campos_extraidos[encabezado] = tabladatos
                tabladatos=[]

        encabezados=['Energía\tInductiva\+Capacitiva\tFacturada']
        tabladatos=[]
        # Buscamos los campos específicos de datos en formato tabla en el texto extraído usando expresiones regulares
        for encabezado in encabezados:
                globals()["match_"+ encabezado] = re.search(encabezado + r'\s*(-?\d{1,3}(?:\.\d+)?(?:,\d{3})*)\s(-?\d{1,3}(?:\.\d+)?(?:,\d{3})(?:.\s\d+)*)\s*(-?\d{1,3}(?:\.\d+)?(?:,\d{3})*)\s*(-?\d{1,3}(?:\.\d+)?(?:,\d{3})*)', texto_pagina)
                if globals()["match_"+ encabezado]:
                    for i in range(1,len(globals()["match_"+ encabezado].groups())+1):
                        tabladatos.append(globals()["match_"+ encabezado].group(i).replace(",", "").replace(" ", ""))
                        campos_extraidos[encabezado] = tabladatos
                    tabladatos=[]  

        for i in range(1,14):
            globals()["match_hoja de entrada "+ str(i)] = re.search('Hoja\tde\tentrada\t'+str(i)+r'\t+(\d+)',texto_pagina)
            if globals()["match_hoja de entrada "+ str(i)]:
                campos_extraidos['Hoja de entrada ' + str(i)]=(globals()["match_hoja de entrada "+ str(i)].group(1).replace(",", ""))  
        
        # Repetimos este proceso para los demás campos que queremos extraer
    
    # Retornamos el diccionario con los campos extraídos´
    return campos_extraidos
#r'\s+(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'

# Definimos la ruta y nombre del archivo Excel donde guardaremos los datos extraídos
excel_file = r"C:\Users\cconsuegra\OneDrive - GECELCA SA\Documentos\facturas.xlsx"


nombres_columnas = ['$/kWh', 'Mes corriente', 'Ajustes anteriores', 'Total']
df=pd.DataFrame()
# Iteramos sobre todos los archivos en la carpeta de facturas PDF
for factura in os.listdir(ruta_facturas):
    # Verificamos si el archivo es un archivo PDF
    if factura.endswith(".pdf"):
        # Construimos la ruta completa del archivo PDF
        ruta_factura_completa = os.path.join(ruta_facturas, factura)
        # Extraemos los campos de la factura y los guardamos en una variable
        campos_factura = extraer_campos_factura(ruta_factura_completa)
        # Escribimos los campos extraídos en el libro de Excel
        fila={}
        for key, value in campos_factura.items():

        # Si el valor es una lista, expandirlo en columnas adicionales
            if isinstance(value, list):
        # Añadir cada elemento de la lista como una nueva columna
                for nombre, v in zip(nombres_columnas, value):
                        fila[f"{key} {nombre}"] = v
            else:
        # Si no es una lista, simplemente añadirlo como una columna
                fila[key] = value
    # worksheet.append(fila)
        df=df._append(fila, ignore_index=True)

conexion1 = psycopg2.connect(host='' ,database="", user="", password="", port='')
cursor1=conexion1.cursor()

fechas=["'2024-10-01'","'2024-10-31'"]
query="SELECT frontera as Frt, factura_dian as Factura, v_consumo_energia_ajustado as Subtotal_Energía_Total, " \
"q_activa as energía_activa, q_inductiva_pen as energía_reactiva_inductiva_facturada, " \
"q_capacitiva_pen as energía_reactiva_capacitiva_facturada, v_gm as generación_mes_corriente, " \
"v_rm as restricciones_mes_corriente, v_cm as comercialización_mes_corriente, v_dm as distribución_mes_corriente, " \
"v_om as otros_cargos_mes_corriente, v_ppond as pérdidas_mes_corriente, v_tpond as transmisión_mes_corriente, " \
"v_reactiva_pen as energía_inductiva_capacitiva_facturada_mes_corriente, v_consumo_energia as subtotal_energía_mes_corriente,  " \
"v_gm_ajuste as generación_ajustes_anteriores, v_rm_ajuste as restricciones_ajustes_anteriores, " \
"v_cm_ajuste as comercialización_ajustes_anteriores, v_dm_ajuste as distribución_ajustes_anteriores, " \
"v_om_ajuste as otros_cargos_ajustes_anteriores,  v_ppond_ajuste as pérdidas_ajustes_anteriores, " \
"v_tpond_ajuste as transmisión_ajustes_anteriores, v_consumo_energia_ajuste as subtotal_energía_ajustes_anteriores, " \
"v_reactiva_pen_ajuste as energía_inductiva_capacitiva_facturada_ajustes_anteriores,  v_gm_ajustado as generación_total, " \
"v_rm_ajustado as restricciones_total, v_cm_ajustado as comercialización_total, v_dm_ajustado as distribución_total, " \
"v_om_ajustado as otros_cargos_total,  v_ppond_ajustado as pérdidas_total, v_tpond_ajustado as transmisión_total, " \
"v_reactiva_pen_ajustado as energía_inductiva_capacitiva_facturada_total, v_contribucion as Contribución, " \
"v_compensacion as Compensaciones, total_saldo_cartera as Amortizacion, v_iapb as Impuesto_Alumbrado_Público, " \
"v_iap_ajuste as Ajuste_IAP_Otros_Meses, v_sgcv as Tasa_Especial_Convivencia_Ciudadana, v_asgcv as Ajuste_Tasa_Convivencia_Otros_Meses, " \
"v_neto_factura as Neto_a_pagar, factor_m, v_aj_cargos_regulados as ajustes_cargos_regulados, " \
"interes_mora as interés_por_mora  FROM app_ectc_gecc.reporte_liquidacion_frts where fechafacturacion between to_date("+fechas[0]+","
"'YYYY-MM-DD') and to_date("+fechas[1]+",'YYYY-MM-DD') and tipo_factura='Factura'"


cursor1.execute(query)
nombres_columnas = [desc[0] for desc in cursor1.description]
df1 = pd.DataFrame(columns=nombres_columnas)
for fila in cursor1:
    df1 = df1._append(dict(zip(nombres_columnas, fila)), ignore_index=True)
conexion1.close()

tamaño = len(df1.columns)
dfcolumns = [re.sub(r'\t', ' ', col) for col in df.columns]
dfcolumns = [re.sub(r'\\+', '', col) for col in dfcolumns]
dfcolumns = [re.sub(r'\+', '_', col) for col in dfcolumns]
dfcolumns = [re.sub(r' ', '_', col).lower() for col in dfcolumns]
df.columns = dfcolumns
df.rename(columns={'no._e': 'factura'}, inplace=True)

columnas_convertir = df.columns.difference(['frt','factura'])
print(df)
print(df.columns)
df[columnas_convertir] = df[columnas_convertir].apply(pd.to_numeric, errors='ignore')
df[columnas_convertir] = df[columnas_convertir].astype(float)

# Guardar el DataFrame en un archivo Excel
ruta_archivo = r'C:\Users\cconsuegra\OneDrive - GECELCA SA\Documentos\HES.xlsx'
df.to_excel(ruta_archivo, index=False)

df_filtrado=df1['frt'].isin(df['frt'])
df_resumen = df.loc[:, df1[df_filtrado].columns]
merged_df = pd.merge(df_resumen, df1[df_filtrado], on='frt', suffixes=('_factura', '_BD'))
filas_iguales = merged_df.copy()

for columna in df1.columns:
    # Filtrar las filas donde las columnas correspondientes son iguales
    if columna!= 'frt' and columna!= 'factura' :
        merged_df[columna+'_diferencia']= filas_iguales[columna + '_factura'] - filas_iguales[columna + '_BD']
        if(filas_iguales[columna + '_factura'] == filas_iguales[columna + '_BD']).any():
            print(columna)
            print('No hay Diferencias')
        else:
            print(columna)
            for i in range(len(filas_iguales)):
                if filas_iguales[columna + '_factura'][i] != filas_iguales[columna + '_BD'][i]:
                    print(filas_iguales['frt'][i], 'Diferencia')
        

# Imprimimos un mensaje para indicar que el proceso ha sido completado
print("Proceso completado.")
valores_distintos_de_cero = (abs(merged_df.iloc[:, -(tamaño-3):]) > 1).any(axis=1)   

# Crear una nueva columna 'Estado' y asignar 'alerta' o 'ok' según el resultado de la verificación
merged_df['Estado'] = 'ok'
merged_df.loc[valores_distintos_de_cero, 'Estado'] = 'alerta'
columnas = list(merged_df.columns)
columnas.insert(2, columnas.pop())
ultimas_columnas = columnas[-(tamaño-3):]
columnas = columnas[:3] + ultimas_columnas + columnas[3:-(tamaño-3)]

resumen=merged_df.copy()
resumen = resumen[resumen['Estado'] == 'alerta'].iloc[:, 0:2]
print(resumen)
# Derretir el DataFrame para que 'Frt' sea la única columna de identificación
merged_df = merged_df.melt(id_vars=['frt'], var_name='Concepto', value_name='Valor')

# Extraer el sufijo de la columna 'Concepto'
merged_df['Sufijo'] = merged_df['Concepto'].str.split('_').str[-1]

# Convertir los valores a numéricos
merged_df['Valor'] = pd.to_numeric(merged_df['Valor'], errors='coerce')                                                                                                                                                     
# Extraer el nombre del concepto
merged_df['Concepto'] = merged_df['Concepto'].apply(lambda x: '_'.join(x.split('_')[:-1]))

# Eliminar filas con valores no numéricos
merged_df = merged_df.dropna(subset=['Valor'])

# Pivotear el DataFrame agrupado
merged_df = merged_df.pivot_table(index=['frt', 'Concepto'], columns='Sufijo', values='Valor', aggfunc='mean').reset_index()
for columna in merged_df.select_dtypes(include=['object']).columns:
    merged_df[columna] = merged_df[columna].apply(lambda x: unidecode.unidecode(str(x)) if isinstance(x, str) else x)
print(merged_df)

nuevos_nombres_columnas = {nombre_columna: quitar_tildes(nombre_columna) for nombre_columna in merged_df.columns}
merged_df = merged_df.rename(columns=nuevos_nombres_columnas)
tabla_html = merged_df.to_html(classes='tabla', escape=False, border=0, justify='left', index=False)
html = resumen.to_html(classes='tabla', escape=False, border=0, justify='left', index=False)
# Parsear el HTML
soup = BeautifulSoup(tabla_html, 'html.parser')

# Encontrar y eliminar los elementos <td> vacíos
for td in soup.find_all('th'):
    if not td.text.strip():
        td.extract()

# Obtener el HTML limpio
tabla_html = str(soup)
# Personalizar el estilo CSS
css_estilo = '''
<style>
/* Estilo para resaltar la fila */
/* Estilos para resaltar las filas de la primera tabla */
#tabla1 tbody tr {
  transition: background-color 0.3s ease; /* Agrega una transición suave al cambio de color */
}

#tabla1 tbody tr:hover {
  background-color: #888888; /* Cambia el color de fondo al pasar el mouse */
  cursor: pointer; /* Cambia el cursor al pasar el mouse */
}
.tabla {
    font-family: Arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
}

.tabla th {
    background-color: #115be6;
    color: #ffff;
    text-align: left;
    padding: 8px;
}

.tabla td {
    border-bottom: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}

.alerta {
    background-color: #df4949 !important;
}
.resaltar-celda {
    background-color: #df4949 !important;
}
/* Estilo para el input */
input[type="text"] {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-right: 10px;
}

/* Estilo para los botones */
button {
    padding: 8px 16px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background-color: #0056b3;
}

/* Estilo para el select */
select {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    width: 200px;
    height: auto;
    overflow-y: auto;
}

/* Estilo para las opciones del select */
select option {
    padding: 8px;
}

/* Estilo para el contenedor */
div {
    margin-bottom: 20px;
}
</style>
<div><input type="text" id="filtroFila" placeholder="Filtrar frontera">
<button id="limpiarFiltroFila">Limpiar filtro</button>
<input type="text" id="filtroFactura" placeholder="Filtrar factura">
<button id="limpiarFiltroFactura">Limpiar filtro</button>
<input type="text" id="filtroEstado" placeholder="Filtrar Estado">
<button id="limpiarFiltroEstado">Limpiar filtro</button></div>
<br>
'''

script_js = '''
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script>
  $(document).ready(function() {
      // Iterar sobre todas las celdas de la tabla
      $("table.dataframe.tabla tbody tr td").each(function() {
          // Obtener el ndice de la celda dentro de la fila
          var cellIndex = $(this).index();
          // Obtener el texto del encabezado de la columna correspondiente
          var columnText = $("table.dataframe.tabla thead tr th").eq(cellIndex).text();
          // Verificar si el encabezado contiene la palabra "diferencia"
          if (columnText.toLowerCase().includes('diferencia')) {
              // Obtener el tipo de dato en la columna (nmero o texto)
              var columnDataType = 'texto';
              var cellText = $(this).text();
              // Verificar si el texto puede ser convertido a un nmero
              if (!isNaN(parseFloat(cellText.replace(/\./g, '').replace(',', '.')))) {
                  columnDataType = 'nmero';
                  // Convertir el texto a nmero
                  var cellValue = parseFloat(cellText.replace(/\./g, '').replace(',', '.'));
                  // Verificar si el valor absoluto es mayor a 1 y diferente de 0
                  if (Math.abs(cellValue) > 1 ) {
                      // Resaltar la celda
                      $(this).addClass("resaltar-celda");
                  }
              }
              // Mostrar informacion de la columna y celda en la consola
              console.log("Columna:", columnText, "Tipo de dato:", columnDataType, "Valor de la celda:", cellText);
          }
      });
  });
  </script>




<script>
$(document).ready(function() {
    // Filtrar frontera
    $('#filtroFila2').on('input', function() {
      var filtro = $(this).val().toLowerCase();
      $('table.dataframe.tabla2 tbody tr:visible').each(function() {
        var frtValue = $(this).find('td:eq(0)').text().toLowerCase();
        if (!frtValue.includes(filtro)) {
          $(this).hide();
        }
      });
    });

    // Filtrar factura
    $('#filtroFactura2').on('input', function() {
      var filtro = $(this).val().toLowerCase();
      $('table.dataframe.tabla2 tbody tr:visible').each(function() {
        var facturaValue = $(this).find('td:eq(1)').text().toLowerCase();
        if (!facturaValue.includes(filtro)) {
          $(this).hide();
        }
      });
    });

    // Filtrar estado
    $('#filtroEstado2').on('input', function() {
      var filtro = $(this).val().toLowerCase();
      $('table.dataframe.tabla2 tbody tr:visible').each(function() {
        var estadoValue = $(this).find('td:eq(2)').text().toLowerCase();
        if (!estadoValue.includes(filtro)) {
          $(this).hide();
        }
      });
    });

    // Limpiar filtro de frontera
    $('#limpiarFiltroFila2').click(function() {
      $('#filtroFila2').val('');
      $('table.dataframe.tabla2 tbody tr').show();
    });

    // Limpiar filtro de factura
    $('#limpiarFiltroFactura2').click(function() {
      $('#filtroFactura2').val('');
      $('table.dataframe.tabla2 tbody tr').show();
    });

    // Limpiar filtro de estado
    $('#limpiarFiltroEstado2').click(function() {
      $('#filtroEstado2').val('');
      $('table.dataframe.tabla2 tbody tr').show();
    });
  });

document.addEventListener("DOMContentLoaded", function() {
  // Obtener la primera tabla y sus filas
  var tabla1 = document.getElementById("tabla1");
  var filasTabla1 = tabla1.getElementsByTagName("tr");

  // Obtener la segunda tabla y sus filas
  var tabla2 = document.getElementById("tabla2");
  var filasTabla2 = tabla2.getElementsByTagName("tr");

  // Agregar un evento de clic a cada fila de la primera tabla
  for (var i = 0; i < filasTabla1.length; i++) {
    filasTabla1[i].addEventListener("click", function() {
      // Obtener el valor de Frt de la fila clicada en la primera tabla
      var frtSeleccionada = this.cells[0].innerText;

      // Filtrar la segunda tabla para mostrar solo las filas con el mismo valor de Frt
      for (var j = 1; j < filasTabla2.length; j++) {
        var frtTabla2 = filasTabla2[j].cells[0].innerText;
        if (frtTabla2 === frtSeleccionada) {
          filasTabla2[j].style.display = "";
        } else {
          filasTabla2[j].style.display = "none";
        }
      }
    });
  }
});

</script>
'''
# Reemplazar 'alerta' con la clase CSS 'alerta' para cambiar el color de fondo
tabla_html  = tabla_html.replace('<td>alerta</td>', '<td class="alerta">alerta</td>')
tabla_html  = tabla_html.replace('<th>Sufijo</th>', '')
html = html.replace('<table class="dataframe tabla">','<table class="dataframe tabla" id="tabla1">')
tabla_html = tabla_html.replace('<table class="dataframe tabla">','<table class="dataframe tabla" id="tabla2">')
html = html.replace('<thead>','<thead><th colspan="2" class="dataframe tabla" style="text-align: center;">Fronteras con diferencias</th>')
html = html + '<br>'
# Agregar el estilo CSS al inicio del documento HTML
tabla_html = css_estilo + html + tabla_html + script_js
# Guardar la tabla HTML en un archivo
with open('tablacopy.html', 'w') as f:
    f.write(tabla_html)

# Guardar el CSV
merged_df.to_csv('mi_dataframe.csv', index=False, sep='\t')

# Guardar el archivo Excel en la ruta especificada
output_path = r'C:\Users\cconsuegra\OneDrive - GECELCA SA\Documentos\alertaspre.xlsx'
merged_df.to_excel(output_path, index=False)