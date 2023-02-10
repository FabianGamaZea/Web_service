import pandas as pd #libreria para un mejor manejo de los datos
import mysql.connector #libreria para conectar con nuestra base de datos

miConexion = mysql.connector.connect( host='localhost', user= 'root', passwd='', db='pmn') #creaccion de la conexion
cur = miConexion.cursor() #para ejecutar los querys

def cartera_vencida(df): #funcion para cartera vencida recibe como parametro el query resultante
    aux = [] #para guardar los datos que cumplen la condicion de cartera vencida
    for index, row in df.iterrows(): #recorremos todos los datos que nos trae el query
        if row[2] != None: #si en row[2] es nulo, significa que no hay historial, entonces es una venta
            dif = row[1] - row[2] #sacamos la diferencia que tenemos en nuestra dos fechas
            if int(dif.days) > 365: #si es mayor a 365 es una cartera vencida
                aux.append(row) #se agrega a nuestra lista 
    return len(aux) #regresamos el tamaño de nuestra lista, que en este caso hace referencia a el total de carteras vencidas
                
def vigente(df):
    aux = []
    for index, row in df.iterrows():
        if row[2] != None:
            if row[2].year == row[1].year: #si es el mismo año entramos a la clausula
                if row[2].month == row[1].month: #si es el mismo mes, estamos hablando de vigente
                    aux.append(row)
    return len(aux)
                    
def adelantado(df):
    aux = []
    for index, row in df.iterrows():
        if row[2] != None:
            dif = row[1] - row[2]
            if row[1] < row[2]: #si nuestra fecha de pago es menor a nuestra fecha de inicio del contrato
                if row[2].year == row[1].year: #si estamos en el mismo año nuestra condicion se puede resumir
                    if row[2].month != row[1].month: #mientras nuestros meses sean distintos con esto se cumple que sea adelanto
                        aux.append(row)
                else: #si estamos en años disntintos, ocuparemos otras condiciones
                    if row[2].month != row[1].month or int(dif.days) < -30: #si son meses distintos o si hay una diferencia mayor a 30 dias
                        aux.append(row)                  
    return len(aux)          
     
def recuperado(df):
    aux = []
    for index, row in df.iterrows():
        if row[2] != None:
            dif = row[1] - row[2]
            if row[2].year == row[1].year: #si estamos en el mismo año
                if row[2].month < row[1].month: #solo validamos que nuestra fecha de nuestro pago sea mayor a nuestra fecha de pago
                    aux.append(row)
            else:
                if int(dif.days) > 0 and int(dif.days) < 365 : #en caso de que sea distinto año solo validamos que no haya pasado un año
                    aux.append(row)
    return len(aux)

query = """SELECT DISTINCT pmn_datos_contratacion.contratacion_no_contrato, pagos_contratados.pagos_contratados_fecha_enque_pago, pmn_datos_contratacion.contratacion_fecha_fin_contrato_anterior, pmn_datos_contratacion.contratacion_sucursal, pagos_contratados.pagos_contratados_sucursal
FROM pmn_datos_contratacion
LEFT JOIN pmn_sis_parametros_pagos_pendiente ON pmn_datos_contratacion.contratacion_no_contrato = pmn_sis_parametros_pagos_pendiente.parametros_pagos_pendiente_no_contrato
LEFT JOIN pagos_contratados ON pmn_sis_parametros_pagos_pendiente.parametros_pagos_pendiente_id = pagos_contratados.pagos_contratados_parametro_fk_id
WHERE pagos_contratados.pagos_contratados_sucursal = """

query2 = """ AND MONTH(pagos_contratados.pagos_contratados_fecha_enque_pago)="""

query3 = """ AND pagos_contratados.pagos_contratados_no_pago_actual = 1 AND pagos_contratados.pagos_contratados_tipo = 'RENOVACION' AND YEAR(pagos_contratados.pagos_contratados_fecha_enque_pago) = """ 

sucursales = ["'Aguascalientes'", "'App'", "'Cancun'", "'Chihuahua'", "'Congreso'", "'Digital'", "'Durango'", "'Hermosillo'", "'Jalisco'", "'Juarez'", "'Leon'", "'Merida'", "'Monterrey'", "'Morelia'", "'Puebla'", "'Queretaro'", "'Tijuana'", "'Toluca'", "'Veracruz'", "'Villahermosa'", "'World Trade Center'", "'Zacatecas'"]
mes = ['Enero','Febrero','Marzo','Abril' , 'Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
n_mes = [1,2,3,4,5,6,7,8,9,10,11,12] # lista para poder iterar en cuestion de la seleccion
año = '2022' 
su = [] #aqui guardaremos nuestro resultado

for i in range(len(n_mes)): #recorremos en meses para poder hacer que la consulta vaya cambiando
    n_query = query + sucursales[20] + query2 + str(n_mes[i]) + query3 + año #aqui concatenamos nuestro query final que estara cambiando conforme a cada iteracion
    cur.execute(n_query) #ejecutamos el query
    queryResult = cur.fetchall() #guardamos el query
    df = pd.DataFrame(queryResult) #pasamos el query a un dataframe para manejar más facil los datos
    su.append([mes[i],adelantado(df),vigente(df), recuperado(df),cartera_vencida(df)]) #vamos agragando todo el resultado por cada iteracion
    
dt = pd.DataFrame(su, columns=['Mes','Adelantado', 'Vigente' ,'Recuperado', 'Cartera Vencida' ]) #hacemos un dataFrame con el resultado de las consultas
dt.loc[len(dt)] = ['Total' , sum(dt['Adelantado']), sum(dt['Vigente']), sum(dt['Recuperado']), sum(dt['Cartera Vencida'])] #sumamos el total por cada una de las columnas
print(dt)
fileQuery = sucursales[20] + '_' + año + '.xlsx' #realizamos un archivo dependiendo de la consulta realizada
dt.to_excel(fileQuery) #realizamos el archivo excel en la ruta anteriormente especificada
miConexion.close() #cerramos la conexion