import os
from typing import Set, List, Tuple
from urllib.parse import urljoin, urlparse, ParseResult

import helium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import requests
from bs4 import BeautifulSoup

# Variável global para o driver – será definida durante a inicialização.
driver: webdriver.Chrome = None  # type: ignore

def initialize_driver() -> webdriver.Chrome:
    """
    Inicializa o WebDriver do Selenium com configurações otimizadas para uso com o Helium.
    
    Configurações aplicadas:
      - Força a escala do dispositivo para 1.
      - Define o tamanho da janela.
      - Desativa o visualizador de PDF integrado.
      - Posiciona a janela no canto superior esquerdo.
      
    Returns:
        Uma instância configurada do Chrome WebDriver.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--force-device-scale-factor=1")
    chrome_options.add_argument("--window-size=1000,1350")
    chrome_options.add_argument("--disable-pdf-viewer")
    chrome_options.add_argument("--window-position=0,0")
    return helium.start_chrome(headless=False, options=chrome_options)

def crawl_site_resources(base_url: str, max_depth: int = 10) -> str:
    """
    Realiza o crawling recursivo a partir de 'base_url' até uma profundidade máxima 'max_depth',
    buscando e baixando recursos com extensões específicas.

    Para cada link encontrado:
      - Se o link apontar para um recurso com extensão presente em 'resource_extensions', o recurso é baixado,
        preservando a hierarquia de diretórios relativa (armazenado em ./data/<domínio>/<caminho>).
      - Caso contrário, o link é considerado uma página e adicionado à fila para navegação.
      
    A função evita acesso repetido a URLs utilizando um conjunto de URLs já visitadas e ignora links externos
    que não pertençam ao domínio "tjsp.jus.br".

    Args:
        base_url: URL inicial para iniciar o processo de crawling.
        max_depth: Profundidade máxima para a recursão no crawling.

    Returns:
        Um resumo dos recursos baixados, listando os caminhos relativos e os links completos.
    """
    visited: Set[str] = set()
    resources: List[Tuple[str, str]] = []  # Lista de tuplas (caminho_relativo, URL_completa)
    queue: List[Tuple[str, int]] = [(base_url, 0)]
    resource_extensions: Set[str] = {
        ".pdf", ".txt", ".xlsx", ".doc", ".docx", ".ppt", ".pptx",
        ".csv", ".xml", ".json", ".rtf", ".zip", ".rar",
    }

    while queue:
        current_url, depth = queue.pop(0)
        # Verifica se atingiu a profundidade máxima
        if depth > max_depth:
            continue
        # Ignora URLs já visitadas
        if current_url in visited:
            continue
        visited.add(current_url)

        parsed: ParseResult = urlparse(current_url)
        # Ignora URLs que não pertencem ao domínio de interesse
        if "tjsp.jus.br" not in parsed.netloc:
            print(f"[crawl_site_resources] Ignorando URL externa: {current_url}")
            continue

        try:
            print(f"[crawl_site_resources] Navegando para {current_url} (profundidade {depth})")
            driver.get(current_url)
            # Aguarda até que a página esteja completamente carregada
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception as e:
            print(f"[crawl_site_resources] Falha ao acessar {current_url}: {e}")
            continue

        # Utiliza BeautifulSoup para extrair todos os links da página
        page_source: str = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        anchors = soup.find_all("a")

        for a in anchors:
            href: str | None = a.get("href")
            if not href:
                continue
            # Converte o link relativo em absoluto
            absolute_href: str = urljoin(current_url, href)
            parsed_href: ParseResult = urlparse(absolute_href)
            # Verifica se o link pertence ao domínio de interesse
            if "tjsp.jus.br" not in parsed_href.netloc:
                print(f"[crawl_site_resources] Ignorando link externo: {absolute_href}")
                continue

            # Extrai a extensão do arquivo para verificar se é um recurso a ser baixado
            _, ext = os.path.splitext(parsed_href.path)
            ext = ext.lower()
            if ext and ext in resource_extensions:
                # Define o caminho relativo para salvar o recurso
                relative_path: str = parsed_href.path.lstrip("/")
                base_dir: str = "./data"
                domain_dir: str = os.path.join(base_dir, parsed_href.netloc)
                save_dir: str = os.path.join(domain_dir, os.path.dirname(parsed_href.path).lstrip("/"))
                os.makedirs(save_dir, exist_ok=True)
                filename: str = os.path.join(save_dir, os.path.basename(parsed_href.path))
                
                # Se o arquivo ainda não foi baixado, tenta realizar o download
                if not os.path.isfile(filename):
                    try:
                        print(f"[crawl_site_resources] Tentando baixar recurso: {absolute_href}")
                        response = requests.get(absolute_href)
                        if response.status_code == 200:
                            with open(filename, "wb") as f:
                                f.write(response.content)
                            resources.append((relative_path, absolute_href))
                            print(f"[crawl_site_resources] Recurso baixado: {filename}")
                        else:
                            print(f"[crawl_site_resources] Falha ao baixar recurso: {absolute_href} (Status: {response.status_code})")
                    except Exception as e:
                        print(f"[crawl_site_resources] Erro ao baixar recurso de {absolute_href}: {e}")
                else:
                    print(f"[crawl_site_resources] Recurso já existe: {filename}")
            else:
                # Adiciona links de páginas para navegação, caso não tenham sido visitados ainda
                if absolute_href not in visited:
                    queue.append((absolute_href, depth + 1))

    # Monta o resumo dos recursos baixados
    summary_lines: List[str] = ["Downloaded resources:"]
    for rel_path, full_url in sorted(resources):
        summary_lines.append(f"{rel_path}: {full_url}")
    summary: str = "\n".join(summary_lines)
    print(f"[crawl_site_resources] {summary}")
    return summary


if __name__ == '__main__':
    crawl_site_resources("https://tjsp.jus.br/", max_depth=3)