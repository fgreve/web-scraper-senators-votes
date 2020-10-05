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

from models_app import votaciones, voto, tabla_votacion, dict_tem, df_resultado_votacion, tabla_boletin_votos, \
    df_senador, df_voto, tabla_voto_senador
from extractor import url_vote, get_boletin

# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(__name__)

# Colors
bgcolor = "#f3f3f1"  # mapbox light map land color
bar_bgcolor = "#b0bec5"  # material blue-gray 200
bar_unselected_color = "#78909c"  # material blue-gray 400
bar_color = "#546e7a"  # material blue-gray 600
bar_selected_color = "#37474f"  # material blue-gray 800
bar_unselected_opacity = 0.8

color_nueva_mayoria = "#E35B34"
color_chile_vamos = "#0094c2"

# Figure template
row_heights = [150, 500, 300]
template = {'layout': {'paper_bgcolor': bgcolor, 'plot_bgcolor': bgcolor}}


def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        'data': [],
        'layout': {
            'height': height,
            'template': template,
            'xaxis': {'visible': False},
            'yaxis': {'visible': False},
        }
    }


# lista_senadores = ["Todos"].extend(list(df_senador()["senador_nombre"])[0])
# print(lista_senadores)

titulo_app = "Buscador votos Senador"
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

buscador_senador = html.Div(
    [
        html.H4([
            "Senador",
            html.Img(
                id='id-buscar-senador',
                src="assets/question-circle-solid.svg",
                n_clicks=0,
                className='info-icon',
            ),
        ], className="container_title"),

        dcc.Dropdown(
            id='id-buscar-senador-input',
            options=[
                {"label": i, "value": i} for i in list(df_senador()["senador_nombre"])
            ],
            value=[]
        )
    ]
)

buscador_tema = html.Div(
    [
        html.H4([
            "Tema",
            html.Img(
                id='id-buscar-tema',
                src="assets/question-circle-solid.svg",
                n_clicks=0,
                className='info-icon',
            ),
        ], className="container_title"),

        dcc.Input(value='', id='id-buscar-tema-input', placeholder='Filter', debounce=True),
    ]
)

votaciones_card = html.Div(
    [
        # dbc.Row(html.H3("Tabla votaciones", className="card-title", id="id-senador-name")),
        html.H4([
            "Resultado de la votación",
        ], className="container_title",
            id='id-senador-name'),

        dash_table.DataTable(
            css=[{'selector': '.row', 'rule': 'margin: 0'}],
            id='voto-senador',

            columns=[
                {"name": i, "id": i} for i in ["voto_id", "date", "voto", "tem", "boletin"]
            ],
            data=votaciones().to_dict('records'),

            row_selectable="single",
            selected_rows=[0],

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
                 'width': '5%'},
                {'if': {'column_id': 'boletin'},
                 'width': '7%'},
                {'if': {'column_id': 'voto'},
                 'width': '5%'},
                {'if': {'column_id': 'partido'},
                 'width': '7%'},
                {'if': {'column_id': 'bloque'},
                 'width': '10%'},
                {'if': {'column_id': 'senador_nombre'},
                 'width': '10%'},
            ]
        ),
    ]
)

# dbc.Row(
#     [
#         dbc.Col(
#             dbc.Jumbotron(
#                 [
#                     html.H5("Tema de la votación"),
#                     html.P("Tem", className="card-text", id="id-tem"),
#                 ],
#             ), width=7
#         ),
#         dbc.Col(
#             dbc.Jumbotron(
#                 [
#                     html.H5("Boletín"),
#                     html.P("Boletin", className="card-text", id="id-boletin"),
#                 ],
#             ), width=5
#         )
#     ]
# ),

termometro = html.Div([
    html.H4("Votación", className="container_title", id="id-votacion"),

    html.Div([
        html.Div([
            html.H5("-", id="id-si"),
            html.P("Apruebo")
        ], className='three columns pretty_cajita'),

        html.Div([
            html.H5("-", id="id-no"),
            html.P("Rechazo")
        ], className='three columns pretty_cajita'),

        html.Div([
            html.H5("-", id="id-abs"),
            html.P("Abstención")
        ], className='three columns pretty_cajita'),
        html.Div([
            html.H5("-", id="id-par"),
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
            size=400,
            max=100,
            value=100
        )
    )
]),

panel = dbc.Card(
    [

        html.H2("Votación por Senador", className="container_title"),

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
                    'backgroundColor': color_nueva_mayoria,
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{bloque_si} = "chile_vamos"',
                        'column_id': 'si'
                    },
                    'backgroundColor': color_chile_vamos,
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{bloque_no} = "nueva_mayoria"',
                        'column_id': 'no'
                    },
                    'backgroundColor': color_nueva_mayoria,
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{bloque_no} = "chile_vamos"',
                        'column_id': 'no'
                    },
                    'backgroundColor': color_chile_vamos,
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{bloque_abspar} = "nueva_mayoria"',
                        'column_id': 'abspar'
                    },
                    'backgroundColor': color_nueva_mayoria,
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{bloque_abspar} = "chile_vamos"',
                        'column_id': 'abspar'
                    },
                    'backgroundColor': color_chile_vamos,
                    'color': 'white'
                }
            ]
        ),
        html.Div(dbc.Button("Sitio del Senado", color="primary", id="tem-url", target="_blank"))
    ]
)

layout = html.Div([
    html.Div(cabecera),
    html.Div([
        html.Div(buscador_senador,
                 className='three columns pretty_container'),

        html.Div(buscador_tema,
                 className='three columns pretty_container'),

        html.Div([
            dcc.Loading(
                type="default",
                fullscreen=False,
                children=termometro
            )
        ], className='six columns pretty_container'),

    ], className='row_flex'),

    html.Div([
        html.Div([
            dcc.Loading(
                type="default",
                fullscreen=False,
                children=votaciones_card
            )
        ], className='six columns pretty_container'),

        html.Div([
            dcc.Loading(
                type="default",
                fullscreen=False,
                children=panel
            )
        ], className='six columns pretty_container'),

    ], className='row')
])

app.layout = layout


@app.callback(
    [Output('voto-senador', 'data'),
     # Output('id-partido', 'children'),
     # Output('id-bloque', 'children'),
     Output('id-senador-name', 'children')],
    [Input('id-buscar-senador-input', 'value'),
     Input('id-buscar-tema-input', 'value')])
def update_table(senador_filtrado, tema_filtrado):
    print(" ----- update_table ------------------- ")
    print("senador_filtrado: ", senador_filtrado)
    print("tema_filtrado: ", tema_filtrado)

    df_votaciones_senador = tabla_voto_senador(senador_filtrado)

    df_votaciones_senador = df_votaciones_senador[
        df_votaciones_senador.apply(lambda row: row.str.contains(tema_filtrado, regex=False).any(), axis=1)]

    partido = df_votaciones_senador.partido[0]
    bloque = df_votaciones_senador.bloque[0]

    return df_votaciones_senador.to_dict('records'), 'Votaciones Senador {}'.format(senador_filtrado)


# partido, bloque,

@app.callback(
    [Output('id-no', 'children'),
     Output('id-abs', 'children'),
     Output('id-par', 'children'),
     Output('id-si', 'children'),
     # Output('id-tem', 'children'),
     Output('tem-url', 'href'),
     Output('id-termometro', 'color'),
     Output('id-termometro', 'max'),
     # Output('id-boletin', 'children'),
     Output('id-votacion', 'children')],
    [Input(component_id='voto-senador', component_property='data'),
     Input(component_id='voto-senador', component_property='selected_rows')])
def get_votacion(tabla_votos, voto_elegido):
    row = tabla_votos[voto_elegido[0]]
    print(" ----- get_votacion ------------------- ")
    print(row)

    voto_id = str(row["voto_id"])
    no = row["no"]
    abst = row["abs"]
    par = row["par"]
    si = row["si"]
    tem = row["tem"]

    boletin_id = row["boletin"]
    print("boletin_id: ", boletin_id)

    if boletin_id is None:
        boletin = "No exite informacion del Boletín"
    else:
        try:
            boletin = get_boletin()[get_boletin().boletin == boletin_id]["titulo"].values[0]
        except:
            boletin = "No exite informacion del Boletín"

    print("boletin: ", boletin)

    maximo = si + no + par + abst
    color = {"ranges": {"green": [0, si], "red": [si, si + no], "yellow": [si + no, maximo]}}

    url = url_vote(str(voto_id))

    return no, abst, par, si, url, color, maximo, 'Resultado de la votación: {}'.format(voto_id)


# return no, abst, par, si, tem, url, color, maximo, boletin, 'Votación: {}'.format(voto_id)


@app.callback(
    [Output(component_id='voto-out', component_property='data')],
    [Input(component_id='id-votacion', component_property='children')])
def get_panel(voto_input):
    voto_id = voto_input.split(": ")[1]
    voto_table = tabla_votacion(str(voto_id))
    return [voto_table.to_dict('records')]


if __name__ == "__main__":
    app.run_server(debug=True, port=8000)
