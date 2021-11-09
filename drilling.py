import pandas as pd
from datetime import datetime
import math as Math


    
def viaje_tuberia(torre, pozo, actividad, fecha_inicio, fecha_fin):

   #ToDo cargue del excel, y el filtro, torre=50
   
   #El archivo que reemplaza la BD que contiene los datos operacionales
    archivo = 'D:\Independence\Sistema\Desktop\SKAN_HAWK\DOCUMENTACION_SKAN\SCRIPTS_PYTHON\SCRIPT_PERFORACION\ExportData_ASCII_ByTime_Independence SA 50_INFA 3146.csv'

    


    df_csv = pd.read_csv(archivo)   
    #Se eliminan las filas inservibles
    df_csv = df_csv.drop(df_csv[df_csv['Hole Depth(ft)'] == -999.25].index) 
    #Se pasa a dateTIme la columna
    df_csv['DateTime'] = pd.to_datetime(df_csv['DateTime'])#Columna datetime
    
    #Si es necesario exportar el csv filtrado
    #df_csv.to_csv('1ExportData_ASCII_ByTime_Independence SA 50_INFA 3146.csv', index=False)

    #Se crea un dataframe con las columnas y equivalencias a trabajar
    df = pd.DataFrame()
    df["carga_gancho"]=df_csv["Hook Load(klb)"]*1000
    df["profundidad"]=df_csv["Bit Position(ft)"]
    df["fecha_hora"]=df_csv["DateTime"]
    df["posicion_bloque"]=df_csv["Block Height(ft)"]

    #FIltro para obtener por rango de fechas
    fecha_inicio=datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S.%f')
    fecha_fin=datetime.strptime(fecha_fin, '%Y-%m-%d %H:%M:%S.%f')
    df = ((df[(df.fecha_hora >= fecha_inicio) & (df.fecha_hora <= fecha_fin)]))

    
    df = df.sort_values(by="fecha_hora").reset_index(drop=True)
    

    indicador = 0
    contador = 0
    maximo_carga = 0    
    bloque = 10000
    conexion = []
    torque = []
    carga = []
   

    for car, pos, pro in zip(df['carga_gancho'][0:], df['posicion_bloque'][0:], df['profundidad'][0:]):

        if car > maximo_carga:
            maximo_carga = car

        if indicador == 0:

            if car > 30000:
                temp = 2
                indicador = 1                
                profundidad_inicio = pro

            else:
                if bloque < 10000:
                    if 'POOH' in actividad:
                        if bloque - pos > 3:
                            temp = 1
                            bloque = 10000
                        else:
                            temp = 0
                    else:
                        if abs(pos - bloque) > abs(profundidad_fin - profundidad_inicio):
                            temp = 1
                            bloque = 10000
                        else:
                            temp = 0
                else:
                    temp = 0

            conexion.append(temp)                    
            carga.append(maximo_carga)

        else:
           
            contador = contador+1

            if car < 30000:
                temp = 1
                bloque = pos
                profundidad_fin = pro                
                carga.append(maximo_carga)                
                contador = 0                
                maximo_carga = 0  # reset Carga
                indicador = 0

            else:
                temp = 0               
                carga.append(maximo_carga)

            conexion.append(temp)

    df['fin_conexion'] = conexion    
    df['max_carga'] = carga    
    df_new = df[df['fin_conexion'] != 0].reset_index(drop=True)

    real = []
    temp = 0

    for i, row in df_new.iterrows():

        if temp == 1:
            if row['fin_conexion'] == 1:
                real.append(0)
            else:
                try:
                    if abs(df_new['profundidad'][i+1] - row['profundidad']) > 25:
                        real.append(2)
                        temp = 0
                    else:
                        real.append(0)
                except:
                    real.append(0)

        elif row['fin_conexion'] == 2:
            try:
                if abs(df_new['profundidad'][i+1] - row['profundidad']) > 25:
                    real.append(2)

                else:
                    real.append(0)
                    temp = 1
            except:
                real.append(0)
        else:
            real.append(1)

    df_new['fin_conexion'] = real
    df_new = df_new[df_new['fin_conexion'] != 0].reset_index(drop=True)

    tipo = []
    tiempo_cuna_cuna = []
    tiempo_con_carga = []
    velocidad_con_carga = []
    tiempo_bloque = []
    velocidad_bloque = []
    t_conexion_desconexion = []
    carga = []
    profundidad = []
    fecha_hora = []
    
    for i, row in df_new.iterrows():

        if row['fin_conexion'] == 2:
            if abs(df_new['profundidad'][i+1]-row['profundidad']) > 25:
                if abs(df_new['profundidad'][i+1]-row['profundidad']) > 55:
                    indicador = 'dobles'
                else:
                    indicador = 'sencillos'
            else:
                indicador = 0
            try:
                t_carga = round(
                    (df_new['fecha_hora'][i+1] - row['fecha_hora']).total_seconds(), 3)
                v_carga = round(
                    abs(df_new['profundidad'][i+1] - row['profundidad']) / (t_carga/60), 2)
            except:
                t_carga = 0
                v_carga = 0

            if 'RIH' in actividad:
                try:
                    t_bloque = round(
                        (df_new['fecha_hora'][i+2] - df_new['fecha_hora'][i+1]).total_seconds(), 3)
                    v_bloque = round(abs(
                        df_new['posicion_bloque'][i+2] - df_new['posicion_bloque'][i+1]) / (t_bloque/60), 2)
                except:
                    t_bloque = 0
                    v_bloque = 0

                try:
                    if df_new['fin_conexion'][i+2] == 1:
                        t_con_des = round(
                            (df_new['fecha_hora'][i+3] - df_new['fecha_hora'][i+2]).total_seconds(), 3)
                    else:
                        t_con_des = 0
                except:
                    t_con_des = 0

            else:
                try:
                    t_con_des = round(
                        (df_new['fecha_hora'][i+2] - df_new['fecha_hora'][i+1]).total_seconds(), 3)
                except:
                    t_con_des = 0

                try:
                    if df_new['fin_conexion'][i+2] == 1:
                        t_bloque = round(
                            (df_new['fecha_hora'][i+3] - df_new['fecha_hora'][i+2]).total_seconds(), 3)
                        v_bloque = round(abs(
                            df_new['posicion_bloque'][i+3] - df_new['posicion_bloque'][i+2]) / (t_bloque/60), 2)
                    else:
                        t_bloque = 0
                        v_bloque = 0
                except:
                    t_bloque = 0
                    v_bloque = 0

            t_cuna_cuna = (t_carga + t_bloque + t_con_des)/60

            tiempo_cuna_cuna.append(t_cuna_cuna)
            carga.append(df_new['max_carga'][i+1])           
            profundidad.append(row['profundidad'])
            fecha_hora.append(row['fecha_hora'])
            tipo.append(indicador)            
            tiempo_con_carga.append(t_carga)
            velocidad_con_carga.append(v_carga)
            tiempo_bloque.append(t_bloque)
            velocidad_bloque.append(v_bloque)
            t_conexion_desconexion.append(t_con_des)
             

    conexiones = pd.DataFrame({'fecha_hora_inicio': fecha_hora, 'tiempo_cuna_cuna': tiempo_cuna_cuna,
                               'tipo_conexion': tipo, 'tiempo_carga': tiempo_con_carga,
                               'velocidad_carga': velocidad_con_carga, 'tiempo_bloque': tiempo_bloque,
                               'velocidad_bloque': velocidad_bloque, 'tiempo_conexion_desconexion': t_conexion_desconexion,
                               'carga_gancho': carga,'profundidad': profundidad})

   

    conexiones['actividad'] = actividad
    conexiones['torre'] = torre
    conexiones['pozo'] = pozo
    conexiones['conexion'] = list(range(1, len(conexiones)+1))
   
    return conexiones
