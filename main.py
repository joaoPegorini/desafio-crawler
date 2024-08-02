import pandas as pd
import logging
import json
import os
import sqlite3
import time

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium import webdriver
from pandas import json_normalize
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CrawlerImdb:

    def __init__(self):
        """
        Inicializa a classe CrawlerImdb, configura o logger, abre o navegador e cria a conexão com o banco de dados.
        """

        # Configurar o logger
        log_filename = os.path.join("logs", datetime.now().strftime("logfile_%Y%m%d_%H%M%S.log"))
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s:%(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )

        self.url = "https://www.imdb.com/chart/top/?ref_=nv_mv_250"
        logging.info('Abrindo Navegador')
        # Abre o navegador Chrome
        self.driver = webdriver.Chrome()

        # Criar o diretório de logs se ele não existir
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Configurações de exibição do pandas
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

        # Conexão com o banco de dados SQLite
        self.create_table()

    def execute(self):
        """
        Executa o processo de web scraping, captura de tela, salvamento de dados e impressão de DataFrame.
        """
        logging.info('Executando tarefa do crawler...')

        # Abre a url no navegador
        self.driver.get(self.url)

        # Rola para baixo até que todos os filmes sejam carregados
        self.scroll_to_load_all_movies()

        # Espera até que todos os filmes estejam carregados
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ipc-metadata-list-summary-item"))
        )

        # Busca lista de filmes pela classe
        rows = self.driver.find_elements(By.CLASS_NAME, "ipc-metadata-list-summary-item")

        # Extrai informações dos filmes
        movies = self.get_movies(rows)

        # Salva os dados dos filmes em um arquivo JSON.
        self.save_json(movies)

        # Salva uma captura de tela da página atual do navegador.
        self.save_screenshot()

        # Salva os dados dos filmes no banco de dados
        self.save_to_db(movies)

        # Cria um DataFrame a partir do JSON
        df = json_normalize(movies)
        print(df)

        logging.info('Tarefa do crawler concluída.')

    def scroll_to_load_all_movies(self):
        """
        Rola a página para baixo até que todos os filmes sejam carregados.
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Rola para o fundo da página
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Espera um pouco para a página carregar

            # Calcula a nova altura da página e compara com a anterior
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def save_to_db(self, movies):
        """
        Salva os dados dos filmes no banco de dados SQLite.
        :param movies: Lista de dicionários contendo informações dos filmes
        """
        logging.info('Salvando dados no banco de dados')
        # Criar uma nova conexão com o banco de dados SQLite
        with sqlite3.connect('movies.db') as conn:
            query = """
            INSERT INTO movies (title, year, duration, placement, rating)
            VALUES (?, ?, ?, ?, ?)
            """
            for movie in movies:
                conn.execute(query,
                             (movie['title'], movie['year'], movie['duration'], movie['placement'], movie['rating']))
            conn.commit()

    def save_screenshot(self):
        """
        Salva uma captura de tela da página atual do navegador.
        """
        # Cria o diretório se ele não existir
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

        # Obtém a data e hora atuais no formato YYYYMMDD_HHMMSSFFF
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S%f")

        # Cria o nome do arquivo com a data e hora atual
        filename = f"screenshot_{current_datetime}.png"

        # Define o caminho completo do arquivo
        filepath = os.path.join("screenshots", filename)

        # Salva a captura de tela no arquivo
        self.driver.save_screenshot(filepath)

        logging.info('Captura de tela salva com sucesso.')

    def save_json(self, movies):
        """
        Salva os dados dos filmes em um arquivo JSON.
        :param movies: JSON de filmes
        """

        # Cria o diretório se ele não existir
        if not os.path.exists("json"):
            os.makedirs("json")

        # Obtém a data e hora atuais no formato YYYYMMDD_HHMMSSFFF
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S%f")

        # Cria o nome do arquivo com a data e hora atual
        filename = f"movies_{current_datetime}.json"

        # Define o caminho completo do arquivo
        filepath = os.path.join("json", filename)

        # Converte o objeto de filmes para JSON com indentação
        object_json = json.dumps(movies, indent=4)

        # Salva o JSON no arquivo
        with open(filepath, "w") as file:
            file.write(object_json)

        logging.info('Arquivo JSON gerado com sucesso.')

    def get_movies(self, rows):
        """
        Extrai informações dos filmes de cada linha buscada no site.
        :param rows: linhas buscadas no site
        :return: lista de dicionários (movies)
        """

        logging.info('Extraindo informações dos filmes.')
        movies = []
        for row in rows:
            infos = row.text.split("\n")

            data = {
                "title": infos[0][infos[0].find(". ") + 2:],
                "year": infos[1],
                "duration": infos[2],
                "placement": infos[3],
                "rating": infos[4]
            }

            movies.append(data)

        return movies

    def create_table(self):
        """
        Cria a tabela de filmes no banco de dados SQLite.
        """
        query = """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            year TEXT,
            duration TEXT,
            placement TEXT,
            rating TEXT
        )
        """
        with sqlite3.connect('movies.db') as conn:
            conn.execute(query)
            conn.commit()


# Inicializa o crawler e o agendador
if __name__ == "__main__":
    crawler = CrawlerImdb()

    # Carrega as variáveis do arquivo .env
    load_dotenv()

    interval = os.getenv("MINUTE_INTERVAL")
    if interval:
        interval = int(interval)
    else:
        interval = 60  # Valor padrão se a variável não estiver definida

    # Executa a tarefa inicial
    crawler.execute()

    # Configurar o agendador
    scheduler = BackgroundScheduler()
    scheduler.add_job(crawler.execute, 'interval', minutes=interval)
    scheduler.start()

    logging.info("Agendador iniciado e tarefa adicionada.")

    # Manter o script em execução
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Encerrando agendador e fechando o navegador.")
        scheduler.shutdown()
        crawler.driver.quit()