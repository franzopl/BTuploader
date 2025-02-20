from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import subprocess
import re
import time
import sys
from dotenv import load_dotenv
import os

def get_chrome_version():
    """Obtém a versão instalada do Google Chrome no sistema."""
    try:
        if sys.platform == "win32":
            cmd = r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
            output = subprocess.check_output(cmd, shell=True).decode()
            version = re.search(r"version\s+REG_SZ\s+([\d.]+)", output).group(1)
        elif sys.platform == "darwin":
            cmd = "/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version"
            output = subprocess.check_output(cmd, shell=True).decode()
            version = re.search(r"Google Chrome ([\d.]+)", output).group(1)
        else:  # Linux (incluindo Fedora)
            cmd = "google-chrome --version"
            output = subprocess.check_output(cmd, shell=True).decode()
            version = re.search(r"Google Chrome ([\d.]+)", output).group(1)
        return version
    except Exception as e:
        print(f"Erro ao verificar a versão do Chrome: {str(e)}")
        return None

def verificar_login_e_prosseguir(driver, caminho_torrent, imdb_id, links_imagens, texto_mediainfo):
    """Abre a página de login e espera o usuário fazer login manualmente, prosseguindo para upload."""
    login_url = "https://brasiltracker.org/login.php"
    index_url = "https://brasiltracker.org/index.php"
    driver.get(login_url)
    WebDriverWait(driver, 10).until(
        lambda d: d.current_url in [login_url, index_url]
    )

    if driver.current_url == index_url:
        print("Usuário já está logado. Prosseguindo para upload...")
        iniciar_upload(driver, caminho_torrent, imdb_id, links_imagens, texto_mediainfo)
    else:
        print("Por favor, faça login manualmente na página aberta.")
        print("Insira suas credenciais, resolva CAPTCHA ou 2FA se necessário, e pressione Enter após o login...")
        WebDriverWait(driver, 300).until(  # Aguarda até 5 minutos para login manual
            EC.url_to_be(index_url)
        )
        print("Login manual concluído. Prosseguindo para upload...")
        iniciar_upload(driver, caminho_torrent, imdb_id, links_imagens, texto_mediainfo)

def extrair_codec_audio(texto_mediainfo):
    """Extrai o codec de áudio do texto do MediaInfo, normalizando para corresponder às opções do dropdown."""
    linhas = texto_mediainfo.splitlines()
    codec = None
    for i, linha in enumerate(linhas):
        if linha.strip() == "Audio":
            for j in range(i + 1, len(linhas)):
                if linhas[j].startswith("Format ") and "Audio" not in linhas[j]:
                    codec = linhas[j].split(":", 1)[1].strip()
                    # Normaliza o codec: remove variações como "2.0", "LC", "HE", "JOC", etc.
                    codec_normalizado = re.sub(r"\s*\d+\.\d+|LC|HE|JOC", "", codec).strip().upper()
                    # Mapeia codecs comuns para corresponder ao dropdown
                    codec_map_normalizacao = {
                        "AAC": "AAC",
                        "AC3": "AC-3",
                        "EAC3": "E-AC-3",
                        "DTS": "DTS",
                        "FLAC": "FLAC",
                        "TRUEHD": "TrueHD",
                        "LPCM": "LPCM",
                        "COOK": "Cook",
                        "REALAUDIO": "RealAudio",
                        "MP1": "MP1",
                        "MP2": "MP2",
                        "MP3": "MP3",
                        "PCM": "PCM",
                        "DTS-ES": "DTS-ES",
                        "DTS-HD": "DTS-HD",
                        "DTS-X": "DTS-X",
                        "E-AC-3 JOC": "E-AC-3 JOC"
                    }
                    # Converte para maiúsculas para comparação e normaliza
                    for key, value in codec_map_normalizacao.items():
                        if key in codec_normalizado:
                            return value  # Retorna o formato do dropdown
                    # Tratamento especial para combinações como "AC3/EAC3", "EAC3/DTS", etc.
                    if "AAC" in codec_normalizado:
                        return "AAC"  # Garante que "AAC" seja retornado para variações como "AAC2.0"
                    if "AC3/EAC3" in codec_normalizado or "AC-3/E-AC-3" in codec_normalizado:
                        return "AC-3/E-AC-3"
                    if "EAC3/DTS" in codec_normalizado or "E-AC-3/DTS" in codec_normalizado:
                        return "E-AC-3/DTS"
                    return codec_normalizado.lower()  # Retorna o codec normalizado em minúsculas se não mapeado
    return None

def extrair_bitrate(caminho_torrent, texto_mediainfo):
    """Extrai o bitrate do nome do arquivo ou do texto do MediaInfo, mapeando para as opções do dropdown 'bitrate'."""
    if not caminho_torrent:
        return "WEB-DL"  # Padrão se não houver caminho

    nome_arquivo = os.path.basename(caminho_torrent)
    # Verifica padrões no nome do arquivo
    if "WEB-DL" in nome_arquivo.upper():
        return "WEB-DL"
    elif "WEBRip" in nome_arquivo.upper():
        return "WEBRip"
    elif "WEB" in nome_arquivo.upper():
        return "WEB"
    elif "Blu-ray" in nome_arquivo.upper() or "BD" in nome_arquivo.upper():
        if "BD100" in nome_arquivo.upper():
            return "BD100"
        elif "BD66" in nome_arquivo.upper():
            return "BD66"
        elif "BD50" in nome_arquivo.upper():
            return "BD50"
        elif "BD25" in nome_arquivo.upper():
            return "BD25"
        elif "Remux" in nome_arquivo.upper():
            return "Remux"
        elif "BRRip" in nome_arquivo.upper():
            return "BRRip"
        elif "BDRip" in nome_arquivo.upper():
            return "BDRip"
        return "Blu-ray"
    elif "DVD" in nome_arquivo.upper():
        if "DVD9" in nome_arquivo.upper():
            return "DVD9"
        elif "DVD5" in nome_arquivo.upper():
            return "DVD5"
        elif "DVDRip" in nome_arquivo.upper():
            return "DVDRip"
        elif "DVDScr" in nome_arquivo.upper():
            return "DVDScr"
        return "DVD9"
    elif "HD-DVD" in nome_arquivo.upper():
        return "HD-DVD"
    elif "HDRip" in nome_arquivo.upper():
        return "HDRip"
    elif "HDTC" in nome_arquivo.upper():
        return "HDTC"
    elif "HDTV" in nome_arquivo.upper():
        return "HDTV"
    elif "PDTV" in nome_arquivo.upper():
        return "PDTV"
    elif "SDTV" in nome_arquivo.upper():
        return "SDTV"
    elif "TC" in nome_arquivo.upper():
        return "TC"
    elif "TVRip" in nome_arquivo.upper():
        return "TVRip"
    elif "VHSRip" in nome_arquivo.upper():
        return "VHSRip"
    else:
        # Tenta extrair do MediaInfo, se disponível
        if texto_mediainfo:
            if "WEB-DL" in texto_mediainfo.upper():
                return "WEB-DL"
            elif "WEBRip" in texto_mediainfo.upper():
                return "WEBRip"
            elif "Blu-ray" in texto_mediainfo.upper() or "BD" in texto_mediainfo.upper():
                return "Blu-ray"
            elif "DVD" in texto_mediainfo.upper():
                return "DVD9"
        return "WEB-DL"  # Padrão se não identificado

def iniciar_upload(driver, caminho_torrent, imdb_id, links_imagens, texto_mediainfo):
    """Inicia o procedimento de upload e preenche o formulário automaticamente."""
    try:
        # Clica no link de upload
        link_upload = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/ul[2]/li[1]/a'))
        )
        link_upload.click()
        print("Link de upload clicado.")

        # Aguarda a página de upload carregar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="file"]'))
        )
        print("Página de upload carregada.")

        # 1. Insere o arquivo .torrent
        campo_torrent = driver.find_element(By.XPATH, '//*[@id="file"]')
        caminho_absoluto = os.path.abspath(caminho_torrent)
        campo_torrent.send_keys(caminho_absoluto)
        print(f"Arquivo .torrent inserido: {caminho_absoluto}")

        # 2. Seleciona "Filmes" no dropdown de categorias
        campo_categorias = Select(driver.find_element(By.XPATH, '//*[@id="categories"]'))
        campo_categorias.select_by_visible_text("Filmes")
        print("Categoria 'Filmes' selecionada.")

        # 3. Aguarda os novos campos carregarem
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="imdb_input"]'))
        )
        print("Novos campos carregados após seleção da categoria.")

        # 4. Preenche o campo IMDb
        if imdb_id:
            campo_imdb = driver.find_element(By.XPATH, '//*[@id="imdb_input"]')
            campo_imdb.clear()
            campo_imdb.send_keys(f"https://www.imdb.com/title/{imdb_id}/")
            print(f"Campo IMDb preenchido com: https://www.imdb.com/title/{imdb_id}/")

        # 5. Preenche o campo MediaInfo e codec de áudio
        if texto_mediainfo:
            campo_mediainfo = driver.find_element(By.XPATH, '//*[@id="mediainfo"]')
            campo_mediainfo.clear()
            campo_mediainfo.send_keys(texto_mediainfo)
            print("Campo MediaInfo preenchido.")
            time.sleep(1)  # Aguarda 1 segundo após inserir o MediaInfo

            # 6. Preenche o campo de codec de áudio
            codec_audio = extrair_codec_audio(texto_mediainfo)
            if codec_audio:
                campo_audio = Select(driver.find_element(By.XPATH, '//*[@id="audio_c"]'))
                # Mapeamento de codecs do MediaInfo para opções do dropdown do BrasilTracker
                codec_map = {
                    "E-AC-3": "E-AC-3",        # Dolby Digital Plus
                    "AC-3": "AC-3",            # Dolby Digital
                    "AAC": "AAC",
                    "MP3": "MP3",
                    "DTS": "DTS",
                    "FLAC": "FLAC",
                    "Vorbis": "Vorbis",
                    "TrueHD": "TrueHD",
                    "LPCM": "LPCM",
                    "Cook": "Cook",
                    "RealAudio": "RealAudio",
                    "MP1": "MP1",
                    "MP2": "MP2",
                    "PCM": "PCM",
                    "DTS-ES": "DTS-ES",
                    "DTS-HD": "DTS-HD",
                    "DTS-X": "DTS-X",
                    "E-AC-3 JOC": "E-AC-3 JOC",
                    "AC-3/E-AC-3": "AC-3/E-AC-3",
                    "AC-3/DTS": "AC-3/DTS",
                    "AC-3/DTS-ES": "AC-3/DTS-ES",
                    "AC-3/DTS-HD": "AC-3/DTS-HD",
                    "AC-3/TrueHD": "AC-3/TrueHD",
                    "E-AC-3/DTS": "E-AC-3/DTS",
                    "DTS-X/AC-3": "DTS-X/AC-3"
                }
                codec_selecionado = codec_map.get(codec_audio, "E-AC-3")  # Padrão para E-AC-3 se não mapeado
                try:
                    campo_audio.select_by_visible_text(codec_selecionado)
                    print(f"Codec de áudio '{codec_selecionado}' selecionado em //*[@id='audio_c'].")
                except:
                    print(f"Codec '{codec_selecionado}' não encontrado nas opções de //*[@id='audio_c']. Deixando sem seleção.")
            else:
                print("Nenhum codec de áudio encontrado no MediaInfo.")

        # 7. Seleciona o bitrate com base no arquivo
        bitrate = extrair_bitrate(caminho_torrent, texto_mediainfo)
        campo_bitrate = Select(driver.find_element(By.XPATH, '//*[@id="bitrate"]'))
        campo_bitrate.select_by_visible_text(bitrate)
        print(f"Bitrate '{bitrate}' selecionado.")

        # 8. Clica 4 vezes no botão de adicionar screenshots
        botao_add_screenshot = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/b/b/form/div[2]/table[2]/tbody/tr[14]/td[2]/a[1]')
        for _ in range(4):
            botao_add_screenshot.click()
            time.sleep(1)
        print("Botão de adicionar screenshots clicado 4 vezes.")

        # 9. Preenche os campos de screenshots
        if links_imagens:
            campos_screenshots = [
                '//*[@id="screen"]',
                '//*[@id="screen_1"]',
                '//*[@id="screen_2"]',
                '//*[@id="screen_3"]',
                '//*[@id="screen_4"]',
                '//*[@id="screen_5"]'
            ]
            for i, link in enumerate(links_imagens[:6]):
                campo = driver.find_element(By.XPATH, campos_screenshots[i])
                campo.clear()
                campo.send_keys(link)
                print(f"Link da imagem {i+1} inserido em {campos_screenshots[i]}: {link}")

        # 10. Aguarda o usuário conferir e clicar em 'Upload'
        print("Formulário de upload preenchido. Revise os campos e clique em 'Upload' manualmente.")

    except Exception as e:
        print(f"Erro ao preencher o formulário de upload: {str(e)}")
        raise

def main(caminho_torrent=None, imdb_id=None, links_imagens=None, texto_mediainfo=None):
    """Função principal que executa o fluxo do programa."""
    load_dotenv()
    
    print("Iniciando o script uploadmain.py...")

    chrome_version = get_chrome_version()
    if chrome_version:
        print(f"Versão do Chrome detectada: {chrome_version}")
    else:
        print("Não foi possível detectar a versão do Chrome. Usando versão padrão.")

    # Configurações para usar o perfil padrão do Chrome e manter a sessão
    chrome_options = Options()
    if sys.platform == "win32":
        user_data_dir = os.path.join(os.path.expanduser("~"), r"AppData\Local\Google\Chrome\User Data")
    elif sys.platform == "darwin":
        user_data_dir = os.path.join(os.path.expanduser("~"), "Library/Application Support/Google/Chrome")
    else:  # Linux (incluindo Fedora)
        user_data_dir = os.path.join(os.path.expanduser("~"), ".config/google-chrome")
    
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    chrome_options.add_argument('--profile-directory=Default')  # Usa o perfil padrão
    # chrome_options.add_argument('--headless')  # Descomente para modo sem interface, se necessário

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        verificar_login_e_prosseguir(driver, caminho_torrent, imdb_id, links_imagens, texto_mediainfo)
        input("Pressione Enter para fechar o navegador...")
    except Exception as e:
        print(f"Erro no fluxo principal: {str(e)}")
    finally:
        driver.quit()
        print("Script finalizado.")

if __name__ == "__main__":
    main()