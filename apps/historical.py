import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from pycoingecko import CoinGeckoAPI
from datetime import datetime
import plotly.graph_objs as go
from dash.dependencies import Input, Output
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

#Création d'un dictionnaire contenant toutes les dates par crypto (fourchette différente pour chaque) 
dict_date = {}
for i in range (51):
    dict_date[list_nom[i]] = []

#Les dates sont au format UNIX, on utilise datetime pour les convertir en format lisible
def date_convertor(unix):
  date = datetime.utcfromtimestamp(unix/1000).strftime('%Y-%m-%d')
  return date

def get_data(crypto):
    #On récupère l'id du crypto
    index = list_nom.index(crypto)

    #On va chercher son id et on récup l'histo des prix/dates via l'API
    id_crypt = all_infos[index]['id']
    histo_data = cg.get_coin_market_chart_by_id(id = id_crypt, vs_currency = 'USD', days = 'max', interval = 'daily')
    for i in range(len(histo_data['market_caps'])):
        #Prix
        dict_crypto[crypto].append(histo_data['prices'][i][1])
        #Date
        dict_date[crypto].append(date_convertor(histo_data['prices'][i][0]))

    return dict_date[crypto], dict_crypto[crypto]

layout = html.Div([html.H3("Get the historical evolution of cryptos", style={"text-transform":"uppercase", 'font-weight':'bold'}),

    html.Hr(),

    html.P(['Choose one or more cryptos :']),

    dcc.Dropdown(
        id='dropdown_crypto',
        options = [{'label': i, 'value': i} for i in list_nom],
        value = 'Bitcoin',
        multi = True
    ), 

    dbc.Row(
                [dbc.Col(children=html.Div(id='images_2'), width=2),
                dbc.Col(children=html.Div(id='graphs_2'), width=10)]
        )
])

@app.callback(
    Output(component_id='graphs_2', component_property='children'),
    Output(component_id='images_2', component_property='children'),
    [Input(component_id='dropdown_crypto', component_property='value')]
)

def update_graph(CryptoChoosen):
    #Si un élement sélectionné, il apparait comme un str, donc on le met dans une liste
    if type(CryptoChoosen) == str:
        CryptoChoosen = [CryptoChoosen]

    graphs = []
    images = []

    for crypto in CryptoChoosen:
        #Update des données
        get_data(crypto)

        #Update photos
        index = list_nom.index(crypto)
        image = html.Img(src=list_logo[index], style={'margin-top':'160px'})
        images.append(image)

        #Get first date for the title
        date_datetime = datetime.strptime(dict_date[crypto][0], '%Y-%m-%d')
        date = date_datetime.strftime('%b %Y')
        #Update graphs
                #Updates du graph
        data = go.Scatter(
            x = dict_date[crypto],
            y = dict_crypto[crypto],
            fill='tozeroy',
            marker= dict(
            color='#3F8EFC'
            ),
            fillcolor='#6eb5dd'
        )

        graphs.append(dcc.Graph(
            id=crypto,
            animate=True,
            figure={'data': [data],'layout' : go.Layout(title='{} (in $) since {}'.format(crypto,  date)) } ))
    
    return graphs, images