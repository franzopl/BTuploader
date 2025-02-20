import argparse
from criar_torrent import criar_torrent

def main():
    # Configura o parser de argumentos
    parser = argparse.ArgumentParser(
        description="Gera um arquivo .torrent a partir de um arquivo fornecido."
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
        help="Caminho de saída para o arquivo .torrent (opcional)"
    )

    # Obtém os argumentos da linha de comando
    args = parser.parse_args()

    # Chama a função criar_torrent com os argumentos fornecidos
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