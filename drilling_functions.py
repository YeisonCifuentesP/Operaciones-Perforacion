import pandas as pd
from datetime import datetime
import math as Math


import smtplib
import email.message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.application import MIMEApplication


 #ToDo cargue del excel, y el filtro, torre=50
   
#El archivo que reemplaza la BD que contiene los datos operacionales
archivo = 'D:\Independence\Sistema\Desktop\export_dataframe.csv'

df_csv = pd.read_csv(archivo)   
#Se eliminan las filas inservibles
#df_csv = df_csv.drop(df_csv[df_csv['Hole Depth(ft)'] == -999.25].index) 
df_csv = df_csv.drop(df_csv[df_csv['Rig Activity Code()']== -999.25].index) 
#df_csv = df_csv.drop(df_csv[df_csv['Bit Position(ft)'] > 11910].index) 


df_csv.replace(-999.250000 , 0)



#Se pasa a dateTIme la columna
df_csv['DateTime'] = pd.to_datetime(df_csv['DateTime'])#Columna datetime

#df_csv.to_csv('export_dataframe_Cosecha_C03.csv', index = False, header=True)

df_csv["Seccion"]='' 
df_csv["Estado"]=''
df_csv["Actividad"]=''
df_csv["Pozo"]=''
df_csv["RIG"]=''
#Si es necesario exportar el csv filtrado
#df_csv.to_csv('1ExportData_ASCII_ByTime_Independence SA 50_INFA 3146.csv', index=False)


    
def viaje_tuberia(torre, pozo, actividad, fecha_inicio, fecha_fin, seccion, estado):   
    print(actividad)
    #Se crea un dataframe con las columnas y equivalencias a trabajar
    df = pd.DataFrame()
    df["carga_gancho"]=df_csv["Hook Load(klb)"]*1000
    df["profundidad"]=df_csv["Bit Position(ft)"]
    df["fecha_hora"]=df_csv["DateTime"]
    df["posicion_bloque"]=df_csv["Block Height(ft)"]
   
    
    #df.loc[((df.fecha_hora >= fecha_inicio) & (df.fecha_hora <= fecha_fin)) ,'Seccion']='success'
    df_csv.loc[((df_csv.DateTime >= fecha_inicio) & (df_csv.DateTime <= fecha_fin)) ,'RIG']=torre
    df_csv.loc[((df_csv.DateTime >= fecha_inicio) & (df_csv.DateTime <= fecha_fin)) ,'Pozo']=pozo
    df_csv.loc[((df_csv.DateTime >= fecha_inicio) & (df_csv.DateTime <= fecha_fin)) ,'Seccion']=seccion
    df_csv.loc[((df_csv.DateTime >= fecha_inicio) & (df_csv.DateTime <= fecha_fin)) ,'Estado']=estado
    df_csv.loc[((df_csv.DateTime >= fecha_inicio) & (df_csv.DateTime <= fecha_fin)) ,'Actividad']=actividad    
    
    #FIltro para obtener por rango de fechas
    fecha_inicio=datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S.%f')
    fecha_fin=datetime.strptime(fecha_fin, '%Y-%m-%d %H:%M:%S.%f')
    df = ((df[(df.fecha_hora >= fecha_inicio) & (df.fecha_hora <= fecha_fin)]))
   
    
    df = df.sort_values(by="fecha_hora").reset_index(drop=True)
    

    indicador = 0
    indice=0;
    contador = 0
    maximo_carga = 0    
    bloque = 55000
    conexion = []
    torque = []
    carga = []
   

    for car, pos, pro in zip(df['carga_gancho'][0:], df['posicion_bloque'][0:], df['profundidad'][0:]):
        indice=indice+1
        if car > maximo_carga:
            maximo_carga = car

        if indicador == 0:

            if car > 55000:
                temp = 2
                indicador = 1                
                profundidad_inicio = pro

            else:
                if bloque < 55000:
                    if 'POOH' in actividad:
                        if bloque - pos > 3:#Confirmar si es un desplazamiento 
                            temp = 1
                            bloque = 55000
                        else:
                            temp = 0
                    else:
                        if abs(pos - bloque) > abs(profundidad_fin - profundidad_inicio):
                            temp = 1
                            bloque = 55000
                        else:
                            temp = 0
                else:
                    temp = 0

            conexion.append(temp)                    
            carga.append(maximo_carga)

        else:
           
            contador = contador+1            
           
            if car < 55000:
                    #Validar si la conexión es estable(1 minuto)
                if(len(df[indice:indice+12].loc[df['carga_gancho'] > 55000])==0):                    
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

def ilt_automate(df):

   
    if(df.empty):
        print("no hay elementos en la busqueda")
    else:
        df = (df[(df.tiempo_cuna_cuna < 25)]) 
        maximo = max(df.tiempo_cuna_cuna)  # Maximo tiempo_cuna_cuna
        minimo = min(df.tiempo_cuna_cuna)  # Minimo tiempo_cuna_cuna
        recorrido = maximo - minimo  # Recorrido necesario para identificar los intervalos
        nIntervalos = Math.ceil(Math.sqrt(len(df)))  # Numero de intervalos
        amplitud = 1  # Amplitud en cada uno de los intervalos
        while True:
            if((nIntervalos*amplitud) >= recorrido):
                break
            else:
                amplitud += 1

        # Extremo inferior de los intervalor
        extremoInferior = minimo-(((nIntervalos*amplitud)-recorrido)/2)
        # Extremo inferior en cada iteración
        extremoInferiorI = minimo-(((nIntervalos*amplitud)-recorrido)/2)

        dicIntervalos = ""
        for i in range(nIntervalos):
            extremoSuperior = extremoInferiorI+amplitud
            frecuencia = len(df[(df.tiempo_cuna_cuna >= extremoInferiorI) &
                                (df.tiempo_cuna_cuna < extremoSuperior)])  # La cantidad de veces que se repiten los datos dentro del intervalo
            if(dicIntervalos == ""):
                # Se crea el diccionario
                dicIntervalos = {
                    ""+str(extremoInferiorI)+" "+str(extremoSuperior): frecuencia}
            else:
                # Se le añaden elementos al diccionario
                dicIntervalos[""+str(extremoInferiorI) +
                              " "+str(extremoSuperior)] = frecuencia

            # Para la siguiente iteracion, siguiente intervalo
            extremoInferiorI = extremoSuperior

        
        # Valor sugerido para tomarlo como la media correcta entre los tiempos (80%)
        mediaSugerida = len(df)*0.8
        
        # Valor sumado entre los intervalos para obtener la media sugerida
        agrupacionIntervalos = 0
        indicadorILT = 0  # Valor que indica desde que intervalo empiezan los ILT's

        for k, v in dicIntervalos.items():
            
            agrupacionIntervalos = agrupacionIntervalos+v
            if(agrupacionIntervalos >= mediaSugerida):
                splitK = k.split()  # Separar la key en formato array
                
                indicadorILT = splitK[1]
                break


        df_muestra = (df[(df.tiempo_cuna_cuna >= extremoInferior) &
                         (df.tiempo_cuna_cuna < float(indicadorILT))])  # DataFrame con los valores que estan dentro del 80%
        # Promedio de los valores que estan dentro de la media
        promedio_muestra = df_muestra.tiempo_cuna_cuna.mean()
        
        # DataFrame con los valores que no estan dentro del 80%
        dfILT = (df[(df.tiempo_cuna_cuna >= float(indicadorILT))]) 
        tiempoTotalILT = 0
        for row in dfILT.itertuples():
            
            tiempoTotalILT += (row.tiempo_cuna_cuna-promedio_muestra)

        tiempoTotalILTHoras = tiempoTotalILT/60  # Tiempo total en horas de los ILT's
      
        return tiempoTotalILTHoras

    

def returnDF():
    return df_csv

def send_email(name_excel,torre,pozo):

    

    msg = MIMEMultipart()
    msg['Subject'] = 'Tiempos Viajes Perforación Torre:'+torre+", Pozo:"+pozo

    msg['From'] = 'informacion@skanhawk.com'
    #msg['To'] = 'lmrincon@skanhawk.com,yfcifuentes@skanhawk.com'
    msg['To'] = 'yfcifuentes@skanhawk.com'
    # msg["Cc"] = "serenity@example.com,inara@example.com"
    password = "Inde3030*"  
        
    #msg.attach(email_content)
    excel = MIMEApplication(open(name_excel, 'rb').read())
    excel.add_header('Content-Disposition', 'attachment', filename= msg['Subject']+".xlsx")
    msg.attach(excel)
    
   

    try:
        s = smtplib.SMTP('smtp-mail.outlook.com: 587')
        s.starttls()

        # Login Credentials for sending the mail
        s.login(msg['From'], password)

        # s.sendmail(msg['From'], msg["To"].split(",") + msg["Cc"].split(","), msg.as_string())
        s.sendmail(msg['From'], msg["To"].split(","), msg.as_string())
        s.quit()
    except:
        print('Ocurrio una excepción al enviar el correo')


