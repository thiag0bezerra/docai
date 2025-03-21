import asyncio
from bs4 import BeautifulSoup
from string import ascii_lowercase, ascii_uppercase, digits
from typing import List, Optional
from urllib.parse import urlparse, ParseResult, parse_qsl, urlencode, urljoin
import os
import httpx


# ----------------------------------------------------------------------------------
# Função: extract_download_urls_from_html
# ----------------------------------------------------------------------------------
def extract_download_urls_from_html(content: str) -> List[str]:
    """
    Extrai todas as URLs que apontam para arquivos PDF a partir do conteúdo dado.
    Considera URLs que começam com "downloadDocumento.do".
    """
    # Cria um objeto BeautifulSoup para realizar o parsing do conteúdo HTML
    soup: BeautifulSoup = BeautifulSoup(content, "html.parser")
    # Encontra todas as tags <a> que possuem o atributo 'href'
    anchors = soup.find_all("a", href=True)
    # Filtra e retorna as URLs que iniciam com "downloadDocumento.do"
    urls: List[str] = [
        anchor["href"]
        for anchor in anchors
        if anchor["href"].startswith("downloadDocumento.do")
    ]
    return urls


# ----------------------------------------------------------------------------------
# Função: fetch_pdf_urls
# ----------------------------------------------------------------------------------
async def fetch_pdf_urls(client: httpx.AsyncClient, url: str) -> List[str]:
    """
    Realiza a requisição para a URL informada e busca por URLs de arquivos PDF
    no conteúdo retornado.

    Retorna uma lista com as URLs encontradas ou uma lista vazia caso ocorra algum erro.
    """
    # Log para indicar o início da requisição
    print(f"Buscando URL: {url}")
    try:
        # Realiza a requisição HTTP de forma assíncrona
        response = await client.get(url)
        # Levanta exceção se a resposta não for bem-sucedida (status diferente de 2xx)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        # Trata erros de status HTTP e imprime mensagem de erro com o status retornado
        print(f"Falha ao buscar URL: {url} (Status: {exc.response.status_code})")
        return []
    except httpx.RequestError as exc:
        # Trata erros de requisição (ex.: conexão) e imprime mensagem de erro
        print(f"Erro ao buscar URL {url}: {exc}")
        return []

    # Obtém o conteúdo textual da resposta
    content: str = response.text
    # Extrai as URLs de PDF a partir do conteúdo HTML
    pdf_urls: List[str] = extract_download_urls_from_html(content)
    return pdf_urls


# ----------------------------------------------------------------------------------
# Função: get_filename
# ----------------------------------------------------------------------------------
def get_filename(url: str) -> str:
    """
    Extrai o nome do arquivo a partir da URL, garantindo uma estrutura de diretórios
    consistente com base no domínio e caminho da URL. Se houver parâmetros de consulta,
    estes são processados e incluídos no nome do arquivo.
    """
    # Analisa a URL e extrai seus componentes
    parsed_url: ParseResult = urlparse(url)
    # Define a pasta a partir do domínio
    domain_dir: str = parsed_url.netloc
    # Define o diretório de salvamento utilizando o caminho da URL, removendo a barra inicial
    save_dir: str = os.path.join(
        domain_dir, os.path.dirname(parsed_url.path).lstrip("/")
    )
    # Monta o nome básico do arquivo utilizando o nome da última parte do caminho
    filename: str = os.path.join(save_dir, os.path.basename(parsed_url.path))

    # Se existirem parâmetros na URL, processa-os para gerar um nome de arquivo seguro
    if parsed_url.query:
        # Define um conjunto de caracteres considerados seguros
        safe_chars = set("_-" + ascii_lowercase + ascii_uppercase + digits)
        # Converte os parâmetros da query string em uma lista de tuplas
        params = parse_qsl(parsed_url.query)
        # Ordena os parâmetros para garantir consistência no nome do arquivo
        params.sort()
        # Gera uma representação canônica dos parâmetros
        query_canon = urlencode(params)
        # Substitui caracteres não seguros por underline
        name = "".join(ch if ch in safe_chars else "_" for ch in query_canon)
        # Acrescenta o processamento dos parâmetros ao nome do arquivo
        filename = os.path.join(filename, name)
    return filename


# ----------------------------------------------------------------------------------
# Função: fetch
# ----------------------------------------------------------------------------------
async def fetch(client: httpx.AsyncClient, url: str) -> Optional[bytes]:
    """
    Realiza o download do recurso na URL informada utilizando httpx de forma assíncrona.
    Retorna o conteúdo em bytes se a requisição for bem-sucedida, ou None em caso de falha.
    """
    try:
        # Realiza a requisição GET de forma assíncrona
        response = await client.get(url)
        # Verifica se o status da resposta indica sucesso
        response.raise_for_status()
        # Retorna o conteúdo da resposta em bytes
        return response.content
    except httpx.HTTPStatusError as exc:
        # Em caso de erro HTTP, imprime a mensagem com o status retornado
        print(f"Falha ao baixar recurso: {url} (Status: {exc.response.status_code})")
    except httpx.RequestError as exc:
        # Em caso de erro na requisição, imprime a mensagem de erro
        print(f"Erro ao baixar recurso de {url}: {exc}")
    # Retorna None se ocorrer algum erro
    return None


# ----------------------------------------------------------------------------------
# Função: process_pdf_url
# ----------------------------------------------------------------------------------
async def process_pdf_url(
    client: httpx.AsyncClient, base_url: str, pdf_url: str
) -> None:
    """
    Processa a URL do PDF: monta a URL completa, verifica se o arquivo já existe e,
    se não existir, realiza o download e o salvamento do conteúdo.
    """
    # Combina a URL base com a URL relativa do PDF para formar a URL completa
    remote_file_url = urljoin(base_url, pdf_url)

    # Constrói o caminho completo para salvar o arquivo, organizando-o em subdiretórios
    filename = (
        os.path.join(
            "data",
            get_filename(base_url),
            "__contains__",
            get_filename(remote_file_url),
        )
        + ".pdf"
    )

    # Verifica se o arquivo já foi baixado (existe no disco)
    if not os.path.isfile(filename):
        # Tenta fazer o download do conteúdo do PDF
        pdf_content = await fetch(client, remote_file_url)
        if pdf_content:
            # Salva o arquivo em disco utilizando uma thread separada para operações de I/O
            await asyncio.to_thread(save_file, filename, pdf_content)
            print(f"Recurso salvo: {filename}")
        else:
            print(f"Falha ao baixar recurso: {pdf_url}")
    else:
        # Caso o arquivo já exista, apenas registra a informação
        print(f"Recurso já existe: {filename}")


# ----------------------------------------------------------------------------------
# Função: save_file
# ----------------------------------------------------------------------------------
def save_file(filename: str, content: bytes) -> None:
    """
    Salva o conteúdo em disco, garantindo que o diretório exista.
    """
    # Cria o diretório (e subdiretórios) caso não existam
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    # Abre o arquivo em modo binário e grava o conteúdo
    with open(filename, "wb") as f:
        f.write(content)


# ----------------------------------------------------------------------------------
# Função: process_titulo
# ----------------------------------------------------------------------------------
async def process_titulo(
    nu_titulo: int, client: httpx.AsyncClient, semaphore: asyncio.Semaphore
) -> None:
    """
    Processa um título específico: monta a URL, busca as URLs de PDF e
    processa cada uma delas de forma concorrente.
    """
    # Utiliza o semaphore para limitar a quantidade de tarefas concorrentes
    async with semaphore:
        # Monta a URL para o título utilizando o número informado
        url = f"https://esaj.tjsp.jus.br/ctoPtl/visualisarContrato.do?nuTitulo={nu_titulo}"
        # Busca as URLs de PDFs presentes no conteúdo da página
        pdf_urls = await fetch_pdf_urls(client, url)
        # Cria tarefas para processar cada URL de PDF encontrada, removendo duplicatas
        tasks = [process_pdf_url(client, url, pdf_url) for pdf_url in set(pdf_urls)]
        # Aguarda a conclusão de todas as tarefas associadas, se houver
        if tasks:
            await asyncio.gather(*tasks)


# ----------------------------------------------------------------------------------
# Função: main
# ----------------------------------------------------------------------------------
async def main() -> None:
    # Define um limite de concorrência para evitar sobrecarregar o sistema
    semaphore = asyncio.Semaphore(10)  # ajuste conforme necessário
    # Cria um cliente HTTP assíncrono com timeout e limites de conexão configurados
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60),
        limits=httpx.Limits(max_keepalive_connections=100, max_connections=10),
    ) as client:
        # Cria uma lista de tarefas para processar um grande número de títulos (neste caso, de 0 a 999.999)
        tasks = [
            process_titulo(nu_titulo, client, semaphore)
            for nu_titulo in range(0, 1000000)
        ]
        # Executa todas as tarefas de forma concorrente e aguarda sua conclusão
        await asyncio.gather(*tasks)


# ----------------------------------------------------------------------------------
# Ponto de entrada do script
# ----------------------------------------------------------------------------------
if __name__ == "__main__":
    # Inicia a execução da função main dentro do loop de eventos do asyncio
    asyncio.run(main())
