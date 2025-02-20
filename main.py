import argparse
from criar_torrent import criar_torrent
from obter_info_midia import obter_info_midia
from gerar_imagens import gerar_imagens
from criar_mediainfo import criar_mediainfo, obter_idiomas_legendas
import os
import uploadmain

def main():
    parser = argparse.ArgumentParser(
        description="Gera um arquivo .torrent, obtém informações TMDB/IMDb, gera imagens com links e cria um .nfo."
    )
    parser.add_argument(
        "arquivo",
        type=str,
        help="Caminho do arquivo ou diretório a ser convertido em torrent"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Caminho de saída para o arquivo .torrent (opcional, sobrescreve o padrão ./media)"
    )

    args = parser.parse_args()

    # Obtém informações da mídia
    tmdb_id, imdb_id = obter_info_midia(args.arquivo)
    if tmdb_id and imdb_id:
        print(f"Informações obtidas - TMDB: {tmdb_id}, IMDb: {imdb_id}")
    else:
        print("Não foi possível obter as informações da mídia.")

    # Gera as imagens e obtém os links
    links_imagens = gerar_imagens(args.arquivo)
    if links_imagens:
        print(f"{len(links_imagens)} imagens geradas e carregadas com sucesso.")
    else:
        print("Não foi possível gerar ou carregar as imagens.")

    # Cria o torrent
    caminho_torrent = criar_torrent(
        caminho_arquivo=args.arquivo,
        caminho_saida=args.output
    )

    if caminho_torrent:
        print(f"Torrent gerado: {caminho_torrent}")

        # Obtém os idiomas das legendas
        idiomas_legendas = obter_idiomas_legendas(args.arquivo)

        # Gera o arquivo .txt com as informações
        nome_base = os.path.splitext(os.path.basename(caminho_torrent))[0]
        caminho_txt = os.path.join(os.path.dirname(caminho_torrent), f"{nome_base}.txt")
        
        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(f"Informações do Torrent: {nome_base}\n")
            f.write(f"TMDB ID: {tmdb_id if tmdb_id else 'Não encontrado'}\n")
            f.write(f"IMDb ID: {imdb_id if imdb_id else 'Não encontrado'}\n")
            f.write("Idiomas das Legendas:\n")
            if idiomas_legendas:
                for i, idioma in enumerate(idiomas_legendas, 1):
                    f.write(f"Legenda {i}: {idioma}\n")
            else:
                f.write("Nenhuma legenda encontrada.\n")
            f.write("Links das Imagens:\n")
            if links_imagens:
                for i, link in enumerate(links_imagens, 1):
                    f.write(f"Imagem {i}: {link}\n")
            else:
                f.write("Nenhuma imagem gerada.\n")
        
        print(f"Arquivo de informações salvo em: {caminho_txt}")

        # Gera o arquivo .nfo e obtém o texto do mediainfo
        caminho_nfo, texto_mediainfo = criar_mediainfo(args.arquivo)
        if caminho_nfo:
            print(f"Arquivo .nfo gerado: {caminho_nfo}")
        else:
            print("Falha ao gerar o arquivo .nfo.")

        # Executa o uploadmain.py com os dados gerados
        print("Iniciando o processo de upload...")
        uploadmain.main(
            caminho_torrent=caminho_torrent,
            imdb_id=imdb_id,
            links_imagens=links_imagens,
            texto_mediainfo=texto_mediainfo
        )

    else:
        print("Falha ao gerar o torrent.")

if __name__ == "__main__":
    main()