# BTuploader


Este script no momento cria um arquivo .torrent, gera arquivo de mediainfo, localiza códigos do TMDB e IMDB do Vídeo, Extrai 6 imagens do vídeo, envia essas imagens ao imgbb através de API e salva todas as informações necessárias para o upload em um arquivo .txt

Para utilizar o script será necessário instalar as dependências necessárias, execute o seguinte comando no terminal para instalar todas as bibliotecas listadas:

    pip3 install -r requirements.txt

Além das bibliotecas Python, o script depende de ferramentas externas que devem ser instaladas no sistema:

FFmpeg: Para gerar imagens do vídeo em gerar_imagens.py. Instale com:

        sudo dnf install ffmpeg  # Fedora
        sudo apt install ffmpeg  # Ubuntu

MediaInfo: Para extrair informações do arquivo em criar_mediainfo.py. Instale com:

        sudo dnf install mediainfo  # Fedora
        sudo apt install mediainfo  # Ubuntu


Comando para uso do script:

        python3 main.py /caminho/para/filme.mkv

serão gerados os arquivos dentro da pasta ./media.

Estou desenvolvendo ainda uma maneira de preencher os dados extraídos no formulário de upload automaticamente (breve)

