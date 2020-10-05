import pandas as pd
from analytics import df_senador, df_resultado_votacion, dict_tem, df_voto
from extractor import get_boletin
import os


def votaciones():
    resultado_votacion = df_resultado_votacion()
    resultado_votacion.index = resultado_votacion["voto_id"]

    tem = dict_tem()
    tem = pd.DataFrame.from_dict(tem, orient='index', columns=['tem'])
    tem.index.name = 'voto_id'

    df = pd.merge(tem, resultado_votacion, left_index=True, right_index=True)
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = pd.to_datetime(df['date']).dt.date
    df = df.sort_values('date', ascending=False)
    df = df[["date", "voto_id", "si", "no", "abs", "par", "tem", "boletin"]]

    return df


def voto(voto_id):
    voto = df_voto()
    voto = voto[voto.voto_id == voto_id]
    voto.index = voto.senador_id

    senador = df_senador()
    senador.index = senador.senador_id
    df = pd.merge(voto, senador, left_index=True, right_index=True, how='left')
    df = df[["voto_id", "voto", "partido", "bloque", "senador_nombre"]]

    return df


def dict_bloque_senadores():
    df = df_senador()
    df = df[["senador_nombre", "bloque"]]
    df = df.reset_index(drop=True)

    list_senadores_nueva_mayoria = list(df[df.bloque == "nueva_mayoria"]["senador_nombre"])
    list_senadores_chile_vamos = list(df[df.bloque == "chile_vamos"]["senador_nombre"])

    dict_bloque_senado = dict()
    dict_bloque_senado["nueva_mayoria"] = list_senadores_nueva_mayoria
    dict_bloque_senado["chile_vamos"] = list_senadores_chile_vamos

    return dict_bloque_senado


def tabla_votacion(voto_id):
    voto_df = voto(voto_id)
    voto_df = voto_df[["senador_nombre", "voto"]]
    voto_df = voto_df.reset_index(drop=True)
    # print(voto_df)

    voto_si = voto_df[voto_df.voto == "si"]["senador_nombre"].values
    voto_no = voto_df[voto_df.voto == "no"]["senador_nombre"].values
    voto_abspar = voto_df[(voto_df.voto == "abs") | (voto_df.voto == "par")]["senador_nombre"].values
    largo = max(len(voto_si), len(voto_no), len(voto_abspar))

    # print(voto_abspar)

    list_si = []
    list_no = []
    list_abspar = []
    for x in range(0, largo - 1):
        if x <= len(voto_si) - 1:
            si = voto_si[x]
        else:
            si = ""
        if x <= len(voto_no) - 1:
            no = voto_no[x]
        else:
            no = ""
        if x <= len(voto_abspar) - 1:
            abspar = voto_abspar[x]
        else:
            abspar = ""

        list_si.append(si)
        list_no.append(no)
        list_abspar.append(abspar)

    # print(list_abspar)

    senadores_df = df_senador()
    senadores_df.index = senadores_df["senador_nombre"]

    def get_bloque(senador_nombre):
        if not senador_nombre:
            return ""
        filtro = senadores_df.loc[senador_nombre]
        bloque_senador = filtro["bloque"]
        return bloque_senador

    list_si_bloque = []
    for senador in list_si:
        bloque = get_bloque(senador)
        list_si_bloque.append(bloque)

    list_no_bloque = []
    for senador in list_no:
        bloque = get_bloque(senador)
        list_no_bloque.append(bloque)

    list_abspar_bloque = []
    for senador in list_abspar:
        bloque = get_bloque(senador)
        list_abspar_bloque.append(bloque)

    # print(len(list_no_bloque), len(list_si_bloque), len(list_abspar_bloque))

    voto_table = pd.DataFrame(list(zip(list_si, list_no, list_abspar, list_si_bloque, list_no_bloque, list_abspar_bloque)),
                              columns=["si", "no", "abspar", "bloque_si", "bloque_no", "bloque_abspar"])

    return voto_table


def tabla_boletin_votos(boletin):

    votaciones_df = df_resultado_votacion().sort_values(by='date', ascending=False)
    votaciones_df = votaciones_df[votaciones_df.boletin == boletin]
    votaciones_df = votaciones_df.sort_values(by='date', ascending=False)

    votos = votaciones_df["voto_id"].values.tolist()

    df = votaciones()

    dff = df[df["voto_id"].isin(votos)]

    return dff


def make_boletines_analytics():
    df = get_boletin()
    boletines = df["boletin"].values
    print(boletines)

    cantidades = []
    for boletin in boletines:
        boletin_votes = tabla_boletin_votos(boletin)

        cantidad = len(boletin_votes)
        print(cantidad)
        cantidades.append(cantidad)

    df["votaciones"] = cantidades

    print(df.head())

    path = "../data/analytics/"
    file = "boletines.csv"
    path_file = os.path.join(path, file)
    df.to_csv(path_file, index=False, encoding="utf-8", header=True)


def tabla_voto_senador(input_value):
    senador = df_senador()
    senador.index = senador.senador_id

    voto_df = df_voto()

    if input_value == "Todos":
        votos_senador = voto_df
    else:
        senador_index = senador[senador.senador_nombre == input_value]["senador_id"].values[0]
        votos_senador = voto_df[voto_df["senador_id"] == senador_index]

    votos_senador.index = votos_senador.senador_id

    votos_senador = pd.merge(votos_senador, senador, left_index=True, right_index=True, how='left')

    votos_senador = votos_senador.drop(columns='senador_id_y')
    votos_senador.columns = ["senador_id", "voto_id", "voto", "partido", "bloque", "senador_nombre"]

    votos_senador.index = votos_senador.voto_id

    votaciones_df = votaciones()
    votaciones_df.index = votaciones_df.voto_id

    votaciones_df = pd.merge(votos_senador, votaciones_df, left_index=True, right_index=True, how='left')
    votaciones_df = votaciones_df.drop(columns='voto_id_y')
    votaciones_df = votaciones_df.rename(columns={"voto_id_x": "voto_id"})

    votaciones_df = votaciones_df.sort_values('date', ascending=False)

    return votaciones_df


def main():
    input_value = "Allamand Z., Andrés"
    # input_value = "Todos"
    df = tabla_voto_senador(input_value)
    # print(df.head())

    # print(df.shape)

    lista_senadores = list(["Todos"].extend(list(df_senador()["senador_nombre"])[0]))
    print(lista_senadores)


if __name__ == "__main__":
    main()
