import datetime
import dash
from dash import html, dcc
import plotly.graph_objects as go
import plotly.express as px
#import cloud_funciones as d_fun
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
#import dash_table
from dash import dash_table

#definimos el objeto
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
#se incluye está sentencia para utilizar un servidor no local
server = app.server
from app import cloud_funciones as d_fun

app.layout = html.Div(id = 'parent', children = [
    dcc.Location(id='url', refresh=True), 
    dcc.Store(id='intraday-value'),
    dcc.Store(id='daily-value'),
    html.H1(id = 'H1', children = "Criptomonedas: Evolución de las Criptomonedas", style = {'textAlign':'center',\
                                            'marginTop':40,'marginBottom':40}),
    #########################
    html.Div([
        html.P('Fuente Yahoo Finance https://finance.yahoo.com/'),     
         
        ]),
    #########################
    #########################    
    html.Div(id = 'card-values'),    
    #############################################
    #############################################
    html.Button("Download Rendimiento", id="btn-download-txt"),
    dcc.Download(id="download-text"),    
    #############################################
    #############################################
    ####Gráficas de desempeño por 
    html.Br(),
    html.Br(),
    dcc.Markdown('''
                **Escoge el periodo** 
                '''),    
    ## con **texto** es bold, *texto* es italic
    dcc.RadioItems(id = "radio_spam", 
                    options = [
                                {'label': 'Desde 2022-01-02', 'value': 'Desde 2022-01-02'},
                                {'label': 'Últimos 6 meses', 'value': '6 meses'},
                                {'label': 'Últimos 30 días', 'value': '30 días'},
                               ] , value = '6 meses', inline=False ),    
    #############################################
    #############################################
    html.Div([
        dcc.Graph(id = 'bar_plot'),
        html.Div('La linea corresponde al promedio ponderado por volumen de las Criptomonedas en análisis',
                 style={'color': 'gray', 'fontSize': 12}),        
        ]),        
     #############################################
     #############################################
     ####Gráficas de desempeño por 
    html.Br(),
    html.Br(),
    dcc.Markdown('''
                **Escoja dos periodos de análisis** 
                '''), 
    dmc.MultiSelect(
        label="Cuadro de Selección",
        description="Escoja sólo dos opciones",
         id="framework-multi-select",
        data=[
                {'label': 'Desde 2022-01-02', 'value': 'Desde 2022-01-02'},
                {'label': 'Últimos 6 meses', 'value': '6 meses'},
                {'label': 'Últimos 30 días', 'value': '30 días'},
        ],
        value = ["6 meses", "30 días"],
        maxSelectedValues=2,
        style={"width": 400},
    ),
    html.Br(),
    html.Br(),    
    dcc.RangeSlider(id='range-slider', min = -500, max = 500, step = 50),    
    html.Div([
        dcc.Graph(id = 'scatter_plot'),
        html.Div('Sólo se presentan las criptomonedas con volumen de operación promedio diario mayor a 100 unidades', 
                 style={'color': 'gray', 'fontSize': 12}),        
        ]),   
    
    #############################################
    #############################################
    html.Br(),
    html.Br(),
    dcc.Markdown(''' #### Información de Precios Intradía '''), ## este es tamaño h3
    ## ### este es tamaño h3
    ## # este es tamaño h1
    html.Div([
        dcc.Graph(id = 'several_plots'),
        html.Div('Sólo se presentan la información de las tres principales criptomonedas',
                 style={'color': 'gray', 'fontSize': 12}),        
        ]),   
    #############################################
    #############################################
    html.Br(),
    html.Br(),
    html.P('Volumen promedio operado intradía', style = {'color':'navy', "font-weight": "bold", 'size':25 }),
    html.Div( id = 'volume-table', style={'width': '35%'},
    ),  
    #############################################
    #############################################
    html.Br(),
    html.Br(),
    html.Div(id = 'ultima-actualizacion'),      
    #############################################
    #############################################
    #se actualiza cada 30 segundos
    html.Meta(httpEquiv="refresh",content="600"),
        ]    
    )
#################################################
###############--- callbacks
#################################################
#################################################
@app.callback(
    Output('intraday-value', 'data'),
    Input('url', 'pathname')
    )
def global_data_intra(relative_pathname):
    #se carga la información intradia
    d_fun.update_crypto_values_day()
    cripto_intradia = d_fun.get_data_table('criptomonedas_day', texto = 'aqui')    
    cripto_intradia = d_fun.put_cripto_names(cripto_intradia)
    cripto_intradia_gb = cripto_intradia[['nombre', 'Volume']].groupby(by=['nombre'])
    cripto_intradia_gb = cripto_intradia_gb['Volume'].mean()
    cripto_intradia_gb.sort_values(ascending=False, inplace = True)
    l_cripto_intradia_gb = [list(cripto_intradia_gb.index), cripto_intradia_gb.to_list()]
    #se convierte a una lista porque entiende el valor de una lista    
    return l_cripto_intradia_gb
#################################################
#################################################
@app.callback(
    Output('daily-value', 'data'),
    Input('url', 'pathname'))
def global_data(relative_pathname):
    #se carga la información diaria
    d_fun.update_crypto_values_history()
    
    #### se realizan las funciones necesarias    
    rend_hist, fmin, fmax = d_fun.rendimiento_log()    

    f_6meses = datetime.datetime.strptime(fmax, '%Y-%m-%d' ).date() - datetime.timedelta(182)
    f_6meses = f_6meses.strftime('%Y-%m-%d')
    rend_6m, fmin_6m, fmax_6m = d_fun.rendimiento_log(f_6meses)
    

    f_30d = datetime.datetime.strptime(fmax, '%Y-%m-%d' ).date() - datetime.timedelta(30)
    f_30d = f_30d.strftime('%Y-%m-%d')
    rend_30d, fmin_30d, fmax_30d = d_fun.rendimiento_log(f_30d)    
    #########
    rend_hist['Periodo']  = 'Desde 2022-01-02'
    rend_hist['fecha min']  = fmin
    rend_hist['fecha max']  = fmax
    rend_6m['Periodo']  = '6 meses'
    rend_6m['fecha min']  = fmin_6m
    rend_6m['fecha max']  = fmax_6m
    rend_30d['Periodo']  = '30 días'
    rend_30d['fecha min']  = fmin_30d
    rend_30d['fecha max']  = fmax_30d
    rendimiento = pd.concat([rend_hist, rend_6m, rend_30d], axis = 0, ignore_index = True)    
    rendimiento = d_fun.put_cripto_names(rendimiento)       
    rendimiento_json = rendimiento.to_json(force_ascii = False)        
    return rendimiento_json
#################################################
#################################################
@app.callback(        
    Output(component_id = 'card-values', component_property = 'children'),
    Input(component_id = 'daily-value', component_property = 'data'))
def display_card(data_card):    
    rendimiento = pd.read_json(data_card)
    periodos = list( rendimiento['Periodo'].unique() )
    medias = []
    std_dev = []    
    l_fmin = []
    l_fmax = []
    for i in range(len(periodos)):
        rendimiento_sub = rendimiento[rendimiento['Periodo'] == periodos[i]]
        mean_hist = rendimiento_sub['Mean'].dot(rendimiento_sub['Volume'])/rendimiento_sub['Volume'].sum()
        std_hist = rendimiento_sub['Std Dev'].dot(rendimiento_sub['Volume'])/rendimiento_sub['Volume'].sum()
        medias.append(mean_hist)
        std_dev.append(std_hist)        
        valor_fmin = list(rendimiento_sub['fecha min'].unique())
        l_fmin.append(valor_fmin[0])
        valor_fmax = list(rendimiento_sub['fecha max'].unique())
        l_fmax.append(valor_fmax[0])

    elemento = html.Div([
    dbc.Row([
                dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                        html.P("Rendimiento del {} al {}".format(l_fmin[0], l_fmax[0])),                                        
                                        html.H4( str(round(medias[0],2)) + '%', style = {'color':'red'} ),                                        
                                        ], className="border-start border-success border-5"),                                        
                                className="text-center m-4", 
                                ),
                        ], width=6, lg=3),                
                dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                        html.P("Desviación Estándar del {} al {}".format(l_fmin[0], l_fmax[0])),                                        
                                        html.H4( str(round(std_dev[0],2)) + '%', style = {'color':'black'} ),                                        
                                        ], className="border-start border-success border-5"),                                        
                                className="text-center m-4", 
                                ),                        
                        ], width=6, lg=3),
                dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                        html.P("Coef. de Variación {} al {}".format(l_fmin[0], l_fmax[0])),                                        
                                        html.H4( str(round(medias[0]/std_dev[0],2)), style = {'color':'red'} ),                                        
                                        ], className="border-start border-success border-5"),                                        
                                className="text-center m-4", 
                                ),                        
                        ], width=6, lg=3),
            ], align="center",
            ),
    #########################
    #########################
    dbc.Row([
                dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                        html.P("Rendimiento del {} al {}".format(l_fmin[1], l_fmax[1])),                                        
                                        html.H4( str(round(medias[1],2)) + '%', style = {'color':'black'} ),                                        
                                        ], className="border-start border-danger border-5"),                                        
                                className="text-center m-4", 
                                ),
                        ], width=6, lg=3),                
                dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                        html.P("Desviación Estándar del {} al {}".format(l_fmin[1], l_fmax[1])),                                        
                                        html.H4( str(round(std_dev[1],2)) + '%', style = {'color':'black'} ),                                        
                                        ], className="border-start border-danger border-5"),                                        
                                className="text-center m-4", 
                                ),                        
                        ], width=6, lg=3),
                dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                        html.P("Coef. de Variación {} al {}".format(l_fmin[1], l_fmax[1])),                                        
                                        html.H4( str(round(medias[1]/std_dev[1],2)), style = {'color':'black'} ),                                        
                                        ], className="border-start border-danger border-5"),                                        
                                className="text-center m-4", 
                                ),                        
                        ], width=6, lg=3),
            ], align="center",
            ),
    #############################################
    #############################################
    dbc.Row([
                dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                        html.P("Rendimiento del {} al {}".format(l_fmin[2], l_fmax[2])),                                        
                                        html.H4( str(round(medias[2],2)) + '%', style = {'color':'black'} ),                                        
                                        ], className="border-start border-info border-5"),                                        
                                className="text-center m-4", 
                                ),
                        ], width=6, lg=3),                
                dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                        html.P("Desviación Estándar del {} al {}".format(l_fmin[2], l_fmax[2])),                                        
                                        html.H4( str(round(std_dev[2],2)) + '%', style = {'color':'black'} ),                                        
                                        ], className="border-start border-info border-5"),                                        
                                className="text-center m-4", 
                                ),                        
                        ], width=6, lg=3),
                dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                        html.P("Coef. de Variación {} al {}".format(l_fmin[2], l_fmax[2])),                                        
                                        html.H4( str(round(medias[2]/std_dev[2],2)), style = {'color':'black'} ),                                        
                                        ], className="border-start border-info border-5"),                                        
                                className="text-center m-4", 
                                ),                        
                        ], width=6, lg=3),
            ], align="center",
            ),
    ]),

    return elemento

#################################################
#################################################
@app.callback(
    Output("download-text", "data"),    
    Input(component_id = "btn-download-txt", component_property = "n_clicks"),    
    prevent_initial_call=True,
)
def func(n_clicks):        
    rend_hist, fmin, fmax = d_fun.rendimiento_log()    

    f_6meses = datetime.datetime.strptime(fmax, '%Y-%m-%d' ).date() - datetime.timedelta(182)
    f_6meses = f_6meses.strftime('%Y-%m-%d')
    rend_6m, fmin_6m, fmax_6m = d_fun.rendimiento_log(f_6meses)
    
    f_30d = datetime.datetime.strptime(fmax, '%Y-%m-%d' ).date() - datetime.timedelta(30)
    f_30d = f_30d.strftime('%Y-%m-%d')
    rend_30d, fmin_30d, fmax_30d = d_fun.rendimiento_log(f_30d)    
    #########
    rend_hist['Periodo']  = 'Desde 2022-01-02'
    rend_hist['fecha min']  = fmin
    rend_hist['fecha max']  = fmax
    rend_6m['Periodo']  = '6 meses'
    rend_6m['fecha min']  = fmin_6m
    rend_6m['fecha max']  = fmax_6m
    rend_30d['Periodo']  = '30 días'
    rend_30d['fecha min']  = fmin_30d
    rend_30d['fecha max']  = fmax_30d
    rendimiento = pd.concat([rend_hist, rend_6m, rend_30d], axis = 0, ignore_index = True)    
    rendimiento = d_fun.put_cripto_names(rendimiento)               
    salida = rendimiento.set_index('ticker')          
    return dcc.send_data_frame(salida.to_csv, "rendimientos.csv")

############################################################################
@app.callback(
    Output(component_id='bar_plot', component_property= 'figure'),
    Input(component_id="radio_spam", component_property= 'value'), 
    Input(component_id = 'daily-value', component_property = 'data'),
)
def graph_radio(radio_button, data_radio):
    #print(radio_button)
    rendimiento = pd.read_json(data_radio)
    df = rendimiento[rendimiento['Periodo'] == radio_button]  

    periodos = list( rendimiento['Periodo'].unique() )
    medias = []    
    for i in range(len(periodos)):
        rendimiento_sub = rendimiento[rendimiento['Periodo'] == periodos[i]]
        mean_hist = rendimiento_sub['Mean'].dot(rendimiento_sub['Volume'])/rendimiento_sub['Volume'].sum()        
        medias.append(mean_hist)        

    if radio_button == 'Desde 2022-01-02':
        _rend = medias[0]
    elif radio_button == '6 meses':
        _rend = medias[1]
    else:
        _rend = medias[2]    
    df['Promedio'] = _rend
    df.sort_values(by = 'Mean', ascending=True, inplace = True)
    fig1 = px.bar(data_frame=df, y="Mean", x="nombre")
    fig2 = px.line(data_frame=df, y="Promedio", x="nombre")
    fig2['data'][0]['line']['color']='rgb(139,0,0)'
    fig = go.Figure(data = fig1.data + fig2.data)
    return fig

############################################################################
@app.callback(
    Output(component_id='range-slider', component_property= 'value'),
    Input(component_id="framework-multi-select", component_property= 'value'), 
    Input(component_id='daily-value', component_property= 'data'),   
)
def slider_set_range(valores, data_daily):
    #print(data_daily)    
    if len(valores)  == 1:
        l_lista = ["Desde 2022-01-02", "6 meses", "30 días" ]        
        l_lista.remove(valores[0])
        valores.append(l_lista[0])

    rendimiento = pd.read_json(data_daily)    
    df0 = rendimiento[ rendimiento['Periodo'] == valores[0] ]            
    df0 = df0[['nombre', 'Mean']]
    df0.columns = ['nombre', valores[0]]    
    df1 = rendimiento[ rendimiento['Periodo'] == valores[1] ]
    df1 = df1[['nombre', 'Mean', 'Volume']]
    df1.columns = ['nombre', valores[1], 'Volume']
    df = pd.merge(df0, df1, on = ['nombre'])        
    df = df[df['Volume']>100]        
    v_max = df[[valores[0], valores[1]]].max().max()
    v_max = int(v_max)    
    v_min = df[[valores[0], valores[1]]].min().min()
    v_min = int(v_min)    
    lista_min_max = [v_min-1, v_max+1]    
    return lista_min_max    

############################################################################
@app.callback(
    Output(component_id='scatter_plot', component_property= 'figure'),
    Input(component_id="framework-multi-select", component_property= 'value'),  
    Input(component_id="range-slider", component_property= 'value'),   
    Input(component_id='daily-value', component_property= 'data'), 
)
def graph_multi(option, option_2, data_daily_scatter):         
    if len(option)  == 1:
        l_lista = ["Desde 2022-01-02", "6 meses", "30 días" ]
        l_lista.remove(option[0])
        option.append(l_lista[0])

    rendimiento = pd.read_json(data_daily_scatter)   
    df0 = rendimiento[rendimiento['Periodo'] == option[0]]            
    df0 = df0[['nombre', 'Mean']]
    df0.columns = ['nombre', option[0]]    
    df1 = rendimiento[rendimiento['Periodo'] == option[1]]
    df1 = df1[['nombre', 'Mean', 'Volume']]
    df1.columns = ['nombre', option[1], 'Volume']
    df = pd.merge(df0, df1, on = ['nombre'])        
    df_scatter = df[df['Volume']>100]    
    v_max = df_scatter[[option[0], option[1]]].max().max()
    v_max = int(v_max)    
    v_min = df_scatter[[option[0], option[1]]].min().min()
    v_min = int(v_min)    
    x2 = np.linspace(v_min, v_max, num=v_max-v_min)            
    y2 = x2    
    fig_2p_1 = px.scatter(df_scatter, x=option[0], y=option[1], color='nombre' )        
    
    fig_2p_1.update_traces(marker={'size': 12})
        
    #fig_2p_1 = px.scatter(df, x=option[0], y=option[1], color='nombre', size='Volume',size_max=12, size_min = 5)
    fig_2p_2 = px.line(y=y2, x=x2)
    fig_2p_2['data'][0]['line']['width']=0.5
    fig_2p_2['data'][0]['line']['color']='rgb(139,0,0)'
    fig_2p = go.Figure(data = fig_2p_1.data + fig_2p_2.data)                
    fig_2p.update_layout(xaxis_title=option[0],yaxis_title=option[1])        
    fig_2p.update_xaxes(range=(option_2[0],option_2[1]))
    return fig_2p

#######################################
#######################################
#'several_plots'
@app.callback(
    Output(component_id='several_plots', component_property= 'figure'),
    Input(component_id='intraday-value', component_property= 'data'),
    Input(component_id='url', component_property= 'pathname')           
)
def update_several_plots(data, relative_pathname):
    print(data)
    cripto_intradia = d_fun.get_data_table('criptomonedas_day')
    cripto_intradia = d_fun.put_cripto_names(cripto_intradia)
    data_dic = {'nombre':data[0], 'Volume':data[1]}
    fig_daily = make_subplots(rows=1, cols=3, start_cell="top-left")
    nom_cripto = data_dic['nombre']

    for i in range(3):
        cripto_intradia_sub = cripto_intradia[cripto_intradia['nombre'] == nom_cripto[i]]
        cripto_intradia_sub.sort_values(by = ['Time'], inplace = True)
        cripto_intradia_sub = cripto_intradia_sub[['Time', 'Close']]
        fig_daily.add_trace(go.Scatter(x=cripto_intradia_sub['Time'],
                                   y=cripto_intradia_sub['Close'],
                                   name=nom_cripto[i]),
                                   row=1, col=i+1)
    #texto = 'Última Actualización {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #print(cripto_intradia_sub)
    return fig_daily

#######################################
#######################################
#'volume-table'
@app.callback(
    Output(component_id='volume-table', component_property= 'children'),
    Input(component_id='intraday-value', component_property= 'data'),
    Input(component_id='url', component_property= 'pathname')           
)
def update_table_volume(data, relative_pathname):
    #print(data)
    data_dic = {'nombre':data[0], 'Volume':data[1]}
    data_table = pd.DataFrame(data_dic)   
    data_table['Volume'] = data_table['Volume'].apply(lambda x: '{:,.0f}'.format(x) )    
    children = html.Div([
        dash_table.DataTable(
                id='table',        
                columns=[{"name": i, "id": i} for i in data_table.columns],
                data=data_table.to_dict('records'),
                style_cell_conditional=[
                        {
                        'if': {'column_id': 'nombre'},
                        'textAlign': 'left'
                        }
                        ],
                style_header={
                        'backgroundColor': 'grey',
                        'fontWeight': 'bold'
                        },
                ),        
        ])
    return children

#######################################
#######################################
@app.callback(
    Output('ultima-actualizacion', 'children'),    
    Input('url', 'pathname'))
def display_page(relative_pathname):
    texto = 'Última Actualización {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return html.Div(texto, style={'color': 'gray', 'fontSize': 12} )   


### fin callback

if __name__=='__main__':
    app.run_server(debug = False)

    

