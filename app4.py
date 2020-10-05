import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from models_app import votaciones, voto, tabla_votacion, dict_tem, df_resultado_votacion, tabla_boletin_votos, \
    df_senador, df_voto, tabla_voto_senador

from extractor import url_vote, get_boletin
from aux_app import buscador_tema, tabla_votaciones_3, termometro, panel, control_boletin
from analytics import df_boletin

titulo_app = "Buscador de Votaciones del Senado de Chile"
cabecera = html.Div([
    html.H1(children=[
        titulo_app,
    ], style={'text-align': 'center'}),
]),

app = dash.Dash(__name__)
server = app.server  # the Flask app

layout = html.Div([
    html.Div(cabecera),

    html.Div([
        html.Div(buscador_tema,
                 className='twelve columns pretty_container'),
    ], className='row_flex'),

    html.Div([
        html.Div(control_boletin,
                 className='twelve columns pretty_container'),
    ], className='row_flex'),

    html.Div([
        html.Div([
            dcc.Loading(
                type="default",
                fullscreen=False,
                children=tabla_votaciones_3
            )
        ], className='twelve columns pretty_container'),
    ], className='row'),

    html.Div([
        html.Div([
            dcc.Loading(
                type="default",
                fullscreen=False,
                children=termometro
            )
        ], className='twelve columns pretty_container'),
    ], className='row_flex'),

    html.Div([
        html.Div([
            dcc.Loading(
                type="default",
                fullscreen=False,
                children=panel
            )
        ], className='twelve columns pretty_container'),
    ], className='row')

])

app.layout = layout


@app.callback(
    [Output('boletin-selector', 'data')],
    [Input('id-buscar-tema-input', 'value')])
def update_table(palabra_filtrada):
    df = get_boletin()
    dff = df[df.apply(lambda row: row.str.contains(palabra_filtrada, regex=False).any(), axis=1)]
    return [dff.to_dict('records')]


@app.callback(
    [Output(component_id='voto-selector', component_property='data')],
    [Input(component_id='boletin-selector', component_property='selected_rows')])
def get_boletin_votos(selected_rows):
    dff_boletin = get_boletin()
    row = dff_boletin.iloc[selected_rows[0]]
    boletin = str(row["boletin"])
    print(" --------- get_boletin_votos() ---------- ")
    print(boletin)

    df = votaciones()
    # df = df[df.boletin == "13678-06"]
    df = df[df.boletin == boletin]
    print(df)
    return [df.to_dict('records')]


@app.callback(
    [Output('id-no', 'children'),
     Output('id-abs', 'children'),
     Output('id-par', 'children'),
     Output('id-si', 'children'),
     Output('tem-url', 'href'),
     Output('id-termometro', 'color'),
     Output('id-termometro', 'max'),
     Output('id-termometro-titulo', 'children')],
    [Input('voto-selector', 'data'),
     Input('voto-selector', 'selected_rows')])
def get_votacion(tabla_votos, voto_elegido):
    try:
        row = tabla_votos[voto_elegido[0]]

        voto_id = str(row["voto_id"])
        no = row["no"]
        abst = row["abs"]
        par = row["par"]
        si = row["si"]
        tem = row["tem"]

        boletin_id = row["boletin"]

    except IndexError:
        row = 'null'
        boletin_id = None

    if boletin_id is None:
        boletin = "No exite informacion del Boletín"
    else:
        try:
            boletin = get_boletin()[get_boletin().boletin == boletin_id]["titulo"].values[0]
        except:
            boletin = "No exite informacion del Boletín"

    # print("boletin: ", boletin)

    maximo = si + no + par + abst
    color = {"ranges": {"green": [0, si], "red": [si, si + no], "yellow": [si + no, maximo]}}

    url = url_vote(str(voto_id))

    return no, abst, par, si, url, color, maximo, 'Resultado de la votación: {}'.format(voto_id)


@app.callback(
    [Output(component_id='voto-out', component_property='data')],
    [Input(component_id='id-termometro-titulo', component_property='children')])
def get_panel(voto_input):
    voto_id = voto_input.split(": ")[1]
    voto_table = tabla_votacion(str(voto_id))
    return [voto_table.to_dict('records')]


if __name__ == "__main__":
    app.run_server(debug=True)
