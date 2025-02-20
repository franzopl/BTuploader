import os
import subprocess
import requests
import json
from dotenv import load_dotenv

def obter_duracao_video(caminho_video):
    """Obtém a duração do vídeo em segundos usando ffprobe."""
    comando = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        caminho_video
    ]
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, check=True, timeout=60)
        dados = json.loads(resultado.stdout)
        return float(dados["format"]["duration"])
    except subprocess.TimeoutExpired:
        print("Erro: ffprobe demorou muito para responder.")
        return None
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as e:
        print(f"Erro ao obter duração do vídeo: {str(e)}")
        return None

def gerar_imagens(caminho_video):
    """
    Gera 6 imagens de um vídeo usando FFmpeg, faz upload para ImgBB e retorna os links.
    
    Parâmetros:
    caminho_video (str): Caminho do arquivo de vídeo
    
    Retorna:
    list: Lista de URLs das imagens carregadas no ImgBB ou None em caso de erro
    """
    try:
        # Carrega as variáveis do .env
        load_dotenv()
        imgbb_api_key = os.getenv("IMGBB_API_KEY")
        if not imgbb_api_key:
            raise ValueError("IMGBB_API_KEY não encontrado no arquivo .env")

        # Verifica se o vídeo existe
        if not os.path.exists(caminho_video):
            raise FileNotFoundError(f"O vídeo {caminho_video} não existe")

        # Obtém a duração do vídeo
        duracao = obter_duracao_video(caminho_video)
        if duracao is None:
            return None
        intervalo = duracao / 7  # Divide em 6 partes (7 pontos, 6 intervalos)

        # Diretório temporário para salvar as imagens
        temp_dir = os.path.join(os.path.dirname(__file__), "temp_images")
        os.makedirs(temp_dir, exist_ok=True)

        # Lista para armazenar os links das imagens
        links_imagens = []

        # Gera 6 imagens em timestamps equidistantes
        for i in range(1, 7):
            timestamp = intervalo * i
            output_file = os.path.join(temp_dir, f"frame_{i:03d}.jpg")
            comando_ffmpeg = [
                "ffmpeg",
                "-ss", str(timestamp),  # Seek antes do input para maior eficiência
                "-i", caminho_video,
                "-frames:v", "1",      # Extrai 1 frame
                "-q:v", "2",           # Qualidade alta
                output_file,
                "-y"                   # Sobrescreve arquivos existentes
            ]
            subprocess.run(comando_ffmpeg, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)

            # Faz upload para o ImgBB
            with open(output_file, "rb") as file:
                url = "https://api.imgbb.com/1/upload"
                payload = {
                    "key": imgbb_api_key,
                    "name": f"frame_{i}_{os.path.basename(caminho_video)}",
                }
                files = {"image": file}
                resposta = requests.post(url, data=payload, files=files, timeout=60)
                resposta.raise_for_status()

                dados = resposta.json()
                link_imagem = dados["data"]["url"]
                links_imagens.append(link_imagem)
                print(f"Imagem {i} carregada: {link_imagem}")

        # Remove o diretório temporário
        for i in range(1, 7):
            arquivo = os.path.join(temp_dir, f"frame_{i:03d}.jpg")
            if os.path.exists(arquivo):
                os.remove(arquivo)
        os.rmdir(temp_dir)

        return links_imagens

    except subprocess.TimeoutExpired:
        print("Erro: FFmpeg ou ImgBB demorou muito para responder.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar FFmpeg: {e.stderr.decode()}")
        return None
    except requests.RequestException as e:
        print(f"Erro ao fazer upload para ImgBB: {str(e)}")
        return None
    except Exception as e:
        print(f"Erro ao gerar imagens: {str(e)}")
        return None