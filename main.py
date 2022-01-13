# Libreria para el manejo de Dataframes (Datos estructurados)
import pandas as pd
from drilling_functions import *
from os import remove





#Archivo con los viajes que se realizaron en el pozo de perforación
archivo = 'D:\Independence\Sistema\Desktop\Desarrollo Perforación\Pruebas All\Drilling datos_ingreso_Viajes.xlsx'
df_export=pd.DataFrame()
ilt_export=list()
df = pd.read_excel(archivo, sheet_name='Marco_tiempo')   

torre=""
pozo=""


for row in df.itertuples():
    
    torre = str(row.deviceId)
    pozo = str(row.pozo).upper()
    actividad = str(row.actividad).upper()     
    fecha_inicio = row.inicio
    fecha_fin = row.fin
    seccion=row.seccion
    estado=row.estado
    
    datos = viaje_tuberia(torre, pozo, actividad, fecha_inicio,
                              fecha_fin,seccion,estado)
    
    df_export=pd.concat([df_export, datos], sort='False', ignore_index='True')
    
name_excel='tuberia_ilts_ExporData.xlsx'


df_dataExport=returnDF()
writer = pd.ExcelWriter(name_excel, engine='xlsxwriter')
df_export.to_excel(writer,sheet_name='Tiempos_Viajes', index = False)

df_dataExport.to_excel(writer,sheet_name='Data', index = False)
writer.save()
send_email(name_excel,torre,pozo)
remove(name_excel)
        
print("Hola")
    


        
