# Libreria para el manejo de Dataframes (Datos estructurados)
import pandas as pd



from drilling import viaje_tuberia

#Archivo con los viajes que se realizaron en el pozo de perforación
archivo = 'D:\Independence\Sistema\Desktop\SKAN_HAWK\DOCUMENTACION_SKAN\SCRIPTS_PYTHON\SCRIPT_PERFORACION\Datos_desarrollo_perforacion.xlsx'


df = pd.read_excel(archivo, sheet_name='Marco_tiempo')   


for row in df.itertuples():
    
    torre = str(row.deviceId)
    pozo = str(row.pozo).upper()
    actividad = str(row.Actividades).upper()     
    fecha_inicio = row.inicio
    fecha_fin = row.fin
    
    datos = viaje_tuberia(torre, pozo, actividad, fecha_inicio,
                              fecha_fin)
        
        

    


        
