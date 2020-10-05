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

from models_app import votaciones, voto, tabla_votacion, dict_tem, df_resultado_votacion, tabla_boletin_votos
from extractor import url_vote, get_boletin


path = "../data/analytics/"
file = "boletines.csv"
path_file = os.path.join(path, file)
df_boletin = pd.read_csv(path_file)

df = votaciones()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# app = dash.Dash(
#     __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
# )
# server = app.server

control_boletin = html.Div(
    [
        dash_table.DataTable(
            css=[{'selector': '.row', 'rule': 'margin: 0'}],
            id='boletin-selector',
            columns=[
                {"name": i, "id": i} for i in df_boletin.keys()
            ],
            data=df_boletin.to_dict('records'),

            row_selectable="single",
            # selected_rows=[],
            # [0],
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
                {'if': {'column_id': 'boletin'},
                 'width': '7%'},
                {'if': {'column_id': 'estado'},
                 'width': '13%'},
                {'if': {'column_id': 'votaciones'},
                 'width': '10%'},
            ]
        )
    ]
)

control = html.Div(
    [
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

cabecera = html.Div(
    [
        dbc.Row(
            [
                # dbc.Col(
                #     html.Img(
                #         src=app.get_asset_url("dash-logo.png"),
                #         id="plotly-image",
                #         style={
                #             "height": "60px",
                #             "width": "auto",
                #             "margin-bottom": "25px",
                #         },
                #     ), width=3
                # ),
                dbc.Col(
                    html.Div(
                        html.H1("Buscador de votaciones del Senado",
                                style={"margin-bottom": "0px"},
                                )
                    ), width=12
                    # html.Div(
                    #     html.H5("tracker de votaciones",
                    #             style={"margin-top": "0px"}
                    #             )
                    # )
                )
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

no_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("No", className="card-title", id="col-no"),
            html.P("Votaciones de rechazo"),
        ]
    )
)
abs_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Abs", className="card-title", id="col-abs"),
            html.P("Votaciones de abstencion"),
        ]
    )
)
par_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Par", className="card-title", id="col-par"),
            html.P("Votaciones de pareo"),
        ]
    )
)
si_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Si", className="card-title", id="col-si"),
            html.P("Votaciones de apruebo"),
        ]
    )
)

# app.layout
app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(cabecera, width=12)),
        dbc.Row(dbc.Col(control_boletin, width=12)),
        dbc.Row(dbc.Col(control, width=12)),

        dbc.Row([
            dbc.Col(tem_card, width=12)
        ]),

        dbc.Row([
            dbc.Col(si_card, width=4),
            dbc.Col(no_card, width=4),
            dbc.Col(abs_card, width=2),
            dbc.Col(par_card, width=2)
        ]),

        dbc.Row(dbc.Col(panel, width=12)),

    ],
)


@app.callback(
    [Output(component_id='voto-selector', component_property='data')],
    [Input(component_id='boletin-selector', component_property='selected_rows')])
def get_boletin_votos(selected_rows):
    dff_boletin = df_boletin
    row = dff_boletin.iloc[selected_rows[0]]
    boletin = row["boletin"]

    boletin_votos = tabla_boletin_votos(boletin)

    return [boletin_votos.to_dict('records')]


@app.callback(
    [Output(component_id='voto-out', component_property='data'),
     Output('col-no', 'children'),
     Output('col-abs', 'children'),
     Output('col-par', 'children'),
     Output('col-si', 'children'),
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
    app.run_server(debug=True)
