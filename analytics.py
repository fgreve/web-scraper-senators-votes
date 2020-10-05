import pandas as pd
import unidecode
import os
from extractor import get_boletin, get_vote


def df_voto():
    df = df_vote()

    def get_voto(row):
        for c in ["si", "no", "abs", "par"]:
            if row[c] == 1:
                return c

    df["voto"] = df.apply(get_voto, axis=1)
    df = df[["senador_id", "voto_id", "voto"]]

    return df


def df_vote():
    """ nombre, si, no, abs, par, vote, senador, partido, bloque, date, voto """

    path = "../data/"
    file = "votes.csv"
    path_file = os.path.join(path, file)
    df = pd.read_csv(path_file)

    df.columns = ["nombre", "si", "no", "abs", "par", "vote"]
    nombres = df["nombre"]

    senadores = []
    for nombre in nombres:
        senadores.append(
            unidecode.unidecode(nombre).strip().replace(".", "").replace(",", "").replace(" ", "_").lower())

    df["senador_id"] = senadores

    df['voto_id'] = df['vote'].astype(str)

    senadores = df_senador()
    vote = df_resultado_votacion()

    df = pd.merge(df, senadores[['senador_id', 'partido', 'bloque']], on='senador_id', how='left')
    df = pd.merge(df, vote[['voto_id', 'date']], on='voto_id', how='left')

    def get_voto(row):
        for c in ["si", "no", "abs", "par"]:
            if row[c] == 1:
                return c

    df["voto"] = df.apply(get_voto, axis=1)
    df = df.drop(['vote'], axis=1)

    return df


def df_resultado_votacion():
    """ voto_id, date, boletin, si, no, abs, par, ses_id """

    df = get_vote()

    df['Fecha'] = df['Fecha'].str.split(" ", n=1, expand=True)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')

    df.columns = ["voto_id", "date", "boletin", "si", "no", "abs", "par", "ses_id"]
    df['voto_id'] = df['voto_id'].astype(str)
    df['ses_id'] = df['ses_id'].astype(str)

    df["date"] = df["date"].dt.date
    df = df.sort_values('date', ascending=False)

    return df


def df_senador():
    """ 'senador_id', 'partido', 'bloque', senador_nombre' """

    path = "../data/"
    file = "df_senador.csv"
    path_file = os.path.join(path, file)
    df = pd.read_csv(path_file)

    return df


def df_votos_bloque():
    votes = df_vote()
    votes = votes[["voto_id", "bloque", "si", "no", "abs", "par"]]

    df = votes.groupby(['voto_id', 'bloque'])[["si", "no", "abs", "par"]].sum()
    return df


def filter_voto_bloque(vote_id, bloque_id, mayoria=False):
    voto_bloque = df_votos_bloque()

    voto_bloque_filtrado = voto_bloque.loc[(vote_id, bloque_id)]

    if mayoria:
        voto_bloque_ordenado = voto_bloque_filtrado.sort_values(ascending=False)
        voto_bloque_mayor = voto_bloque_ordenado.index[0]

        return voto_bloque_mayor

    return voto_bloque_filtrado


def series_senator_votes(senador):
    votes = df_vote()
    votes.index = votes["senador_id"]

    votes_filter = votes.loc[senador]
    votes_filter = votes_filter[["voto_id", "si", "no", "abs", "par"]]

    df = votes_filter.groupby('voto_id')[["si", "no", "abs", "par"]].sum()

    def get_voto(row):
        for c in df.columns:
            if row[c] == 1:
                return c

    votes_filter_1_column = df.apply(get_voto, axis=1)

    return votes_filter_1_column


def series_bloque_votos(bloque_id):

    df = df_votos_bloque()

    voto_bloque_filtrado = df.xs(bloque_id, level=1, drop_level=True)

    def get_vote_max(row):
        votes = max(row["si"], row["no"], row["abs"], row["par"])
        for c in df.columns:
            if row[c] == votes:
                return c

    df2 = voto_bloque_filtrado.apply(get_vote_max, axis=1)

    return df2


def filter_senador_bloque(senador):
    senadores_df = df_senador()
    senadores_df.index = senadores_df["senador_id"]
    filtro = senadores_df.loc[senador]

    bloque = filtro["bloque"]

    return bloque


def df_alineado(senador_id):
    """ 'senador', 'bloque', 'alineado' """

    serie_votos_senador = series_senator_votes(senador_id)
    serie_votos_senador_df = pd.DataFrame(serie_votos_senador, columns=['senador'])

    bloque = filter_senador_bloque(senador_id)

    serie_votos_bloque = series_bloque_votos(bloque)
    serie_votos_bloque_df = pd.DataFrame(serie_votos_bloque, columns=['bloque'])

    df = pd.merge(serie_votos_senador_df, serie_votos_bloque_df, on='voto_id', how='left')

    cond = df.senador == df.senador

    df["alineado"] = "no"
    df.loc[cond, "alineado"] = "si"

    df_no_alineado = df[df['alineado'] == 'no']

    return df


def dict_tem():
    path = "../data/"
    file = "tem.txt"
    path_file = os.path.join(path, file)

    tem = dict()

    fh = open(path_file, "r", encoding='latin-1')
    for line in fh:
        voto_id = line.split(" || ")[0].strip()
        tem_text = line.split(" || ")[1].strip()
        tem[voto_id] = tem_text

    fh.close()

    return tem


def porcentaje_alineado(senador_id):
    df = df_alineado(senador_id)
    print(df.head())

    n_inasistencias = df[df['senador'].isnull()].shape[0]
    print("n_inasistencias: ", n_inasistencias)

    n_votaciones = df.shape[0]
    print("n_votaciones: ", n_votaciones)

    n_alineado = df[df.alineado == "si"].shape[0]
    print("n_alineado: ", n_alineado)

    porcentaje_alineacion = n_alineado / (n_votaciones - n_inasistencias) * 100
    print("porcentaje_alineacion: ", porcentaje_alineacion)

    return porcentaje_alineacion


def df_boletin():
    path = "../data/analytics/"
    file = "boletines.csv"
    path_file = os.path.join(path, file)
    df = pd.read_csv(path_file)
    return df


def main():
    senador_id = "allamand_z_andres"

    votaciones_df = df_voto()
    print(votaciones_df.head())


if __name__ == "__main__":
    main()
