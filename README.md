# Document AI

### Participantes:

- Anne Fernandes da Costa Oliveira
- Matheus da Silva Nunes
- Thiago Henrique Menêses Bezerra

# Coleta e Documentação dos Dados PDF

## 1. Visão Geral

Este projeto tem como objetivo realizar a coleta de arquivos PDF do site do TJSP, organizando-os para análises futuras. O processo envolve o crawling do site, o download dos recursos e a extração de metadados essenciais de cada arquivo, possibilitando a criação de um repositório robusto e estruturado.

## 2. Descrição do Conjunto de Dados

O conjunto de dados é composto pelas informações extraídas dos arquivos PDF baixados. A tabela a seguir descreve cada coluna do dataset:

| Nome da Coluna              | Descrição                                                                                                       | Exemplo                                                       |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| **URL (string)**            | Endereço completo do arquivo PDF.                                                                               | `https://www.tjsp.jus.br/recursos/documento.pdf`              |
| **mime-type (string)**      | Tipo MIME do arquivo, geralmente `application/pdf` para arquivos PDF.                                           | `application/pdf`                                             |
| **nato-digital (boolean)**  | Indica se o PDF foi gerado digitalmente (nascido digital) ou se foi digitalizado a partir de documento físico.     | `true`                                                        |
| **numero-de-paginas (number)** | Número total de páginas presentes no PDF.                                                                    | `12`                                                          |
| **megabytes (number)**      | Tamanho do arquivo PDF em megabytes.                                                                            | `1.8`                                                         |

## 3. Processo de Coleta

A coleta dos dados foi realizada por meio de um crawler customizado que:

- **Navega e Extrai Links:** Utiliza ferramentas como Selenium, Helium e BeautifulSoup para identificar links internos que apontam para arquivos PDF.
- **Realiza o Download:** Efetua o download dos arquivos, preservando a hierarquia de diretórios do site.
- **Extrai Metadados:** Durante o download, são coletadas informações essenciais (URL, mime-type, status digital, número de páginas e tamanho do arquivo) para compor o dataset.

## 4. Armazenamento dos Dados

Após a coleta, os arquivos PDF e seus metadados foram organizados e armazenados em uma pasta no Google Drive, facilitando o acesso e análises futuras. Essa organização também permite a manutenção e expansão do repositório, que contém um volume muito maior de arquivos do que o micro exemplo aqui ilustrado.

## 5. Layout Estruturado dos Dados

A estrutura dos dados segue uma hierarquia que reflete a organização do site do TJSP. A seguir, um exemplo simplificado da disposição dos arquivos:

```
C:\USERS\WINDOWS\DESKTOP\ICD\PROJETO\DATA\WWW.TJSP.JUS.BR
├───Donwload
│   └───Portal
│       └───PrimeiraInstancia
│           └───GestaoDocumental
│               ├───Arquivo1.pdf
│               ├───Arquivo2.pdf
│               └───Arquivo3.pdf
├───Download
│   ├───acessibilidade
│   │   └───(vários PDFs)
│   ├───AssessoriaImprensa
│   │   └───(vários PDFs)
│   ├───Auxiliaresdajustica
│   │   └───(vários PDFs)
│   └───Biblioteca
│       ├───AgendaCentoCinquenta
│       │   └───(vários PDFs)
│       └───Homenagem
│           └───(vários PDFs)
```

> **Observação:** Este é apenas um micro exemplo ilustrativo. O repositório final contém muitos outros diretórios e arquivos, organizados de forma a refletir a estrutura original do site.

## 6. Link do Dataset

Acesse uma amostra do dataset através do link:  
[https://drive.google.com/drive/folders/1QFVWyyXfoqQxdXrhPfplIQ9nu_Q5yFsK?usp=drive_link](https://drive.google.com/drive/folders/1QFVWyyXfoqQxdXrhPfplIQ9nu_Q5yFsK?usp=drive_link)

