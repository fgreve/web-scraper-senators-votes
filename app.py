import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from models_app import votaciones, voto, tabla_votacion, dict_tem, df_resultado_votacion, tabla_boletin_votos, \
    df_senador, df_voto, tabla_voto_senador

from extractor import url_vote, get_boletin

from aux_app import buscador_tema, tabla_votaciones_2, termometro, panel

titulo_app = "Buscador de Votaciones del Senado de Chile"
cabecera = html.Div([
    html.H1(children=[
        titulo_app,
        # html.A(
        #     html.Img(
        #         src="assets/dash-logo.png",
        #         style={'float': 'right', 'height': '50px'}
        #     ), href="https://dash.plot.ly/"),
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
        html.Div([
            dcc.Loading(
                type="default",
                fullscreen=False,
                children=tabla_votaciones_2
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
    [Output('voto-selector', 'data')],
    [Input('id-buscar-tema-input', 'value')])
def update_table(palabra_filtrada):
    print(" ----- update_table ------------------- ")
    df = votaciones()
    dff = df[df.apply(lambda row: row.str.contains(palabra_filtrada, regex=False).any(), axis=1)]
    return [dff.to_dict('records')]


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
    row = tabla_votos[voto_elegido[0]]
    print(" ----- get_votacion ------------------- ")
    print("voto_elegido: ", voto_elegido)
    print("row: ", row)

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


@app.callback(
    [Output(component_id='voto-out', component_property='data')],
    [Input(component_id='id-termometro-titulo', component_property='children')])
def get_panel(voto_input):
    voto_id = voto_input.split(": ")[1]
    voto_table = tabla_votacion(str(voto_id))
    return [voto_table.to_dict('records')]


if __name__ == "__main__":
    app.run_server(debug=True)
