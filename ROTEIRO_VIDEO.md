# Roteiro para vídeo de até 5 minutos

Meta: 4min40s com margem para transições. Roteiro para o aluno gravar; nenhum vídeo foi criado ou publicado.

## 0:00–0:35 — Contexto (painel 1)

Analisei os sinistros registrados pela PRF nas rodovias federais. A população de 2024 contém 73202 ocorrências, com 30 colunas e IDs únicos. A unidade é um sinistro, não uma pessoa. O ano de 2023 fornece somente referências históricas. Não estou estimando risco por viagem.

## 0:35–1:15 — AAS e dimensionamento

Conferi ausências, IDs, datas e contagens. Não excluí ocorrências ou extremos. Usei confiança 95%, margem de cinco pontos percentuais, p de 0,50 e correção finita. O tamanho final foi 383. Sorteei sem reposição com semente 2024, salvando os IDs para reproduzir a mesma amostra.

## 1:15–2:00 — População e amostra (painéis 1 e 2)

Mostrar proporções de fim de semana e ocorrência com morte, médias de feridos e veículos e distribuições. Explicar que as mesmas escalas permitem comparar as duas bases. A variação amostral é esperada; extremos podem influenciar as médias.

## 2:00–3:40 — Quatro testes (painel 3)

Cada teste é bilateral e compara o parâmetro2024 com a referência fixa de 2023, a 5%. Usei Z com escore para proporções e t aproximado para médias, incorporando a correção finita. A inferência usa só a amostra; o parâmetro2024 é exibido para comparação.

- **Sinistros no fim de semana**: referência 33,01%; população 31,96%; amostra 30,81%; IC [26,41%; 35,59%]; valor-p 0,3590. Não rejeitamos H₀.
- **Sinistros com pelo menos uma morte**: referência 7,17%; população 7,14%; amostra 8,36%; IC [5,99%; 11,55%]; valor-p 0,3669. Não rejeitamos H₀.
- **Feridos por sinistro**: referência 1,1579; população 1,1556; amostra 1,1854; IC [1,0623; 1,3084]; valor-p 0,6602. Não rejeitamos H₀.
- **Veículos por sinistro**: referência 1,9978; população 1,9858; amostra 1,9765; IC [1,8780; 2,0750]; valor-p 0,6706. Não rejeitamos H₀.

Manter a tabela visível e priorizar interpretação, sem ler todos os números.

## 3:40–4:25 — Limitações

Não rejeitar não prova igualdade. Os parâmetros completos mostram diferenças realizadas que a amostra pode não detectar. Há aproximação nos testes, assimetria, extremos, quatro comparações e ICs marginais. Holm e bootstrap são apenas sensibilidades. Não atribuo causalidade nem mudanças de risco individual aos resultados.

## 4:25–4:40 — Encerramento

As fontes, o código e os IDs estão documentados. A comparação com a população permite avaliar esta realização amostral. Os links dos painéis, vídeo e dados serão incluídos na entrega.

## Antes de gravar

- Inserir nome e turma, se necessário.
- Ensaiar com cronômetro e reduzir a fala caso ultrapasse cinco minutos.
- Confirmar que a tela mostra os resultados da amostra salva.
- Publicar o vídeo e conferir os links sem autenticação.
