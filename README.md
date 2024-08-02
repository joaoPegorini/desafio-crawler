# IMDb Top 250 Crawler

Este projeto é um crawler para extrair informações dos filmes top 250 do IMDb. Utiliza a biblioteca `selenium` para realizar o web scraping e salva os dados em formatos JSON e SQLite.

## Funcionalidades

- **Web Scraping**: Extrai informações dos filmes top 250 do IMDb, incluindo título, ano, duração, colocação e classificação.
- **Salvamento em JSON**: Armazena os dados extraídos em um arquivo JSON com timestamp.
- **Captura de Tela**: Salva uma captura de tela da página de filmes.
- **Banco de Dados SQLite**: Salva os dados dos filmes em um banco de dados SQLite.
- **Agendamento de Execução**: Utiliza o `APScheduler` para agendar a execução do crawler a cada minuto, permitindo atualizações automáticas dos dados.

## Requisitos

- Python 3.x
- Selenium
- Pandas
- SQLite3
- WebDriver para o navegador Chrome

## Consulta da Tabela no SQLite

- Abra o terminal
- Execute o comando ' **sqlite3 movies.db** ' para acessar o banco de dados
- Execute o comando ' **SELECT * FROM movies;** ' para consultar os dados

## Agendador

O agendador é configurado usando a biblioteca `APScheduler`. O método `execute` do crawler é agendado para rodar periodicamente, e o script principal mantém o agendador em execução contínua. Se necessário, o agendador pode ser interrompido manualmente, e o navegador será fechado corretamente.

- Configurar intervalo de tempo do agendador no arquivo .env `em minutos`