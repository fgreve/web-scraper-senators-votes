import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_daq as daq

from extractor import url_vote, get_boletin
from models_app import votaciones
# from analytics import df_boletin

ultimo_voto = "7914"

bgcolor = "#f3f3f1"  # mapbox light map land color
bar_bgcolor = "#b0bec5"  # material blue-gray 200
bar_unselected_color = "#78909c"  # material blue-gray 400
bar_color = "#546e7a"  # material blue-gray 600
bar_selected_color = "#37474f"  # material blue-gray 800
bar_unselected_opacity = 0.8

color_nueva_mayoria = "#E35B34"
color_chile_vamos = "#0094c2"

tabla_votaciones = html.Div(
    [
        dash_table.DataTable(
            css=[{'selector': '.row', 'rule': 'margin: 0'}],
            id='boletin-selector',
            columns=[
                {"name": i, "id": i} for i in get_boletin().keys()
            ],
            data=get_boletin().to_dict('records'),

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

tabla_votaciones_2 = html.Div(
    [
        html.H4("Votación", className="container_title", id="id-votacion"),

        dash_table.DataTable(
            css=[{'selector': '.row', 'rule': 'margin: 0'}],
            id='voto-selector',
            columns=[
                {"name": i, "id": i} for i in ["date", "voto_id", "tem", "boletin"]
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

            page_size=5,

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
                 'width': '10%'},
            ]
        ),
    ]
)

tabla_votaciones_3 = html.Div(
    [
        html.H4("Votación", className="container_title", id="id-votacion"),

        dash_table.DataTable(
            css=[{'selector': '.row', 'rule': 'margin: 0'}],
            id='voto-selector',
            columns=[
                {"name": i, "id": i} for i in ["date", "voto_id", "tem", "boletin"]
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
                 'width': '7%'},
                {'if': {'column_id': 'boletin'},
                 'width': '10%'},
            ]
        ),
    ]
)


control_boletin = html.Div(
    [
        html.H4("Proyectos", className="container_title", id="id-boletin"),

        dash_table.DataTable(
            css=[{'selector': '.row', 'rule': 'margin: 0'}],
            id='boletin-selector',
            columns=[
                {"name": i, "id": i} for i in ["date", "boletin", "titulo"]
            ],
            data=get_boletin().to_dict('records'),

            row_selectable="single",
            selected_rows=[8],
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

buscador_tema = html.Div(
    [
        html.H4([
            "Tema (buscar por palabra clave)",
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

termometro = html.Div([
    html.H4("Votación", className="container_title", id="id-termometro-titulo"),

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

panel = html.Div(
    [
        html.Div([
            html.Div(html.H2("Resultado de la Votación", className="container_title"),
                     className='six columns pretty_cajita'
                     ),
            html.Div(dbc.Button("Sitio del Senado", color="secondary", id="tem-url", target="_blank")
                     )
        ]),

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
    ]
)

votaciones_card = html.Div(
    [
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
