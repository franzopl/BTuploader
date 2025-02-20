import os
import libtorrent as lt
from dotenv import load_dotenv

def criar_torrent(caminho_arquivo, caminho_saida=None):
    """
    Cria um arquivo .torrent usando libtorrent, com tracker_url vindo de um arquivo .env.
    
    Parâmetros:
    caminho_arquivo (str): Caminho do arquivo que será convertido em torrent
    caminho_saida (str, opcional): Caminho onde o .torrent será salvo
    
    Retorna:
    str: Caminho do arquivo .torrent criado
    """
    try:
        # Carrega as variáveis do arquivo .env na mesma pasta
        load_dotenv()
        
        # Obtém o tracker_url do .env
        tracker_url = os.getenv("TRACKER_URL")
        if not tracker_url:
            raise ValueError("TRACKER_URL não encontrado no arquivo .env")

        # Verifica se o arquivo existe
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"O arquivo {caminho_arquivo} não existe")

        # Cria o file_storage
        fs = lt.file_storage()
        lt.add_files(fs, caminho_arquivo)
        
        # Cria o torrent com file_storage e piece_size diretamente
        t = lt.create_torrent(fs, piece_size=8192 * 1024)  # 8 MB
        
        # Adiciona o tracker
        t.add_tracker(tracker_url)
        
        # Gera os hashes
        lt.set_piece_hashes(t, os.path.dirname(caminho_arquivo) or ".")
        
        # Gera o arquivo torrent
        torrent_data = t.generate()
        
        # Define caminho de saída padrão
        if caminho_saida is None:
            caminho_saida = os.path.splitext(caminho_arquivo)[0] + ".torrent"
        
        # Salva o arquivo
        with open(caminho_saida, "wb") as f:
            f.write(lt.bencode(torrent_data))
            
        print(f"Arquivo torrent criado com sucesso em: {caminho_saida}")
        return caminho_saida
        
    except Exception as e:
        print(f"Erro ao criar o torrent: {str(e)}")
        return None