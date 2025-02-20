# BTuploader


Este script no momento cria um arquivo .torrent, gera arquivo de mediainfo, localiza códigos do TMDB e IMDB do Vídeo, extrai 6 imagens do vídeo, envia essas imagens ao imgbb através de API e salva todas as informações necessárias para o upload em um arquivo .txt

## Pré-requisitos

Para utilizar o script será necessário instalar as dependências necessárias, execute o seguinte comando no terminal para instalar todas as bibliotecas listadas:

    pip3 install -r requirements.txt

Além das bibliotecas Python, o script depende de ferramentas externas que devem ser instaladas no sistema:

FFmpeg: Para gerar imagens do vídeo em gerar_imagens.py.

    sudo dnf install ffmpeg  # Fedora
    sudo apt install ffmpeg  # Ubuntu

MediaInfo: Para extrair informações do arquivo em criar_mediainfo.py.

    sudo dnf install mediainfo  # Fedora
    sudo apt install mediainfo  # Ubuntu

## Configuração do script:

Copie e renomeie o arquivo .example.env para .env e preencha suas credenciais:

ATENÇÃO: o arquivo .env guarda suas credenciais pessoais, não deve ser compartilhado. 

    cp .example.env .env

    nano .env

    TRACKER_URL=udp://tracker.openbittorrent.com:80
    TMDB_API_KEY=sua_chave_tmdb_aqui
    IMGBB_API_KEY=sua_chave_imgbb_aqui

## Comando para uso do script:

Execute o script main.py e forneça o arquivo desejado como primeiro argumento:

    python3 main.py /caminho/para/filme.mkv

serão gerados os arquivos dentro da pasta ./media.

Estou desenvolvendo ainda uma maneira de preencher os dados extraídos no formulário de upload automaticamente (breve)

