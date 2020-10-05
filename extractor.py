import urllib
import urllib.request
from bs4 import BeautifulSoup
import json
import datetime
import os
import os.path
from scraper_api import ScraperAPIClient
import pandas as pd
import io
from unidecode import unidecode
from shutil import copyfile
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from dotenv import load_dotenv

load_dotenv()


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


def boletin():
    path = "../data/analytics/"
    file = "boletines.csv"
    path_file = os.path.join(path, file)
    df = pd.read_csv(path_file)
    return df


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


def make_soup(url, scraper_api=False):
    """ takes an url and returns a soup """
    if scraper_api:
        client = ScraperAPIClient(os.environ.get("SCRAPER_API"))
        page = client.get(url=url).text
        soup = BeautifulSoup(page, "html.parser")
    else:
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, "html.parser")
    return soup


def extract_html(url, scraper_api=False):
    """ takes an url and returns a text """
    if scraper_api:
        client = ScraperAPIClient(os.environ.get("SCRAPER_API"))
        page = client.get(url=url).text
    else:
        page = urllib.request.urlopen(url).text
    return page


def extract_ses(leg_iid):
    """ takes url and returns a ses_iid list and a dict with the text """

    file = "../data/leg-html/leg-" + str(leg_iid) + ".html"

    with open(file, "r") as f:
        contents = f.read()

    soup = BeautifulSoup(contents, 'lxml')

    ses_tab = soup.find("select", {"name": "sesionessala"})

    ses_date = []

    for row in ses_tab.findAll('option'):
        ses_date.append(row.text)

    ses_tab_options = []

    for row in ses_tab.findAll('option'):
        ses_tab_options.append(row['value'])

    ses_tab_options = ses_tab_options[1:]
    ses_date = ses_date[1:]

    dict_text = dict()
    i = 0
    for ses in ses_tab_options:
        dict_text[ses] = ses_date[i]
        i = i + 1

    return ses_tab_options, dict_text


def extract_leg(url, scraper_api=False):
    """ takes url and returns 4 lists with legs's characteristics """

    soup = make_soup(url, scraper_api)
    leg_tab = soup.find("select", {"name": "legislaturas"})

    leg = []
    for row in leg_tab.findAll('option'):
        leg.append(row.text[:3])

    leg_tab_options = []
    for row in leg_tab.findAll('option'):
        leg_tab_options.append(row['value'])

    date_1 = []
    date_2 = []
    for row in leg_tab.findAll('option'):
        date_1.append(row.text.split("(", 1)[1].split(" -", 1)[0])
        date_2.append(row.text.split("- ", 1)[1].split(")", 1)[0])

    return leg_tab_options, leg, date_1, date_2


def make_leg(url, scraper_api=False):
    """ takes an url and save a file into ../data/leg/ + current_date with the 4 lists with legs's characteristics """

    list1, list2, list3, list4 = extract_leg(url, scraper_api)
    elements = zip(list1, list2, list3, list4)

    d = datetime.datetime.now()
    current_date = d.strftime('%Y-%m-%d')
    file_name = 'leg-' + current_date + ".csv"
    path = "../data/leg/" + file_name

    my_file = open(path, 'w')

    for ele1, ele2, ele3, ele4 in elements:
        my_file.write(ele1)
        my_file.write(",")
        my_file.write(ele2)
        my_file.write(",")
        my_file.write(ele3)
        my_file.write(",")
        my_file.write(ele4)

        my_file.write('\n')

    my_file.close()

    return list1, list2, list3, list4


def extract_vote(url, links=False, scraper_api=False):
    """ takes an url and returns a list of votes's id: vota_id"""
    soup = make_soup(url, scraper_api)

    list_ver = soup.find_all(string="Ver Votación")

    votes = []
    if links:
        for x in list_ver:
            votes.append("https://www.senado.cl/appsenado/" + x.find_parents("a")[0].get('href'))

    else:
        for x in list_ver:
            votes.append(x.find_parents("a")[0].get('href').split("=")[-1])

    return votes


def url_ses(leg_iid, ses_iid):
    """ returns ses url (if ses_iid = 0, it works too) """
    dom = "https://www.senado.cl/appsenado/index.php?mo=sesionessala&ac=votacionSala&legiini=361&legiid="
    url = dom + leg_iid + "&sesiid=" + ses_iid
    return url


def url_vote(vote_id):
    """ returns the url of the votes """
    dom = "https://www.senado.cl/appsenado/index.php?mo=sesionessala&ac=detalleVotacion&votaid="
    url = dom + vote_id
    return url


def url_leg(leg_iid):
    url = url_ses(str(leg_iid), "0")
    return url


def make_vote_html(vote_id, scraper_api=False):
    """ make a file in ../data/vote-html/ """
    url = url_vote(vote_id)
    page = extract_html(url, scraper_api)

    path = "../data/vote-html/" + "vote-" + vote_id + ".html"

    with open(path, 'w') as f:
        f.write(page)


def make_ses_html(leg_iid, ses_iid, scraper_api=False):
    """ make a file in ../data/ses-html/ """
    url = url_ses(leg_iid, ses_iid)
    page = extract_html(url, scraper_api)

    path = "../data/ses-html/" + "ses-" + str(ses_iid) + ".html"

    with open(path, 'w') as f:
        f.write(page)


def make_leg_html(leg_iid, scraper_api=False):
    """ make a file in ../data/ses-html/ """
    url = url_leg(leg_iid)
    page = extract_html(url, scraper_api)

    path = "../data/leg-html/" + "leg-" + str(leg_iid) + ".html"

    with open(path, 'w') as f:
        f.write(page)


def make_vote_folder(vote_id):
    """ takes vote_id and create a folder in ../data/votes-folder/ """
    file = "../data/vote-html/vote-" + vote_id + ".html"
    with open(file, "r") as f:
        contents = f.read()

    soup = BeautifulSoup(contents, 'lxml')
    text = soup.find("div", {"class": "auxi-art"}) \
        .find("div", {"class": "col1"}) \
        .text.splitlines()

    ses_tem = text[1]
    ses = ses_tem.split(":", 1)[1].split("Tema:", 1)[0]
    tem = ses_tem.split("Tema:", 1)[1]

    tab = soup.find("div", {"class": "auxi-art"}) \
        .find("div", {"class": "col1"}) \
        .find("table")

    rows = tab.find_all("tr")

    votes = []
    names = []
    for col in rows[0].find_all("th"):
        names.append(col.text)

    votes.append(names)

    for row in rows[1:]:
        cols = []
        senator = row.find_all("td")[0].text
        cols.append(senator)

        for col in row.find_all("td")[1:]:
            if col.find("img") is None:
                cols.append(0)
            else:
                cols.append(1)

        votes.append(cols)

    path = "../data/vote-folder/vote-" + vote_id

    if os.path.exists(path):
        words = "folder for vote " + vote_id + " already exists"
        return print(words)

    os.mkdir(path)
    path = "../data/vote-folder/vote-" + vote_id + "/" + "ses.txt"
    my_file = open(path, 'w')
    my_file.write(ses)
    my_file.close()

    path = "../data/vote-folder/vote-" + vote_id + "/" + "tem.txt"
    my_file = open(path, 'w')
    my_file.write(tem)
    my_file.close()

    path = "../data/vote-folder/vote-" + vote_id + "/vote-" + vote_id + ".csv"
    votes_df = pd.DataFrame(votes)
    votes_df.to_csv(path, index=False, header=False)


def make_ses_vote(ses_iid):
    """ returns a csv file in ../data/ses-vote/ from a html file in /data/ses-html/ """
    file = "ses-" + ses_iid + ".html"
    path = "../data/ses-html/"
    file_path = path + file

    with open(file_path, "r") as f:
        contents = f.read()

    soup = BeautifulSoup(contents, 'lxml')

    list_ver = soup.find_all(string="Ver Votación")
    votes_num = len(list_ver)

    votes = []
    for x in list_ver:
        votes.append(x.find_parents("a")[0].get('href').split("=")[-1])

    tabla = soup.find("table", {"class": "clase_tabla"})

    rows = tabla.find_all("tr")
    rows_num = len(rows)

    names = []
    for col in rows[0].find_all("th"):
        names.append(col.text)

    data = []
    data.append(names)
    j = 1
    for x in range(rows_num):
        if j % 4 == 0:
            row = []
            for i in rows[x].find_all("td"):
                row.append(i.text)

            data.append(row)
        j = j + 1

    votes.insert(0, "vote_id")

    i = 0
    for row in data:
        row.insert(0, votes[i])
        i = i + 1

    for row in data:
        print(row)

    data_df = pd.DataFrame(data)

    file = "ses-" + ses_iid + ".csv"
    path = "../data/ses-vote/"
    file_path = path + file

    data_df.to_csv(file_path, index=False, header=False)


# hay q arreglar esta wea
def make_sess():
    """ generates sess file in ../data/sess/ """
    legs = get_legs()
    legs = list(legs[0])

    names = ["leg", "ses", "text"]

    data = [names]
    for leg in legs:
        sess, dict_text = extract_ses(leg)

        for ses in sess:
            row = [leg, ses, dict_text[ses]]
            data.append(row)
            print(row)

    d = datetime.datetime.now()
    current_date = d.strftime('%Y-%m-%d')

    path = "../data/sess/"
    file = 'sess-' + current_date + ".csv"
    path_file = os.path.join(path, file)

    df = pd.DataFrame(data[1:])
    df.columns = ["leg", "ses", "text"]
    print(df.head())

    texts = df['text'].values

    dates_sp = []
    dates = []
    for text in texts:
        date_sp = text.split("en ")[1]
        dates_sp.append(date_sp)
        date = get_date(date_sp)
        dates.append(date)
        print(date_sp)
        print(date)

    df["date_sp"] = dates_sp
    df["date"] = dates

    df.to_csv(path_file, index=False, header=True)

    path = "../data/sess/"
    file = 'sess-' + current_date + ".csv"
    source_path = os.path.join(path, file)

    path = "../data/"
    file = "sess.csv"
    destination_path = os.path.join(path, file)

    copyfile(source_path, destination_path)


# def make_sess():
#     folder_files = os.listdir("../data/vote-folder/")
#     votes = []
#     for folder in folder_files:
#         votes.append(folder.split("-")[1])
#
#     path = "../data/vote-folder/" + folder_files[0] + "/"
#     file = "vote-" + str(votes[0]) + ".csv"
#     path_file = os.path.join(path, file)
#
#     data = pd.read_csv(path_file)
#     data["vote"] = str(votes[0])
#
#     for vote in votes[1:]:
#         print(vote)
#         path = "../data/vote-folder/" + "vote-" + str(vote) + "/"
#         file = "vote-" + str(vote) + ".csv"
#         path_file = os.path.join(path, file)
#
#         df = pd.read_csv(path_file)
#         df["vote"] = vote
#
#         data = data.append(df, ignore_index=True)
#
#     d = datetime.datetime.now()
#     current_date = d.strftime('%Y-%m-%d')
#     file = 'votes-' + current_date + ".csv"
#     path = "../data/votes/"
#     path_file = os.path.join(path, file)
#     data.to_csv(path_file, index=False, header=True)
#
#     path_file = "../data/votes.csv"
#     data.to_csv(path_file, index=False, header=True)


def get_date(date_sp):
    """ generates a date 21-7-2020 from Martes 21 de Julio de 2020 """
    day = date_sp.split()[1]
    year = date_sp.split()[-1]

    month_sp = date_sp.split("de")[1].replace(" ", "")

    month = {"Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
             "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12}

    date = year + "-" + str(month[month_sp]) + "-" + day
    return date


def make_vote():
    """ retorna /data/vote.csv """
    path = "../data/ses-vote/"
    files = os.listdir(path)

    data = pd.read_csv(path + files[0])

    ses = files[0].split("-")[1].split(".")[0]
    data["ses"] = ses

    for file in files[1:]:
        df = pd.read_csv(path + file)
        print(df.head())
        ses = file.split("-")[1].split(".")[0]
        df["ses"] = ses
        data = data.append(df, ignore_index=True)

    d = datetime.datetime.now()
    current_date = d.strftime('%Y-%m-%d')
    file = 'vote-' + current_date + ".csv"
    path = "../data/vote/"
    path_file = os.path.join(path, file)
    data.to_csv(path_file, index=False, header=True)

    path = "../data/vote.csv"
    data.to_csv(path, index=False, header=True)


def make_votes():
    folder_files = os.listdir("../data/vote-folder/")
    votes = []
    for folder in folder_files:
        votes.append(folder.split("-")[1])

    path = "../data/vote-folder/" + folder_files[0] + "/"
    file = "vote-" + str(votes[0]) + ".csv"
    path_file = os.path.join(path, file)

    data = pd.read_csv(path_file)
    data["vote"] = str(votes[0])

    for vote in votes[1:]:
        print(vote)
        path = "../data/vote-folder/" + "vote-" + str(vote) + "/"
        file = "vote-" + str(vote) + ".csv"
        path_file = os.path.join(path, file)

        df = pd.read_csv(path_file)
        df["vote"] = vote

        data = data.append(df, ignore_index=True)

    d = datetime.datetime.now()
    current_date = d.strftime('%Y-%m-%d')
    file = 'votes-' + current_date + ".csv"
    path = "../data/votes/"
    path_file = os.path.join(path, file)
    data.to_csv(path_file, index=False, header=True)

    path_file = "../data/votes.csv"
    data.to_csv(path_file, index=False, header=True)


def make_ses():
    def append_new_line(file_name, text_to_append):
        """Append given text as a new line at the end of file"""
        # Open the file in append & read mode ('a+')
        with open(file_name, "a+") as file_object:
            # Move read cursor to the start of file.
            file_object.seek(0)
            # If file is not empty then append '\n'
            data = file_object.read(100)
            if len(data) > 0:
                file_object.write("\n")
            # Append text at the end of file
            file_object.write(text_to_append)

    path = "../data/"
    file = "vote.csv"
    path_file = os.path.join(path, file)
    vote_df = pd.read_csv(path_file)

    votes = vote_df["vote_id"].values

    d = datetime.datetime.now()
    current_date = d.strftime('%Y-%m-%d')
    file = 'ses-' + current_date + ".txt"
    path = "../data/ses/"
    path_file = os.path.join(path, file)

    if os.path.isfile(path_file):
        os.remove(path_file)

    for vote in votes:
        print(vote)

        path = "../data/vote-folder/" + "vote-" + str(vote) + "/"
        file = "ses.txt"
        path_file = os.path.join(path, file)

        with io.open(path_file, 'rt') as my_file:
            tem_text = my_file.read()

        ses = str(vote) + " || " + tem_text
        print(ses)

        file = 'ses-' + current_date + ".txt"
        path = "../data/ses/"
        path_file = os.path.join(path, file)
        append_new_line(path_file, ses)

    file = 'ses-' + current_date + ".txt"
    path = "../data/ses/"
    source_path = os.path.join(path, file)

    path = "../data/"
    file = "ses.txt"
    destination_path = os.path.join(path, file)

    copyfile(source_path, destination_path)


def make_tem():
    def append_new_line(file_name, text_to_append):
        """Append given text as a new line at the end of file"""
        # Open the file in append & read mode ('a+')
        with open(file_name, "a+") as file_object:
            # Move read cursor to the start of file.
            file_object.seek(0)
            # If file is not empty then append '\n'
            data = file_object.read(100)
            if len(data) > 0:
                file_object.write("\n")
            # Append text at the end of file
            file_object.write(text_to_append)

    vote_df = get_vote()
    votes = vote_df["vote_id"].values

    d = datetime.datetime.now()
    current_date = d.strftime('%Y-%m-%d')
    file = 'tem-' + current_date + ".txt"
    path = "../data/tem/"
    path_file = os.path.join(path, file)

    if os.path.isfile(path_file):
        os.remove(path_file)

    carpetas_faltantes = []
    for vote in votes:
        print(vote)

        path = "../data/vote-folder/" + "vote-" + str(vote) + "/"
        file = "tem.txt"
        path_file = os.path.join(path, file)

        try:
            with io.open(path_file, 'rt') as my_file:
                tem_text = my_file.read()

            tem = str(vote) + " || " + tem_text
            print(tem)

            file = 'tem-' + current_date + ".txt"
            path = "../data/tem/"
            path_file = os.path.join(path, file)
            append_new_line(path_file, tem)

        except IOError:
            print("No hay carpeta: ", str(vote))
            carpetas_faltantes.append(vote)

    file = 'tem-' + current_date + ".txt"
    path = "../data/tem/"
    source_path = os.path.join(path, file)

    path = "../data/"
    file = "tem.txt"
    destination_path = os.path.join(path, file)
    copyfile(source_path, destination_path)
    print(carpetas_faltantes)


def make_boletin_html_to_csv(file):
    """ [used in make_boletin()] returns a df from a html file in ../data/boletines-html/ """
    path = "../data/boletines-html/"
    path_file = os.path.join(path, file)

    with open(path_file, "r", encoding="utf-8") as f:
        contents = f.read()

    soup = BeautifulSoup(contents, 'html.parser')
    tables = soup.find_all("table")

    tabla = []
    for table in tables:
        head = table.find("thead")
        tab_table = []
        if head is not None:
            ths = head.find("tr").find_all("th")

            row = []
            for th in ths:
                row.append(th.text)
            tab_table.append(row)

            body = table.find("tbody")
            tds = body.find_all("tr")

            for td in tds:
                td_boletin = td.find("td", {"class": "td_boletin"})
                if td_boletin is not None:
                    print("---------------------------------------------------")
                    print(td_boletin.contents[0])
                    rows = td_boletin.parent.find_all("td")
                    linea = []
                    for row in rows:
                        content = row.contents[0]
                        linea.append(content)
                    tabla.append(linea)

    return tabla


def make_boletin():
    """ build boletin.csv from files in ../data/boletines-html/ """
    path = "../data/boletines-html/"

    file = "grid.xlsx"
    path_file = os.path.join(path, file)
    grid = pd.read_excel(path_file)
    grid = grid.drop_duplicates('N° Boletín')
    grid.columns = ['date', 'boletin', 'titulo', 'estado']

    file = "grid_1.xlsx"
    path_file = os.path.join(path, file)
    grid_1 = pd.read_excel(path_file)
    grid_1 = grid_1.drop_duplicates('N° Boletín')
    grid_1.columns = ['date', 'boletin', 'titulo', 'estado']

    file = "grid_2.xlsx"
    path_file = os.path.join(path, file)
    grid_2 = pd.read_excel(path_file)
    grid_2 = grid_2.drop_duplicates('N° Boletín')
    grid_2.columns = ['date', 'boletin', 'titulo', 'estado']

    file = "grid_3.xlsx"
    path_file = os.path.join(path, file)
    grid_3 = pd.read_excel(path_file)
    grid_3 = grid_3.drop_duplicates('Boletín')
    grid_3 = grid_3.drop('Ley', axis=1)
    grid_3.columns = ['boletin', 'titulo', 'estado', 'date']
    grid_3 = grid_3[['date', 'boletin', 'titulo', 'estado']]

    frames = [grid, grid_1, grid_2, grid_3]
    result = pd.concat(frames)
    result = result[["date", "boletin", "titulo"]]

    from glob import glob
    path_files = glob('*.html')

    for path_file in path_files:
        boletines = make_boletin_html_to_csv(path_file)

        tabla_df = pd.DataFrame(boletines)
        tabla_df.columns = ["boletin", "titulo", "blanco", "estado", "fecha_ingreso"]
        tabla_df = tabla_df[["fecha_ingreso", "boletin", "titulo", "estado"]]
        tabla_df.columns = ["date", "boletin", "titulo", "estado"]
        tabla_df = tabla_df.drop_duplicates('boletin')
        tabla_df = tabla_df[["date", "boletin", "titulo"]]

        frames = [result, tabla_df]
        result = pd.concat(frames)

    def get_date_from_fecha(date_sp):
        """ generates a date 21-7-2020 from: Martes 21 de Julio, 2020 """
        day = date_sp.split()[1]
        year = date_sp.split()[-1]
        month_sp = date_sp.split()[3].replace(",", "")

        month = {"Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04", "Mayo": "05", "Junio": "06",
                 "Julio": "07", "Agosto": "08", "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"}

        if len(day) == 1:
            day = "0" + day

        date = day + "/" + str(month[month_sp]) + "/" + year
        return date

    df1 = pd.read_csv(os.path.join("../data/boletines-html/", "boletin.csv"))
    df2 = pd.read_csv(os.path.join("../data/boletines-html/", "boletines_new2.csv"))
    df = pd.concat([df1, df2], axis='rows')
    df['date'] = df['date'].apply(get_date_from_fecha)

    df = pd.concat([result, df], axis='rows')

    path = "../data/boletin/"
    files = os.listdir(path)
    df1 = pd.read_csv(os.path.join(path, files[0]))
    for file in files[1:]:
        df0 = pd.read_csv(os.path.join(path, file))
        df1 = pd.concat([df1, df0], axis='rows')
    df1['date'] = df1['date'].apply(get_date_from_fecha)

    df = pd.concat([df, df1], axis='rows')

    path = "../data/"
    file = "boletin.csv"
    path_file = os.path.join(path, file)
    df.to_csv(path_file, index=False, encoding="utf-8", header=True)


def get_sess():
    """ returns the sess from /data/sess/ as df """

    path = "../data/sess/"
    file_list = os.listdir(path)

    date_list = []
    for file in file_list:
        date_list.append(file.split("-", 1)[1].split(".")[0])

    date_list = sorted(date_list)
    date = date_list[-1]
    print("la ultima fecha es: ", date)

    file_path = path + "sess-" + date + ".csv"
    df = pd.read_csv(file_path, parse_dates=True)

    df['leg'] = df['leg'].astype(str)
    df['ses'] = df['ses'].astype(str)

    return df


def get_legs():
    """ returns the list of legs from /data/leg/ as data frame """
    path = "../data/leg/"
    file_list = os.listdir(path)

    date_list = []
    for file in file_list:
        date_list.append(file.split("-", 1)[1].split(".")[0])

    date_list = sorted(date_list)
    date = date_list[-1]

    file_path = path + "leg-" + date + ".csv"
    df = pd.read_csv(file_path, header=None, parse_dates=True)

    return df


def get_leg_last():
    legs = get_legs()

    legs[2] = pd.to_datetime(legs[2])
    legs[3] = pd.to_datetime(legs[3])

    legs = legs.sort_values(by=3, ascending=False)

    last_leg = str(legs.loc[0, 0])

    return last_leg


def get_sess_from_leg(leg_iid):
    """ returns a df with sess from leg_iid """
    sess = get_sess()
    sess.index = sess["leg"]
    return sess.loc[leg_iid]


def get_boletin():
    """ returns the boletin.csv as df """
    path = "../data/"
    file = "boletin.csv"
    path_file = os.path.join(path, file)
    df = pd.read_csv(path_file)
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df


def get_vote():
    """ returns the vote.csv as df """
    path = "../data/"
    file = "vote.csv"
    path_file = os.path.join(path, file)

    df = pd.read_csv(path_file)
    df['vote_id'] = df['vote_id'].astype(str)

    return df


class ExtractBoletinBot:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=%s" % "1920,1080")
        self.driver = webdriver.Chrome(executable_path='../chromedriver.exe',
                                       options=chrome_options)

    def open_site(self, boletin_id):
        self.driver.get("http://www.senado.cl/appsenado/templates/tramitacion/index.php?boletin_ini=" + str(boletin_id))
        sleep(10)
        close_popup_btn = self.driver.find_element_by_xpath('//*[@id="modalTramites"]/div/div/div[1]/button')
        close_popup_btn.click()
        titulo = self.driver.find_element_by_xpath('//*[@id="div_box"]/table/tbody/tr[1]/td[2]').text
        date = self.driver.find_element_by_xpath('//*[@id="div_box"]/table/tbody/tr[2]/td[2]').text

        self.driver.close()

        return titulo, date


def extract_boletin():
    """ utiliza la class ExtractBoletinBot para comparar los boltines en voto y en boletin.csv y extrae la diferencia """
    path = "../data/boletin/"
    file = "boletin.csv"
    path_file = os.path.join(path, file)
    boletin_ok = pd.read_csv(path_file)

    boletines_en_boletin = set(boletin()["boletin"].unique()).union(set(boletin_ok.boletin))
    boletines_en_votaciones = set(votaciones()["boletin"].dropna())
    boletines_faltantes = boletines_en_votaciones - boletines_en_boletin
    print(len(boletines_faltantes))

    faltan = []
    for boletin_id in list(boletines_faltantes):
        # boletin_id = "13678-06"
        try:
            bot = ExtractBoletinBot()
            titulo, date = bot.open_site(boletin_id)

            print("date", " | ", "titulo", " | ", "boletin")
            print(date, " | ", titulo, " | ", boletin_id)

            bol = []
            head = ["date", "boletin", "titulo"]
            row = [date, boletin_id, titulo]
            bol.append(head)
            bol.append(row)

            path = "../data/boletin/"
            file = str(boletin_id) + ".csv"
            path_file = os.path.join(path, file)
            votes_df = pd.DataFrame(bol)
            print(votes_df)
            votes_df.to_csv(path_file, index=False, header=False)

        except:
            print("Boletin no encontrado: ", boletin_id)
            faltan.append(boletin_id)

    print("faltan: ", faltan)


def main():
    # make_boletin()


    df = votaciones()
    df = df[df.boletin == "13678-06"]
    print(df)



if __name__ == "__main__":
    main()
