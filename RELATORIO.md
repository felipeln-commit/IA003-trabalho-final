# Sinistros registrados pela PRF: população e amostra de 2024

Trabalho de Probabilidade e Estatística — IA003. Resultados reproduzíveis. A identificação do aluno e os links de entrega ainda devem ser preenchidos.

## Pergunta, fonte e população

Como estimativas obtidas em uma AAS de 2024 se comparam aos parâmetros da população completa de 2024 e às referências históricas fixas de 2023?

A população contém todas as **73202 ocorrências** do CSV 2024, sem exclusões. A unidade amostral é **um sinistro registrado**, não uma pessoa ou veículo. 2023 é usado exclusivamente como referência histórica para H₀, sem entrar no sorteio ou nos painéis descritivos de 2024.

A fonte oficial é a PRF, versão agrupada por ocorrência do BAT. A população não representa todos os sinistros brasileiros ou os não registrados. A proporção de sinistros com morte não é mortalidade entre pessoas; fim de semana não mede risco por viagem ou exposição ao tráfego.

## Inspeção e tratamento antes do sorteio

| Ano | Linhas de dados, sem cabeçalho | Colunas originais | IDs únicos | Ausências nas quatro variáveis |
| --- | ---: | ---: | ---: | ---: |
| 2024 | 73202 | 30 | 73202 | 0 |
| 2023 | 67766 | 30 | 67766 | 0 |

Leitura direta dos CSVs nos ZIPs: Windows-1252 (cp1252), ponto e vírgula, cabeçalho na primeira linha, decodificação estrita e sem pular linhas. ID preservado como texto. Datas no CSV são ISO (AAAA-MM-DD), diferença de apresentação em relação ao dd/mm/aaaa do dicionário de 2017.

Conferidos: quantidade de campos de cada linha, unicidade e preenchimento de ID; datas no ano correto; correspondência do dia da semana; contagens inteiras não negativas; veículos ≥ 1; feridos = leves + graves.

**Nenhuma exclusão, imputação, deduplicação, remoção ou suavização de extremos foi feita antes do sorteio.** As conversões de tipo preservam os valores. Foram apenas derivados os indicadores e campos de apoio. Ausências de outras colunas estão no arquivo de inspeção e não definem exclusões.

| Campo | Definição utilizada | Dicionário |
| --- | --- | --- |
| id | Identificador da ocorrência | p. 3 |
| dia_semana | fim_semana = 1 em sábado/domingo, 0 nos demais | p. 3 |
| mortos | com_morte = 1 se houver pelo menos uma pessoa morta | p. 4 |
| feridos | Feridos leves + graves por ocorrência, incluindo zeros | p. 4 |
| veiculos | Veículos envolvidos por ocorrência | p. 4 |

## Dimensionamento e AAS

Confiança 95%; z = 1,95996398; E = 0,05 (5 pontos percentuais); p* = 0,50; N = 73202.

n₀ = z² p*(1−p*) / E²; n_finito = N n₀ / (N−1+n₀).

n₀ = 384,145882; n_finito = 382,145697; **n = 383** após arredondar para cima. Margem máxima aproximada atingida: 4,994 pontos percentuais.

O planejamento para proporções não assegura precisão específica para médias nem poder suficiente para qualquer diferença pequena.

Sorteio: numpy.random.default_rng(2024).choice(N, size=n, replace=False), gerador PCG64, ordem física do CSV original. Posições ordenadas apenas após seleção. Probabilidade de inclusão de cada elemento n/N = 0,00523210; fração amostral 0,5232%.

IDs e posições foram salvos. A amostra é única e congelada para todos os painéis; o aplicativo não sorteia novamente. A reprodução depende dos ZIPs, da ordem dos registros, do algoritmo, da versão do NumPy e da semente. Hashes estão em resultados/inspecao.json.

## Métodos e hipóteses

São quatro testes bilaterais, α = 0,05 por teste, definidos antes dos resultados. Para cada variável: H₀: parâmetro2024 = valor calculado no CSV completo de 2023; H₁: parâmetro2024 ≠ referência2023. A referência de 2023 é uma constante histórica, sem erro-padrão estimado; não é um teste entre duas amostras.

Apenas a amostra de 2024 fornece estimativas, variâncias e estatísticas dos testes. A população completa de 2024 fornece parâmetros descritivos para comparação e erro amostral observado, sem escolher hipóteses ou adaptar a amostra.

### Proporções

k = (N−n)/(N−1); EP₀ = √[k p₀(1−p₀)/n]; Z = (p̂−p₀)/EP₀; valor-p bilateral = 2 Φ(−|Z|). A aproximação normal incorpora a amostragem sem reposição e usa a proporção nula no erro-padrão do teste.

O IC de escore com correção finita inverte |p̂−p| ≤ z √[k p(1−p)/n]. Com a = z²k/n, centro = (p̂+a/2)/(1+a) e semi-amplitude = √[a p̂(1−p̂)+a²/4]/(1+a). É uma extensão aproximada de Wilson, não intervalo hipergeométrico exato. Verificam-se contagens esperadas e observadas. p₀ histórico não precisa corresponder a um número inteiro de sucessos em N na aproximação normal.

### Médias

s² = Σ(xᵢ−x̄)²/(n−1); EP = √[(1−n/N)s²/n]; t = (x̄−μ₀)/EP. Referência aproximada t com n−1 graus de liberdade; IC95% = x̄ ± t₀,₉₇₅ EP.

A dependência das seleções sem reposição é incorporada na variância. A distribuição t é aproximação de inferência para este desenho finito com contagens assimétricas, não uma garantia exata por n > 30. A fração amostral é baixa, então o efeito da correção finita é pequeno, mas foi aplicado consistentemente.

## Resultados

| Indicador | Referência 2023 | População 2024 | Amostra 2024 | IC95% da amostra | Estatística | Valor-p | Decisão 5% |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| Sinistros no fim de semana | 33,01% | 31,96% | 30,81% | [26,41%; 35,59%] | Z = -0,9173 | 0,358995 | Não rejeitar H₀ |
| Sinistros com pelo menos uma morte | 7,17% | 7,14% | 8,36% | [5,99%; 11,55%] | Z = 0,9023 | 0,366885 | Não rejeitar H₀ |
| Feridos por sinistro | 1,1579 | 1,1556 | 1,1854 | [1,0623; 1,3084] | t = 0,4399 | 0,660245 | Não rejeitar H₀ |
| Veículos por sinistro | 1,9978 | 1,9858 | 1,9765 | [1,8780; 2,0750] | t = -0,4257 | 0,670597 | Não rejeitar H₀ |

### Sinistros no fim de semana

Diferença populacional 2024 − 2023: -1,0468 pontos percentuais. Erro amostral observado (estimativa − parâmetro2024): -1,1515 pontos percentuais. O IC contém o parâmetro conhecido de 2024 e contém a referência de 2023.

A amostra não fornece evidência suficiente para rejeitar igualdade com a referência histórica. Isso não prova igualdade nem ausência de mudança. A diferença realizada nos arquivos completos é conhecida descritivamente, independentemente da decisão do teste.

Condições: 118 sucessos e 265 fracassos na amostra; esperados sob H₀: 126,42 e 256,58. Critério de pelo menos 10 em cada contagem: atendido.

### Sinistros com pelo menos uma morte

Diferença populacional 2024 − 2023: -0,0310 pontos percentuais. Erro amostral observado (estimativa − parâmetro2024): 1,2173 pontos percentuais. O IC contém o parâmetro conhecido de 2024 e contém a referência de 2023.

A amostra não fornece evidência suficiente para rejeitar igualdade com a referência histórica. Isso não prova igualdade nem ausência de mudança. A diferença realizada nos arquivos completos é conhecida descritivamente, independentemente da decisão do teste.

Condições: 32 sucessos e 351 fracassos na amostra; esperados sob H₀: 27,46 e 355,54. Critério de pelo menos 10 em cada contagem: atendido.

### Feridos por sinistro

Diferença populacional 2024 − 2023: -0,0022 por sinistro. Erro amostral observado (estimativa − parâmetro2024): 0,0297 por sinistro. O IC contém o parâmetro conhecido de 2024 e contém a referência de 2023.

A amostra não fornece evidência suficiente para rejeitar igualdade com a referência histórica. Isso não prova igualdade nem ausência de mudança. A diferença realizada nos arquivos completos é conhecida descritivamente, independentemente da decisão do teste.

Diagnóstico: assimetria amostral 4,863, máximo 14, P95 3,00; maior valor responde por 3,08% da soma. Os dados brutos não são assumidos normais.

IC bootstrap de sensibilidade: [1,0706; 1,3158], que contém a referência. É diagnóstico aproximado, sem substituir o IC t definido previamente ou eliminar a fragilidade a extremos raros ausentes da amostra.

### Veículos por sinistro

Diferença populacional 2024 − 2023: -0,0120 por sinistro. Erro amostral observado (estimativa − parâmetro2024): -0,0093 por sinistro. O IC contém o parâmetro conhecido de 2024 e contém a referência de 2023.

A amostra não fornece evidência suficiente para rejeitar igualdade com a referência histórica. Isso não prova igualdade nem ausência de mudança. A diferença realizada nos arquivos completos é conhecida descritivamente, independentemente da decisão do teste.

Diagnóstico: assimetria amostral 1,162, máximo 6, P95 4,00; maior valor responde por 0,79% da soma. Os dados brutos não são assumidos normais.

IC bootstrap de sensibilidade: [1,8774; 2,0756], que contém a referência. É diagnóstico aproximado, sem substituir o IC t definido previamente ou eliminar a fragilidade a extremos raros ausentes da amostra.

## Sensibilidade e limitações

Para as duas médias: 10.000 reamostragens empíricas com reposição, semente separada 202405, ordem feridos/veiculos. Médias bootstrap centradas na estimativa e reescaladas por √[(1−n/N)n/(n−1)], compatibilizando a variância com a estimativa AAS. IC percentil aproximado, não bootstrap exato do desenho. Nenhum novo sorteio na população, nenhuma variância populacional usada.

Os quatro testes primários usam 5% individualmente. Como sensibilidade à multiplicidade, aplica-se Holm com nível familiar 5%, sem escolher o resultado mais favorável:

| Indicador | Valor-p | Valor-p Holm | Decisão Holm |
| --- | ---: | ---: | --- |
| Sinistros no fim de semana | 0,358995 | 1,000000 | Não rejeitar |
| Sinistros com pelo menos uma morte | 0,366885 | 1,000000 | Não rejeitar |
| Feridos por sinistro | 0,660245 | 1,000000 | Não rejeitar |
| Veículos por sinistro | 0,670597 | 1,000000 | Não rejeitar |

Valores extremos são mantidos: máximos de veículos 131 em 2023 e 26 em 2024; máximos de feridos 62 e 85. Os registros não foram auditados individualmente. Poucos eventos podem influenciar médias, e uma amostra de 383 pode não capturar caudas raras. O dimensionamento de proporções não garante precisão nem poder das médias.

Os ICs são marginais, não simultâneos. Não se espera que exatamente 95% de apenas quatro ICs cubram os parâmetros. Significância não é relevância prática; não rejeitar H₀ não demonstra igualdade.

Os arquivos completos permitem verificar diferenças realizadas, mas não causalidade. Composição dos registros, cobertura, exposição e práticas de registro podem mudar entre anos. Não se mede risco por quilômetro ou viagem e não se atribui causa às diferenças. A fonte pode ser revisada; o estudo vale para os ZIPs preservados.

## Painéis e reprodução

Painel 1: população2024. Painel 2: a mesma análise na amostra salva. Painel 3: referência2023, parâmetro2024, estimativa, IC e teste. Filtros exploratórios descritivos não alteram o sorteio ou os testes.

Executar python analise.py regenera inspeção, amostra, resultados e documentação. Executar python iniciar_paineis.py abre os painéis locais. Publicação externa continua pendente.

## Fontes

- [PRF: catálogo oficial](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf), arquivos obtidos em 05/11/2026.
- [ZIP 2024](https://drive.google.com/file/d/14lB0vqMFkaZj8HZ44b0njYgxs9nAN8KO/view) e [ZIP 2023](https://drive.google.com/file/d/1-WO3SfNrwwZ5_l7fRTiwBKRw7mi1-HUq/view).
- [Dicionário oficial](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dicionario-acidentes), PDF 2017 indicado para registros a partir de 2017; cópia local em fontes/.
- [Penn State STAT 506](https://online.stat.psu.edu/stat506/Lesson02): apoio a AAS, variância e população finita. A inversão do escore com FPC foi explicitada neste relatório.
- [SciPy normal](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html) e [t](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.t.html): referências numéricas.
- Enunciado local: ../prova_final.txt. Não há prazo indicado no enunciado.

Ambiente: {"python": "3.14.7", "numpy": "2.5.4", "pandas": "3.1.1", "scipy": "1.18.1"}.
