import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
from datetime import datetime as dt
import re
import dash_table
import pandas as pd
import dash_daq as daq

from models_app import votaciones, voto, tabla_votacion, dict_tem, df_resultado_votacion, tabla_boletin_votos
from extractor import url_vote, get_boletin

from aux_app import tabla_votaciones

path = "../data/analytics/"
file = "boletines.csv"
path_file = os.path.join(path, file)
df_boletin = pd.read_csv(path_file)

df = votaciones()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

titulo_app = "Buscador de votaciones del Senado"
cabecera = html.Div(
    [
        html.H1(children=[
            titulo_app,
            html.A(
                html.Img(
                    src="assets/dash-logo.png",
                    style={'float': 'right', 'height': '50px'}
                ), href="https://dash.plot.ly/"),
        ], style={'text-align': 'left'}),
    ]),

tabla_votaciones = tabla_votaciones

control = html.Div(
    [
        html.H4("Votación", className="container_title", id="id-votacion"),

        dash_table.DataTable(
            css=[{'selector': '.row', 'rule': 'margin: 0'}],
            id='voto-selector',
            # data=[],
            columns=[
                {"name": i, "id": i} for i in ["date", "voto_id", "tem", "boletin"]
            ],
            data=df.to_dict('records'),

            row_selectable="single",
            # selected_rows=[0],

            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },

            style_cell={
                'textAlign': 'left',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0
            },

            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },

            filter_action="native",
            sort_action="native",
            sort_mode='multi',

            page_size=10,

            # 'height': '550px',
            style_table={
                'overflowY': 'hidden',
                'minWidth': '100%'},

            style_cell_conditional=[
                {'if': {'column_id': 'date'},
                 'width': '10%'},
                {'if': {'column_id': 'voto_id'},
                 'width': '7%'},
                {'if': {'column_id': 'boletin'},
                 'width': '7%'},
            ]
        ),
    ]
)

panel = html.Div(
    [
        dash_table.DataTable(
            css=[{'selector': '.row', 'rule': 'margin: 0'}],
            id='voto-out',
            data=[],
            columns=[
                {"name": i, "id": i} for i in ["si", "no", "abspar"]
            ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },

            style_cell={
                'textAlign': 'center',
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                'height': 'auto'
            },

            style_table={'overflowY': 'hidden'},

            style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{bloque_si} = "nueva_mayoria"',
                        'column_id': 'si'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{bloque_si} = "chile_vamos"',
                        'column_id': 'si'
                    },
                    'backgroundColor': '#0074D9',
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{bloque_no} = "nueva_mayoria"',
                        'column_id': 'no'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{bloque_no} = "chile_vamos"',
                        'column_id': 'no'
                    },
                    'backgroundColor': '#0074D9',
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{bloque_abspar} = "nueva_mayoria"',
                        'column_id': 'abspar'
                    },
                    'backgroundColor': '#FF4136',
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{bloque_abspar} = "chile_vamos"',
                        'column_id': 'abspar'
                    },
                    'backgroundColor': '#0074D9',
                    'color': 'white'
                }
            ]
        )
    ]
)

tem_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Tema", className="card-title"),
            html.P("Tem", className="card-title", id="id-tem"),
            dbc.Button("Sitio del Senado", color="primary", id="tem-url"),
        ]
    )
)

# no_card = dbc.Card(
#     dbc.CardBody(
#         [
#             html.H5("No", className="card-title", id="col-no"),
#             html.P("Rechazo"),
#         ]
#     )
# )
# abs_card = dbc.Card(
#     dbc.CardBody(
#         [
#             html.H5("Abs", className="card-title", id="col-abs"),
#             html.P("Abstencion"),
#         ]
#     )
# )
# par_card = dbc.Card(
#     dbc.CardBody(
#         [
#             html.H5("Par", className="card-title", id="col-par"),
#             html.P("Pareo"),
#         ]
#     )
# )
# si_card = dbc.Card([
#     dbc.CardBody(
#         [
#             html.H5("Si", className="card-title", id="col-si"),
#             html.P("Apruebo"),
#         ]
#     )], color="warning"
# )

buscador = html.Div(
    [
        html.H5("Buscar por tema de votación", className="card-title", id="buscador"),
        dcc.Input(value='', id='filter-input', placeholder='Filter', debounce=True),
    ]
)

votacion_detalle_card = html.Div([
    html.H4("Votación", className="container_title"),  # , id="id-votacion"

    html.Div([
        html.Div([
            html.H5("Si", id="id-si"),
            html.P("Apruebo")
        ], className='three columns pretty_cajita'),

        html.Div([
            html.H5("No", id="id-no"),
            html.P("Rechazo")
        ], className='three columns pretty_cajita'),

        html.Div([
            html.H5("Abs", id="id-abs"),
            html.P("Abstención")
        ], className='three columns pretty_cajita'),
        html.Div([
            html.H5("Par", id="id-par"),
            html.P("Pareo")
        ], className='three columns pretty_cajita')
    ]),

    # dbc.Col(
    #     dbc.Button("Sitio del Senado", color="primary", id="tem-url", target="_blank"),
    #     width=2
    # )

    html.Div(
        daq.GraduatedBar(
            id='id-termometro',
            color={"ranges": {"green": [0, 60], "red": [60, 90], "yellow": [90, 100]}},
            # showCurrentValue=True,
            size=600,
            max=100,
            value=100
        )
    )
]),

layout = html.Div([
    html.Div(cabecera),

    html.Div([
        html.Div([
            html.Div([
                html.Div(buscador, className='three columns pretty_container'),
                html.Div("three columns pretty_container", className='three columns pretty_container')
            ], className="row"),
            html.Div(control, className='six columns pretty_container')
        ]),

        html.Div([
            html.Div(tem_card, className='six columns pretty_container'),

            html.Div(children=[
                html.Div(votacion_detalle_card),
                html.Div(panel)
            ], className='five columns pretty_container')
        ])
    ])
])

app.layout = layout


@app.callback(
    Output('voto-selector', 'data'),
    [Input('filter-input', 'value')])
def update_table(filter_string):
    dff = df[df.apply(lambda row: row.str.contains(filter_string, regex=False).any(), axis=1)]
    return dff.to_dict('records')


@app.callback(
    [Output(component_id='voto-out', component_property='data'),
     Output('id-no', 'children'),
     Output('id-abs', 'children'),
     Output('id-par', 'children'),
     Output('id-si', 'children'),
     Output('id-tem', 'children'),
     Output('tem-url', 'href')],
    [Input(component_id='voto-selector', component_property='selected_rows')])
def get_votacion(selected_rows):
    dff = df
    row = dff.iloc[selected_rows[0]]
    voto_id = row["voto_id"]
    no = row["no"]
    abst = row["abs"]
    par = row["par"]
    si = row["si"]

    tem_dict = dict_tem()
    tem = tem_dict[str(voto_id)]
    url = url_vote(str(voto_id))

    voto_table = tabla_votacion(str(voto_id))

    return voto_table.to_dict('records'), no, abst, par, si, tem, url


if __name__ == "__main__":
    app.run_server(debug=True, port=8000)
