import pandas as pd
import mysql.connector
#pip install mysql-connector-python
import datetime
import yfinance as yf
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def conectar_db():
    mydb = mysql.connector.connect(
        host="bycegytc3os0kmsrpu4c-mysql.services.clever-cloud.com",
        user="uh4br2tei7wx6fvf",
        password="U9Z2AaOxPh1181Kt3sCc",
        database="bycegytc3os0kmsrpu4c",
    )

    cursor = mydb.cursor()
    cursor.execute( 'CREATE TABLE IF NOT EXISTS cat_criptomonedas ( ticker TEXT, nombre TEXT )' )        
    cursor.execute( 'CREATE TABLE IF NOT EXISTS criptomonedas_hystory ( ticker TEXT, Date TEXT, Open REAL, High REAL, Low REAL, Close REAL, Volume BIGINT)' )
    cursor.execute('CREATE TABLE IF NOT EXISTS criptomonedas_day ( ticker TEXT, Date TEXT, Time TEXT, Open REAL, High REAL, Low REAL, Close REAL, Volume BIGINT)')            
    mydb.commit()
    mydb.close()

def get_nom_columns(tabla):
    mydb = mysql.connector.connect(
        host="bycegytc3os0kmsrpu4c-mysql.services.clever-cloud.com",
        user="uh4br2tei7wx6fvf",
        password="U9Z2AaOxPh1181Kt3sCc",
        database="bycegytc3os0kmsrpu4c",
    )

    cursor = mydb.cursor()
    sentencia = "SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'bycegytc3os0kmsrpu4c' AND TABLE_NAME = '" + tabla + "' ORDER BY ORDINAL_POSITION"
    
    cursor.execute(sentencia)
    resultado = cursor.fetchall()
    resultado = pd.DataFrame(resultado)    
    resultado.columns = ['column_name', 'data_type']
    resultado = resultado['column_name']
    resultado = resultado.tolist()
    mydb.close()
    return resultado

def cargar_datos(tabla, datos):
    #está función carga los datos a una tabla desde un dataframe
    mydb = mysql.connector.connect(
        host="bycegytc3os0kmsrpu4c-mysql.services.clever-cloud.com",
        user="uh4br2tei7wx6fvf",
        password="U9Z2AaOxPh1181Kt3sCc",
        database="bycegytc3os0kmsrpu4c",
    )
    col_tabla = get_nom_columns(tabla)            
    cursor = mydb.cursor()    
    sentencia = 'INSERT INTO ' + tabla + ' (' + ','.join(col_tabla) + ') VALUES ('    
    sentencia = sentencia + ','.join(['%s']*len(col_tabla) ) + ')'         
    f = datos.values.tolist()
    cursor.executemany(sentencia, f)
    mydb.commit()
    mydb.close()

def eliminar_tabla(tabla):
    mydb = mysql.connector.connect(
        host="bycegytc3os0kmsrpu4c-mysql.services.clever-cloud.com",
        user="uh4br2tei7wx6fvf",
        password="U9Z2AaOxPh1181Kt3sCc",
        database="bycegytc3os0kmsrpu4c",
    )

    cursor = mydb.cursor()
    sentencia = 'DROP TABLE {}'.format(tabla)
    cursor.execute(sentencia)
    mydb.commit()
    mydb.close()

def borrar(tabla, campo_condicional = [], condicion = []):
    conexion = mysql.connector.connect(
        host="bycegytc3os0kmsrpu4c-mysql.services.clever-cloud.com",
        user="uh4br2tei7wx6fvf",
        password="U9Z2AaOxPh1181Kt3sCc",
        database="bycegytc3os0kmsrpu4c",
    )
    cursor = conexion.cursor()
    sentencia = 'Delete from ' + tabla
    if len(campo_condicional) != 0:
        sentencia = sentencia + ' where '
        for i in range(len(campo_condicional)):
            sentencia = sentencia + campo_condicional[i] + ' = %s and '
        sentencia = sentencia[:-5]

    cursor.execute(sentencia, (condicion))
    conexion.commit()
    conexion.close()

def get_data(ticker, start_date = '2022-01-02', end_date = ''):
    if end_date == '':
        end_date = datetime.date.today()
    days= pd.date_range(start = start_date , end = end_date)
    yticker = yf.Ticker(ticker)
    stock_data =yticker.history(start=start_date , end=end_date)
    stock_data.reset_index(inplace = True)
    stock_data['Date'] = stock_data['Date'].apply(lambda x: datetime.date(x.year, x.month, x.day) )
    stock_data.set_index('Date', inplace = True)
    stock_data = stock_data.reindex(days, method = 'nearest')
    stock_data.reset_index(inplace = True)
    stock_data.rename(columns = {'index':'Date'}, inplace = True)
    stock_data['ticker'] = ticker
    stock_data = stock_data[['ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    return stock_data

def get_data_daily(ticker):
    yticker = yf.Ticker(ticker)
    stock_data =yticker.history(period='1d')
    horario = datetime.datetime.now().time()
    fecha = datetime.date.today()
    stock_data['Time'] = horario
    stock_data.reset_index(inplace = True)
    stock_data['Date'] = fecha
    stock_data['ticker'] = ticker
    stock_data = stock_data[['ticker', 'Date','Time', 'Open', 'High', 'Low', 'Close', 'Volume']]
    return stock_data


def get_data_table(tabla, campos = [], condiciones = []):
    conexion = mysql.connector.connect(
        host="bycegytc3os0kmsrpu4c-mysql.services.clever-cloud.com",
        user="uh4br2tei7wx6fvf",
        password="U9Z2AaOxPh1181Kt3sCc",
        database="bycegytc3os0kmsrpu4c",
    )
    cursor = conexion.cursor()
    if len(campos) == 0:
        sentencia = 'SELECT * FROM ' + tabla
        cursor.execute(sentencia)
        resultados = cursor.fetchall()
    else:
        sentencia = 'SELECT * FROM ' + tabla + ' WHERE '
        for i in range(len(campos)):
            sentencia = sentencia + campos[i] + ' = %s and '
        sentencia = sentencia[:-5]
        cursor.execute(sentencia, tuple( condiciones) )
        resultados = cursor.fetchall()
    resultados = pd.DataFrame(resultados)
    if resultados.shape[0]>0:
        nom_col = get_nom_columns(tabla)
        resultados.columns = nom_col
    conexion.close()
    print(resultados)
    return resultados

def update_crypto_values_history():
    criptos = get_data_table('cat_criptomonedas')
    for i in range(criptos.shape[0]):
        ticker = criptos['ticker'].loc[i]
        datos = get_data_table('criptomonedas_hystory', campos = ['ticker'], condiciones = [ticker])
        if datos.shape[0]==0:
            start_date = '2022-01-01'
        else:
            start_date = datos['Date'].max()

        if datetime.datetime.strptime(start_date, '%Y-%m-%d' ).date() < datetime.date.today():
            data = get_data(ticker, start_date = start_date, end_date = '')
            if data.shape[0]>0:
                data['Date'] = data['Date'].apply(lambda x: x.strftime('%Y-%m-%d') )                
                cargar_datos('criptomonedas_hystory', data)

def update_crypto_values_day():
    criptos = get_data_table('cat_criptomonedas')
    for i in range(criptos.shape[0]):
        ticker = criptos['ticker'].loc[i]
        data  = get_data_daily(ticker)
        data['Date'] = data['Date'].apply(lambda x: x.strftime('%Y-%m-%d') )
        data['Time'] = data['Time'].apply(lambda x: x.strftime('%H:%M:%S') )
        datos = get_data_table('criptomonedas_day', campos = ['ticker'], condiciones = [ticker])
        if datos.shape[0]==0:
            cargar_datos('criptomonedas_day', data)
        else:
            fecha = datos['Date'].max()
            if datetime.datetime.strptime(fecha, '%Y-%m-%d' ).date() != datetime.date.today():
                #print('entro')
                borrar('criptomonedas_day')
            cargar_datos('criptomonedas_day', data)

        data_history = data.drop(columns = ['Time'])
        if data_history.shape[0]>0:
            fecha = data_history['Date'].iloc[0]
            borrar('criptomonedas_hystory', campo_condicional = ['ticker', 'Date'], condicion = [ticker, fecha])
            cargar_datos('criptomonedas_hystory', data_history)

def rendimiento_log(fecha = ''):
    data = get_data_table('criptomonedas_hystory')
    if fecha != '':
        fechas = data['Date'][data['Date']>= fecha].unique()
        data = data[data['Date'].isin(fechas)]
    else:
        fechas = data['Date'].unique()

    f_min = min(fechas)
    f_max = max(fechas)

    ticker = data['ticker'].unique()
    medias = []
    desv_stds = []
    volumenes = []
    for i in range( len(ticker) ):
        data_sub = data[data['ticker']==ticker[i]]
        data_sub.reset_index(drop = True, inplace = True)
        data_sub['log_ret'] = np.log(data_sub.Close) - np.log(data_sub.Close.shift(1))
        media = data_sub['log_ret'].dropna().mean()*365*100
        desv_std = np.sqrt(data_sub['log_ret'].dropna().var()*252)*100
        medias.append(media)
        desv_stds.append(desv_std)
        volumenes.append( data_sub['Volume'].mean()/1000000 )
    metricas = pd.DataFrame({'ticker':ticker, 'Mean':medias, 'Std Dev':desv_stds, 'Volume':volumenes})
    return metricas, f_min, f_max

def put_cripto_names(df):
    data = get_data_table('cat_criptomonedas')
    df = df.merge(data, how = 'left', on = ['ticker'])
    return df
