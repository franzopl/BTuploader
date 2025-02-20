import argparse
from criar_torrent import criar_torrent
from obter_info_midia import obter_info_midia

def main():
    parser = argparse.ArgumentParser(
        description="Gera um arquivo .torrent a partir de um arquivo fornecido e obtém informações TMDB/IMDb."
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

    # Cria o torrent
    caminho_torrent = criar_torrent(
        caminho_arquivo=args.arquivo,
        caminho_saida=args.output
    )

    if caminho_torrent:
        print(f"Torrent gerado: {caminho_torrent}")
    else:
        print("Falha ao gerar o torrent.")

if __name__ == "__main__":
    main()