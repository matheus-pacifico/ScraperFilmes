# -*- coding: utf-8 -*-

# raspagem de dados
import requests
from bs4 import BeautifulSoup

## delay entre requisicoes
import random
import time

# dataframe
import pandas as pd


"""# Raspagem de dados"""

url_base = 'https://www.adorocinema.com'
url_lista_filmes = url_base + '/filmes-todos/'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'}

def requisicao(url, headers=headers):
  return requests.get(url, headers=headers)

def atrasarRequisicao(url='', min_ = 0.5, max_ = 2):
  delay = random.uniform(min_, max_)
  print(f"Aguardando {delay:.2f}s antes da próxima requisição {{{url}}}")
  time.sleep(delay)
  return delay


"""## Gêneros"""

OK = 200

resposta = requisicao(url_lista_filmes)

if resposta.status_code == OK:
  print("Gêneros encontrados:")
  
  soup = BeautifulSoup(resposta.content, 'html.parser')

  genero_ul = soup.find('ul', class_='filter-entity-word', attrs={'data-name': 'Por tipo'})
  genero_items = genero_ul.find_all('li', class_='filter-entity-item')
  generos = []

  for item in genero_items:
    a_ic = item.find('a', class_='item-content')
    genero_nome = a_ic.get_text(strip=True)
    filmes_count = item.find('span', class_='light').get_text().strip('()')
    try:
      filmes_count = int(filmes_count)
      if filmes_count >= filmes_count:
        generos.append((genero_nome, filmes_count, a_ic['href']))
        mensagem = f"Gênero: {genero_nome}, {filmes_count} filme{'s' if filmes_count != 1 else ''}"
        print(mensagem)
    except ValueError:
      continue
else:
  print(f"Falha ao acessar a página: {resposta.status_code}")

NOME = 0
# generos_escolhidos = ['Aventura', 'Ação']
generos_escolhidos = [genero[NOME] for genero in generos]
generos_selecionados = [genero for genero in generos if genero[NOME] in generos_escolhidos]
print(f"\nGêneros selecionados:\n{generos_selecionados}\n")


"""## Filmes"""

def get_somente_generos_escolhidos(generos, generos_escolhidos):
  result = []
  for genero in generos:
    genero = genero.get_text(strip=True)
    if genero in generos_escolhidos:
      result.append(genero)
  return result

def esta_adicionado(titulo, sinopse, lista_filmes):
  for filme in lista_filmes:
    if (filme[0] == titulo and filme[1] == sinopse):
      return True
  return False

def get_filmes_li(resposta):
  b_soup = BeautifulSoup(resposta.content, 'html.parser')
  filmes_soup = b_soup.find('div', class_='gd-col-middle')
  return filmes_soup.find_all('li', class_='mdl')

def adicionar_filmes(filmes_soup, lista_filmes, tamanho_minimo_sinopse = 1, maximo_generos_em_comum = len(generos_escolhidos)):
  NOME = 0
  num_filmes_invalidos = 0
  for filme in filmes_soup:
    titulo = filme.find('a', class_='meta-title-link').get_text(strip=True)
    info = filme.find('div', class_='meta-body-item meta-body-info')
    generos_filme = info.find_all('span', class_='dark-grey-link')
    generos_filme = get_somente_generos_escolhidos(generos_filme, generos_escolhidos)
    if len(generos_filme) > maximo_generos_em_comum:
      continue
    sinopse = filme.find('div', class_='content-txt')
    if sinopse == None:
      num_filmes_invalidos += 1
      continue
    sinopse = sinopse.get_text(strip=True)
    if len(sinopse) < tamanho_minimo_sinopse:
      continue
    if (not esta_adicionado(titulo, sinopse, lista_filmes)):
      lista_filmes.append((titulo, sinopse, generos_filme))
  return num_filmes_invalidos
  
filmes = []

OK = 200
URL = 2
QUANTIDADE = 1
NOME = 0
# MINIMO_FILMES_GENERO = 200
MINIMO_FILMES_GENERO = [genero[QUANTIDADE] for genero in generos]
#TAMANHOS_MINIMO_SINOPSE = [180, 100]
TAMANHOS_MINIMO_SINOPSE = [1] * len(generos_selecionados)
#NUMERO_MAXIMO_GENEROS_EM_COMUM = 1
NUMERO_MAXIMO_GENEROS_EM_COMUM = len(generos_selecionados)

tempo_em_espera = 0

print("Buscando filmes...\n")

for ind, genero in enumerate(generos_selecionados):
  filmes_adicionados = []
  pagina = 1
  tamanho_minimo_sinopse = TAMANHOS_MINIMO_SINOPSE[ind]
  minimo_filmes_genero = MINIMO_FILMES_GENERO[ind]
  print(f"--- Coletando filmes do gênero: {genero[NOME]} ---")
  
  while len(filmes_adicionados) < minimo_filmes_genero:
    request_url = url_base + genero[URL] + (('?page=' + str(pagina)) if pagina > 1 else '')
    tempo_em_espera += atrasarRequisicao(request_url)
    resposta = requisicao(request_url)
    if resposta.status_code != OK:
      print(f"Falha ao acessar a página: {resposta.status_code}")
      break
    filmes_li = get_filmes_li(resposta)
    minimo_filmes_genero -= adicionar_filmes(filmes_li, filmes_adicionados, tamanho_minimo_sinopse, NUMERO_MAXIMO_GENEROS_EM_COMUM)
    pagina += 1
  print()
  if minimo_filmes_genero <= 0:
    print(f"Nenhum filme do gênero {genero} encontrado!")
    continue
  filmes.extend(filmes_adicionados[:MINIMO_FILMES_GENERO])
print(f"Tempo de espera total entre requisições: {tempo_em_espera:.0f}s")

print(f"Foram selecionados {len(filmes)} filmes ao total")


"""# Criação do dataset.csv"""

nome_arquivo = 'dataset.csv'

cabecalhos = ['Titulo', 'Sinopse', 'Genero']

ds = pd.DataFrame(filmes, columns=cabecalhos)
ds.to_csv(nome_arquivo, index=False, sep=';')
print(f"Filmes salvos em '{nome_arquivo}' com {len(ds)} linhas")
