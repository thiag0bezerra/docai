# Document AI

### Participantes:

- Anne Fernandes da Costa Oliveira
- Matheus da Silva Nunes
- Thiago Henrique Menêses Bezerra


Este projeto tem como objetivo a extração estruturada de dados dos portais oficiais dos seguintes órgãos:

- **Tribunal de Justiça de São Paulo (TJSP)**
- **Tribunal Regional Federal da 5.ª Região (TRF5)**
- **Justiça Federal no Ceará (JFCE)**

## Metodologia

### 1. Identificação das Fontes
- **Mapeamento das Páginas de Interesse:**  
  São identificadas as páginas oficiais dos tribunais e órgãos relacionados, onde se encontram as informações relevantes para a extração.

### 2. Extração Estruturada
- **Bibliotecas Utilizadas:**  
  Utilizamos as bibliotecas [httpx](https://www.python-httpx.org/) e [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) para a coleta e o parsing dos dados.

- **httpx:**  
  Responsável por realizar as requisições HTTP de forma assíncrona (ou síncrona, conforme a necessidade), permitindo a obtenção rápida do conteúdo das páginas.

- **BeautifulSoup:**  
  Utilizada para analisar e extrair os dados a partir da estrutura HTML das páginas, facilitando a identificação de elementos como tabelas, listas e outros componentes relevantes.

#### Exemplo de Código

```python
import httpx
from bs4 import BeautifulSoup

# URL de exemplo de uma página de um dos tribunais
url = "https://www.exemplo.org.br/pagina-de-interesse"

# Realizando a requisição HTTP utilizando httpx
response = httpx.get(url)
if response.status_code == 200:
    # Fazendo o parsing do conteúdo HTML com BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Exemplo: extração de todos os links de uma seção específica
    section = soup.find('div', {'id': 'secao-de-dados'})
    if section:
        links = section.find_all('a')
        for link in links:
            print(link.get('href'))
else:
    print(f"Erro ao acessar a página: {response.status_code}")
```

### 3. Tratamento dos Dados
- **Limpeza e Normalização:**  
  Após a extração, os dados passam por um processo de limpeza e normalização para remover inconsistências e formatações indesejadas.
  
- **Armazenamento:**  
  As informações processadas são armazenadas em formato estruturado (por exemplo, JSON, CSV ou bancos de dados relacionais) para facilitar análises futuras.

### 4. Respeito às Normas
- **Cumprimento das Diretrizes:**  
  Todas as extrações são realizadas em conformidade com as diretrizes de uso dos sites oficiais e a legislação vigente sobre acesso a dados públicos.  
- **Ética e Legalidade:**  
  O projeto respeita os limites impostos pelos Termos de Uso dos respectivos portais, garantindo que o acesso às informações seja feito de maneira ética e legal.

