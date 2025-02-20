import os
import subprocess

def criar_mediainfo(caminho_arquivo, caminho_saida=None):
    """
    Extrai informações do arquivo de mídia usando mediainfo e gera um arquivo .nfo no formato padrão,
    com o campo 'Complete name' mostrando apenas o nome do arquivo.
    
    Parâmetros:
    caminho_arquivo (str): Caminho do arquivo de mídia
    caminho_saida (str, opcional): Caminho onde o .nfo será salvo (padrão: junto ao .torrent)
    
    Retorna:
    tuple: (caminho do arquivo .nfo gerado, texto do mediainfo) ou (None, None) em caso de erro
    """
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"O arquivo {caminho_arquivo} não existe")

        # Define o caminho de saída padrão (mesmo diretório do torrent)
        if caminho_saida is None:
            nome_base = os.path.splitext(os.path.basename(caminho_arquivo))[0]
            diretorio_media = os.path.join(os.path.dirname(__file__), "media")
            caminho_saida = os.path.join(diretorio_media, f"{nome_base}.nfo")

        # Comando para extrair informações com mediainfo (formato padrão)
        comando_mediainfo = [
            "mediainfo",
            caminho_arquivo
        ]
        resultado = subprocess.run(comando_mediainfo, capture_output=True, text=True, check=True)

        # Processa a saída para ajustar o campo "Complete name"
        linhas = resultado.stdout.splitlines()
        nome_arquivo = os.path.basename(caminho_arquivo)
        output_modificado = []
        
        for linha in linhas:
            if linha.startswith("Complete name"):
                output_modificado.append(f"Complete name                            : {nome_arquivo}")
            else:
                output_modificado.append(linha)

        texto_mediainfo = "\n".join(output_modificado)

        # Gera o arquivo .nfo com as informações modificadas
        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write("MediaInfo\n")
            f.write("----------------------------------------\n")
            f.write(texto_mediainfo)
            f.write("\n----------------------------------------\n")

        print(f"Arquivo .nfo gerado com sucesso em: {caminho_saida}")
        return caminho_saida, texto_mediainfo

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar mediainfo: {e.stderr}")
        return None, None
    except Exception as e:
        print(f"Erro ao criar o arquivo .nfo: {str(e)}")
        return None, None

def obter_idiomas_legendas(caminho_arquivo):
    """Extrai os idiomas das faixas de legendas do arquivo usando mediainfo."""
    try:
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"O arquivo {caminho_arquivo} não existe")

        comando_mediainfo = ["mediainfo", caminho_arquivo]
        resultado = subprocess.run(comando_mediainfo, capture_output=True, text=True, check=True)

        linhas = resultado.stdout.splitlines()
        idiomas = []
        em_secao_texto = False
        
        for linha in linhas:
            if linha.startswith("Text"):
                em_secao_texto = True
            elif em_secao_texto and linha.startswith("Language"):
                idioma = linha.split(":")[1].strip()
                idiomas.append(idioma)
                em_secao_texto = False

        return idiomas

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar mediainfo para legendas: {e.stderr}")
        return []
    except Exception as e:
        print(f"Erro ao obter idiomas das legendas: {str(e)}")
        return []