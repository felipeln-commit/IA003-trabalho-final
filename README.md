# IA003 — Trabalho final

Análise dos sinistros registrados pela PRF em 2024, com referência histórica de 2023. Aplicativo Streamlit com três painéis: população, amostra e inferência estatística.

## Executar localmente

Na raiz deste repositório, com Python 3.14:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Publicar no Streamlit Community Cloud

- Repositório: `IA003-trabalho-final`.
- Branch: a branch publicada no GitHub, normalmente `main`.
- Arquivo principal: `app.py`.
- Em Advanced settings, escolher Python 3.14, se disponível e compatível com as dependências.
- Acesso do aplicativo: público, para permitir avaliação sem autorização.

O endereço público será registrado após o deploy. Não há publicação realizada apenas pela criação desta pasta.

## Dados e resultados

Os ZIPs originais são da versão agrupada por ocorrência dos dados abertos da PRF. Fonte: https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf . Links e detalhes em [RELATORIO.md](RELATORIO.md).

A população de 2024 contém 73.202 sinistros. A amostra aleatória simples fixa tem 383 registros, selecionados sem reposição com semente 2024. Os arquivos em `dados/` e `resultados/` devem acompanhar o aplicativo: não é necessário refazer a análise para publicá-lo.

2023 fornece referências históricas fixas, sem participar do sorteio. Os filtros são descritivos e não alteram os testes.

## Reprodução da análise

```powershell
.\.venv\Scripts\python.exe analise.py
```

Esse comando regenera resultados e documentação; execute apenas quando desejar reproduzir a análise. `relatorio.py` é utilizado por esse processo.

## Documentação

- [Relatório e limitações](RELATORIO.md)
- [Plano de análise](PLANO_ANALISE.md)
- [Roteiro de vídeo](ROTEIRO_VIDEO.md)
- [Pendências de entrega](ENTREGA.md)

Não incluir dependências instaladas, ambientes virtuais ou credenciais no GitHub. As versões e o funcionamento na nuvem precisam ser confirmados nos logs e na validação do deploy.
