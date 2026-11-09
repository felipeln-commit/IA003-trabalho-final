# Plano de análise definido antes dos resultados

## Escopo aprovado

População: todas as linhas do CSV oficial datatran2024, agrupado por ocorrência. Unidade amostral: sinistro registrado. Histórico datatran2023: apenas quatro referências constantes de H₀. Não combinar os anos nem tratar o histórico como segunda amostra.

## Inspeção concluída antes da seleção

2024: 73.202 linhas de dados e 30 colunas; 2023: 67.766 e 30. IDs únicos; nenhuma ausência em dia_semana, mortos, feridos ou veiculos. Datas e dias coerentes; contagens inteiras não negativas; feridos iguais a leves mais graves. Nenhuma exclusão, imputação, correção de valores ou remoção de extremos.

Dicionário oficial PRF, ocorrência a partir de 2017: ID e dia_semana na página 3; mortos, feridos e veiculos na página 4. Formato ISO de data no CSV prevalece sobre a descrição antiga de apresentação do dicionário.

## Sorteio

AAS sem reposição, confiança 95%, E = 0,05, p* = 0,50, correção de população finita e arredondamento para cima. N = 73.202; n = 383. Semente principal 2024, NumPy default_rng/PCG64, ordem física do CSV. Salvar posições e IDs. Não repetir seleção por conveniência ou resultado.

## Quatro testes bilaterais

1. Proporção de sinistros em sábado/domingo de 2024 = proporção do CSV completo de 2023.
2. Proporção de sinistros com mortos ≥ 1 em 2024 = proporção do CSV completo de 2023.
3. Média de feridos por sinistro em 2024 = média do CSV completo de 2023.
4. Média de veículos por sinistro em 2024 = média do CSV completo de 2023.

As alternativas são desigualdades bilaterais; α = 0,05 por teste. ICs de 95%, marginais. Proporções: escore normal com FPC, IC por inversão; verificar sucessos e fracassos observados/esperados. Médias: t aproximado, variância amostral e FPC; descrever assimetria e extremos. O relatório explicita as aproximações.

## Sensibilidades, sem substituir os testes

Holm para as quatro comparações; bootstrap percentil centrado/reescalado para as duas médias, B = 10.000 e semente separada 202405. Sem usar a população completa para gerar bootstrap ou adaptar a amostra. Divergências entre métodos serão relatadas, sem escolher o resultado favorável.

## Produto

Três painéis locais em Streamlit: população, amostra e inferência/comparação. A mesma amostra em todas as análises. Filtros apenas exploratórios nos dois painéis descritivos; inferência permanece fixa. Relatório, resultados CSV/JSON, código, roteiro de vídeo e checklist. Hospedagem e vídeo final permanecem pendentes.
