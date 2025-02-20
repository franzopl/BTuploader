import os
import requests
import re
from dotenv import load_dotenv

def obter_info_midia(caminho_arquivo):
    """
    Obtém o código TMDB e o ID IMDb de uma mídia a partir do nome do arquivo usando a API TMDB.
    
    Parâmetros:
    caminho_arquivo (str): Caminho do arquivo de mídia
    
    Retorna:
    tuple: (tmdb_id, imdb_id) ou (None, None) em caso de erro
    """
    try:
        # Carrega as variáveis do .env
        load_dotenv()
        api_key = os.getenv("TMDB_API_KEY")
        if not api_key:
            raise ValueError("TMDB_API_KEY não encontrado no arquivo .env")

        # Extrai o nome do arquivo
        nome_arquivo = os.path.basename(caminho_arquivo)
        
        # Remove extensões e tenta extrair título e ano com regex
        nome_sem_extensao = os.path.splitext(nome_arquivo)[0]
        match = re.match(r"(.+?)\.(\d{4})", nome_sem_extensao)
        if match:
            titulo = match.group(1).replace(".", " ").strip()
            ano = match.group(2)
        else:
            titulo = nome_sem_extensao.replace(".", " ").strip()
            ano = None

        # URL da API TMDB para busca
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": api_key,
            "query": titulo,
            "year": ano if ano else None,
            "language": "pt-BR"  # Pode ajustar o idioma
        }

        # Faz a requisição à API
        resposta = requests.get(url, params=params)
        resposta.raise_for_status()  # Levanta exceção se houver erro HTTP
        
        dados = resposta.json()
        if not dados["results"]:
            print(f"Nenhum resultado encontrado para '{titulo}'")
            return None, None

        # Pega o primeiro resultado
        resultado = dados["results"][0]
        tmdb_id = resultado["id"]
        
        # Busca detalhes adicionais para obter o IMDb ID
        url_detalhes = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params_detalhes = {"api_key": api_key}
        resposta_detalhes = requests.get(url_detalhes, params=params_detalhes)
        resposta_detalhes.raise_for_status()
        
        detalhes = resposta_detalhes.json()
        imdb_id = detalhes.get("imdb_id", None)

        print(f"TMDB ID: {tmdb_id}, IMDb ID: {imdb_id}")
        return tmdb_id, imdb_id

    except Exception as e:
        print(f"Erro ao obter informações da mídia: {str(e)}")
        return None, None