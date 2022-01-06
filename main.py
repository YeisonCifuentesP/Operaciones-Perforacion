# Libreria para el manejo de Dataframes (Datos estructurados)
import pandas as pd
from drilling_functions import *
import pandas as pd
from os import remove





#Archivo con los viajes que se realizaron en el pozo de perforación
archivo = 'D:\Independence\Sistema\Desktop\SKAN_HAWK\DOCUMENTACION_SKAN\SCRIPTS_PYTHON\SCRIPT_PERFORACION\Datos_desarrollo_perforacion.xlsx'
df_export=pd.DataFrame()
ilt_export=list()
df = pd.read_excel(archivo, sheet_name='Marco_tiempo')   

torre=""
pozo=""


for row in df.itertuples():
    
    torre = str(row.deviceId)
    pozo = str(row.pozo).upper()
    actividad = str(row.Actividades).upper()     
    fecha_inicio = row.inicio
    fecha_fin = row.fin
    
    datos,ilt = viaje_tuberia(torre, pozo, actividad, fecha_inicio,
                              fecha_fin)
    ilt_export.append([torre,pozo,actividad,ilt])
    df_export=pd.concat([df_export, datos], sort='False', ignore_index='True')
    
name_excel='tuberia_ilts.xlsx'
df_ilts=pd.DataFrame(ilt_export,
                  columns=['torre','pozo', 'actividad', 'ilt'])
writer = pd.ExcelWriter(name_excel, engine='xlsxwriter')
df_export.to_excel(writer,sheet_name='Tiempos_Viajes', index = False)
df_ilts.to_excel(writer,sheet_name='ILTs', index = False)
writer.save()
send_email(name_excel,torre,pozo)
remove(name_excel)
        
print("Hola")
    


        
