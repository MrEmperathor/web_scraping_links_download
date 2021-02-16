from bs4 import BeautifulSoup
import requests
from requests.utils import requote_uri
import json
import os
import re
import fnmatch
from tmdbv3api import TMDb
from tmdbv3api import Movie
from requests.utils import requote_uri

tmdb = TMDb()
tmdb.api_key = 'be58b29465062a3b093bc17dacef8bf3'
tmdb.language = 'es'
tmdb.debug = True
movie = Movie()

combi_mi = ['a','A','b','B','c','C','d','D','e','E','f','F','g','G','h','H','i','I','j','J','k','K','l','L','m','M','n','N','o','O','p','P','q','Q','r','R','s','S','t','T','u','U','v','V','w','W','x','X','y','Y','z','Z']

def ResultadoBusquedaPaginaPeli(name):

    base = 'https://pelisenhd.net/?s='
    url = requote_uri(base + name)
    try:

        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        search = soup.find_all('div', class_='result-item')
        search = str(search).strip("['']")
        search2 = BeautifulSoup(search, 'html.parser')
        url_peli_buscada = search2.find_all('a',href=True)[0].get('href')

        page = requests.get(url_peli_buscada)
        soup = BeautifulSoup(page.content, 'html.parser')
        search = soup.find_all('fieldset')
        search = str(search).strip("['']")
        search2 = BeautifulSoup(search, 'html.parser')
        titulo_original = search2.find_all('p')
        data = {}
        data_final = {}
        dlist = list()
        flist = ''
        i0 = 0
        i1 = 1
        #la variable titulo_original es una lista en donde estan todos los datos, los itero cada uno
        for i in titulo_original:
            print(i.text)
            flist += i.text.replace('|',':') + ':'
            dlist.append(i.text)
        # dlist = flist.split(':')
        # for j in range(0, len(dlist),2):
        #     if len(dlist[j]) > 1 and len(dlist[i1]) > 1: data[dlist[j].strip()] = dlist[i1].strip()
        #     i1 += 2 

        data = dict(map(lambda x: x.split(':', 1), dlist))
        # print(data)
        # print()
        # print(dlist)
        for k in data:
            if 'Audio' in k:
                if 'Latino' in data[k]: 
                    data_final['audio'] = 'LATINO' 
                else: 
                    data_final['audio'] = data[k]
        
        data_final['titulo'] = data['Titulo Original']
        data_final_fial = dict(data_final,**data)
        # print(data_final)
        return data_final_fial
    except: 
        return False

#buscar nombre original
def BuscarIdTmdb(titulo,year):

    if titulo: 
        print('datos a buscar: {}'.format(titulo))
        search = movie.search(titulo)

        for res in search:
            # print(res.id)
            # print(res.title)
            # print(res.overview)
            # print(res.poster_path)
            # print(res.vote_average)
            # print(res.release_date)

            yea = res.release_date[0:4]
            try:
                if yea == year: 
                    miId = res.id
                    # return miId
                    print(res.id)
                    break
                else:
                    return res.id
            except:
                return res.id
    else:
        return False


#comprobar enlaces si estan activos
def comprobarEnlaces(link):
    try:

        if 'uptobox.com' in link:
            page = requests.get(link)
            soup = BeautifulSoup(page.content, 'html.parser')
            titulo = soup.find_all('h1')[0].text.strip()
            if titulo == "File not found" or titulo == "Archivo no encontrado":
                return False
            else:
                return link
        elif 'drive.google.com' in link:
            regex = "([\w-]){33}|([\w-]){19}"
            match = re.search(regex,link)
            url_edit = 'https://drive.google.com/u/0/uc?id='+match[0]+'&export=download'

            page = requests.get(url_edit)
            soup = BeautifulSoup(page.content, 'html.parser')
            titulo = soup.find_all('title')[0].text.strip()
            if titulo == 'Google Drive - Quota exceeded':
                return False
            else:
                return link
        elif 'megaup.net' in link:
            return False
        elif '1fichier.com' in link:
            return False
        elif 'userscloud.com' in link:
            return False
        elif 'mediafire.com' in link:
            page = requests.get(link)
            soup = BeautifulSoup(page.content, 'html.parser')
            titulo = soup.find_all('div', class_='dl-btn-label')[0].text.strip()
            if titulo: return link
        elif 'mega.nz' in link:
            page = requests.get(link)
            soup = BeautifulSoup(page.content, 'html.parser')
            titulo = soup.find_all('meta',content=True)[0].get('content')
            if 'GB file' in titulo: return link
        else: 
            return False
    except:
        return False

serie = input('LETRA EN SERIE: ')
base_url = 'https://hdpastes.com/?v='
i = 0
lista_url = list()
lista_urls = list()



while True:
    # print(base_url + serie + combi_mi[i])
    paste_url = base_url + serie + combi_mi[i]
    lista_url.append(paste_url)
    if combi_mi[i] == 'Z': break
    i += 1
print(lista_url)


for url in lista_url:
    link_descarga = list()
    json_url = {}

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # href = soup.find_all('a', class_='btn-class')
    
    try:
        titulo = soup.find_all('h3')[0].text.strip()
        for href in soup.find_all('a',href=True):
            hr = href.get('href')
            if 'https' in hr: link_descarga.append(href.get('href'))
        linkk = link_descarga
        json_url['nombre'] = titulo
        json_url['links'] = [url, linkk]
        lista_urls.append(json_url)
    except:
        print('NO SE ENCONTRO TITULO PARA LA URL: ' + url)
    # print(json.dumps(json_url, indent=2))

    # print(link_descarga)
    print(titulo)
print(json.dumps(lista_urls, indent=2))
guardar = json.dumps(lista_urls, indent=2)
file = open("enlacess_paste.json", "w")
file.write(str(guardar) + os.linesep)
# file.write("Segunda línea")
file.close()

with open('enlacess_paste.json') as file:
    data = json.load(file)
#crear n archivo de texto para almacenar los comandos
file = open("comandos.txt", "w")
for i in data:
    print(i['nombre'])

    link_uptobox = fnmatch.filter(i['links'][1],'*uptobox.com*')
    print(link_uptobox)
    if link_uptobox: 
        str_link = str(link_uptobox).strip("['']")
        posicion_up = link_uptobox.index(str_link)
        if str_link in link_uptobox:
            enlace_final = comprobarEnlaces(link_uptobox[posicion_up])
        else:
            enlace_final = False
    else:
        enlace_final = False
    if 'enlace_final' in globals() and enlace_final is not False: 
        enlace_final = enlace_final
    else: 
        for t in i['links'][1]:
            salida_comp_enlace = comprobarEnlaces(t)
            if 'salida_comp_enlace' in globals() and salida_comp_enlace is not False: enlace_final = t
    if 'enlace_final' in globals() and enlace_final is not False:
        data_json = ResultadoBusquedaPaginaPeli(i['nombre'])
        print(data_json)
        if 'data_json' in globals() and data_json is not False:
            # print(data_json)
            idtmdb = BuscarIdTmdb(data_json['titulo'],i['nombre'][-4:])
            comando = 'de2 -n "' + i['nombre'] + '" -i '+ data_json['audio'] +' -c 1080 -K 1080 -t '+ str(idtmdb) +' -e \'' + str(enlace_final) + '\' -L "true" -F "true" -p "www.pelisenhd.net";'
            print(comando)
    else:
        comando = False
    # print(comando)
    print()
    if 'comando' in globals() and comando is not False: 
        file.write(str(comando) + '\n\n')
        file.write(str(data_json) + os.linesep)


    # file.write("Segunda línea")
file.close()


# de2 -n "No basta con amar" -i "LATINO" -c 1080 -K 1080 -t 625707 -e 'https://mega.nz/file/1hdXQSzC#FZvevuhwNHFOvHWFK9MWKp0q1cC33KCmlQ6gqqLcge8' -L "true" -F "true" -p 'www.pelisenhd.net'; 
