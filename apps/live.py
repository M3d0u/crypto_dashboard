import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from pycoingecko import CoinGeckoAPI
import plotly.graph_objs as go
from datetime import datetime
from app import app

#Connexion et Récupération des infos via l'API
cg = CoinGeckoAPI()
all_infos = cg.get_coins_markets(vs_currency = 'USD')

list_nom = []
for i in range(51):
    list_nom.append(all_infos[i]['name'])

list_logo = []
for i in range(51):
    list_logo.append(all_infos[i]['image'])

#Création d'un dictionnaire contenant toutes les listes 
dict_crypto = {}
for i in range (51):
    dict_crypto[list_nom[i]] = []

#Création de la liste pour l'axe des abscisses
list_x = []

def update_data(crypto):
    #On récupère l'id du crypto
    index = list_nom.index(crypto)

    #On va chercher son id et on récup le prix via l'API
    id_crypt = all_infos[index]['id']
    prix = cg.get_price(ids = id_crypt, vs_currencies = 'usd')
    dict_crypto[crypto].append(prix[id_crypt]['usd'])
    list_x.append(datetime.today().strftime('%H:%M:%S'))
    return list_x, dict_crypto[crypto]

layout = html.Div([html.H3("Follow the live evolution of cryptos", style={"text-transform":"uppercase", 'font-weight':'bold'}),

    html.Hr(),

    html.P(['Choose one or more cryptos :']),

    dcc.Dropdown(
        id='dropdown_crypto',
        options = [{'label': i, 'value': i} for i in list_nom],
        value = 'Bitcoin',
        multi = True
    ), 

    dbc.Row(
                [
                    dbc.Col(children=html.Div(id='images'), width=2),
                    dbc.Col(children=html.Div(id='graphs'), width=10)
                ]
        ),

    dcc.Interval(
    id='interval_component', 
    interval= 10000,
    n_intervals=0
    )
])

@app.callback(
    Output(component_id='graphs', component_property='children'),
    Output(component_id='images', component_property='children'),
    [Input(component_id='dropdown_crypto', component_property='value'),
    Input(component_id='interval_component',component_property='n_intervals')]
)

def update_graph(CryptoChoosen, n_interval):
    #Si un élement sélectionné, il apparait comme un str, donc on le met dans une liste
    if type(CryptoChoosen) == str:
        CryptoChoosen = [CryptoChoosen]

    graphs = []
    images = []

    for crypto in CryptoChoosen:
        #Update des données
        update_data(crypto)

        #Update phots
        index = list_nom.index(crypto)
        image = html.Div(html.Img(src=list_logo[index]), style={'margin-top':'160px'})
        images.append(image)

        #Updates du graph
        data = go.Scatter(
            x = list_x,
            y = dict_crypto[crypto],
            fill='tozeroy',
            marker= dict(
            color='#3F8EFC'
            ),
            fillcolor='#6eb5dd'
        )

        graphs.append(html.Div(dcc.Graph(
            id=crypto,
            animate=True,
            figure={'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(list_x),max(list_x)]),
                                                        yaxis=dict(range=[min(dict_crypto[crypto])-(0.05*max(dict_crypto[crypto])),max(dict_crypto[crypto])+(0.05*max(dict_crypto[crypto]))]),
                                                        title='{} (in $)'.format(crypto)
          )}) ))
            

    return graphs, images