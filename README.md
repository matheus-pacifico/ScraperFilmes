# ScraperFilmes 

Esse projeto realiza o web scraping de filmes do site [AdoroCinema](https://www.adorocinema.com/). Os filmes são salvos em um arquivo csv separados por ";". As informações armazenadas são: título, sinopse e gênero.

## Instalação

### Pré-requisitos

- Python 3.x
- pip

### Instruções

1. **Clone o repositório**

   ```bash
   git clone https://github.com/matheus-pacifico/ScraperFilmes.git
   cd ScraperFilmes
   ```

2. **Instale as dependências**

   ```bash
   pip install -r dependencias.txt
   ```

3. **Execute o Scraper**

   ```bash
   python scraper.py
   ```

   Ele gerará o arquivo `dataset.csv`

## Dependências

- **Python 3.x**
- **Bibliotecas usadas:**
  - `requests`
  - `bs4`
  - `pandas`
