"""Documentação gerada dos resultados; não inventa links ou vídeo."""
from pathlib import Path
import json
WORK=Path(__file__).resolve().parent
def fmt(x,d=4):
    return f"{x:,.{d}f}".replace(",","X").replace(".",",").replace("X",".")
def value(r,x):
    return fmt(100*x,2)+"%" if r["tipo"]=="proporcao" else fmt(x)
def generate(b,inspection):
    d=b["desenho"];rs=b["testes"]
    def write(name,lines):
        (WORK/name).write_text("\n".join(lines).strip()+"\n",encoding="utf-8")
    lines=[
"# Sinistros registrados pela PRF: população e amostra de 2024","",
"Trabalho de Probabilidade e Estatística — IA003. Resultados reproduzíveis. A identificação do aluno e os links de entrega ainda devem ser preenchidos.","",
"## Pergunta, fonte e população","",
"Como estimativas obtidas em uma AAS de 2024 se comparam aos parâmetros da população completa de 2024 e às referências históricas fixas de 2023?","",
f"A população contém todas as **{d['N']} ocorrências** do CSV 2024, sem exclusões. A unidade amostral é **um sinistro registrado**, não uma pessoa ou veículo. 2023 é usado exclusivamente como referência histórica para H₀, sem entrar no sorteio ou nos painéis descritivos de 2024.","",
"A fonte oficial é a PRF, versão agrupada por ocorrência do BAT. A população não representa todos os sinistros brasileiros ou os não registrados. A proporção de sinistros com morte não é mortalidade entre pessoas; fim de semana não mede risco por viagem ou exposição ao tráfego.","",
"## Inspeção e tratamento antes do sorteio","",
"| Ano | Linhas de dados, sem cabeçalho | Colunas originais | IDs únicos | Ausências nas quatro variáveis |",
"| --- | ---: | ---: | ---: | ---: |"]
    for year in ["2024","2023"]:
        v=inspection[year]
        lines.append(f"| {year} | {v['linhas_dados']} | {v['colunas_originais']} | {v['ids_unicos']} | {sum(v['ausentes_variaveis_escolhidas'].values())} |")
    lines += ["",
"Leitura direta dos CSVs nos ZIPs: Windows-1252 (cp1252), ponto e vírgula, cabeçalho na primeira linha, decodificação estrita e sem pular linhas. ID preservado como texto. Datas no CSV são ISO (AAAA-MM-DD), diferença de apresentação em relação ao dd/mm/aaaa do dicionário de 2017.","",
"Conferidos: quantidade de campos de cada linha, unicidade e preenchimento de ID; datas no ano correto; correspondência do dia da semana; contagens inteiras não negativas; veículos ≥ 1; feridos = leves + graves.","",
"**Nenhuma exclusão, imputação, deduplicação, remoção ou suavização de extremos foi feita antes do sorteio.** As conversões de tipo preservam os valores. Foram apenas derivados os indicadores e campos de apoio. Ausências de outras colunas estão no arquivo de inspeção e não definem exclusões.","",
"| Campo | Definição utilizada | Dicionário |","| --- | --- | --- |",
"| id | Identificador da ocorrência | p. 3 |",
"| dia_semana | fim_semana = 1 em sábado/domingo, 0 nos demais | p. 3 |",
"| mortos | com_morte = 1 se houver pelo menos uma pessoa morta | p. 4 |",
"| feridos | Feridos leves + graves por ocorrência, incluindo zeros | p. 4 |",
"| veiculos | Veículos envolvidos por ocorrência | p. 4 |","",
"## Dimensionamento e AAS","",
f"Confiança 95%; z = {fmt(d['z'],8)}; E = 0,05 (5 pontos percentuais); p* = 0,50; N = {d['N']}.",
"",
"n₀ = z² p*(1−p*) / E²; n_finito = N n₀ / (N−1+n₀).","",
f"n₀ = {fmt(d['n0'],6)}; n_finito = {fmt(d['n_finito_antes_arredondamento'],6)}; **n = {d['n']}** após arredondar para cima. Margem máxima aproximada atingida: {fmt(100*d['margem_maxima_atingida_aproximada'],3)} pontos percentuais.","",
"O planejamento para proporções não assegura precisão específica para médias nem poder suficiente para qualquer diferença pequena.","",
f"Sorteio: numpy.random.default_rng({d['semente']}).choice(N, size=n, replace=False), gerador PCG64, ordem física do CSV original. Posições ordenadas apenas após seleção. Probabilidade de inclusão de cada elemento n/N = {fmt(d['probabilidade_inclusao'],8)}; fração amostral {fmt(100*d['fracao'],4)}%.","",
"IDs e posições foram salvos. A amostra é única e congelada para todos os painéis; o aplicativo não sorteia novamente. A reprodução depende dos ZIPs, da ordem dos registros, do algoritmo, da versão do NumPy e da semente. Hashes estão em resultados/inspecao.json.","",
"## Métodos e hipóteses","",
"São quatro testes bilaterais, α = 0,05 por teste, definidos antes dos resultados. Para cada variável: H₀: parâmetro2024 = valor calculado no CSV completo de 2023; H₁: parâmetro2024 ≠ referência2023. A referência de 2023 é uma constante histórica, sem erro-padrão estimado; não é um teste entre duas amostras.","",
"Apenas a amostra de 2024 fornece estimativas, variâncias e estatísticas dos testes. A população completa de 2024 fornece parâmetros descritivos para comparação e erro amostral observado, sem escolher hipóteses ou adaptar a amostra.","",
"### Proporções","",
"k = (N−n)/(N−1); EP₀ = √[k p₀(1−p₀)/n]; Z = (p̂−p₀)/EP₀; valor-p bilateral = 2 Φ(−|Z|). A aproximação normal incorpora a amostragem sem reposição e usa a proporção nula no erro-padrão do teste.","",
"O IC de escore com correção finita inverte |p̂−p| ≤ z √[k p(1−p)/n]. Com a = z²k/n, centro = (p̂+a/2)/(1+a) e semi-amplitude = √[a p̂(1−p̂)+a²/4]/(1+a). É uma extensão aproximada de Wilson, não intervalo hipergeométrico exato. Verificam-se contagens esperadas e observadas. p₀ histórico não precisa corresponder a um número inteiro de sucessos em N na aproximação normal.","",
"### Médias","",
"s² = Σ(xᵢ−x̄)²/(n−1); EP = √[(1−n/N)s²/n]; t = (x̄−μ₀)/EP. Referência aproximada t com n−1 graus de liberdade; IC95% = x̄ ± t₀,₉₇₅ EP.","",
"A dependência das seleções sem reposição é incorporada na variância. A distribuição t é aproximação de inferência para este desenho finito com contagens assimétricas, não uma garantia exata por n > 30. A fração amostral é baixa, então o efeito da correção finita é pequeno, mas foi aplicado consistentemente.","",
"## Resultados","",
"| Indicador | Referência 2023 | População 2024 | Amostra 2024 | IC95% da amostra | Estatística | Valor-p | Decisão 5% |",
"| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |"]
    for r in rs:
        lines.append(f"| {r['rotulo']} | {value(r,r['referencia_2023'])} | {value(r,r['populacao_2024'])} | {value(r,r['estimativa'])} | [{value(r,r['ic95'][0])}; {value(r,r['ic95'][1])}] | {r['estatistica_nome']} = {fmt(r['estatistica'])} | {fmt(r['p_valor'],6)} | {'Rejeitar H₀' if r['rejeita_h0'] else 'Não rejeitar H₀'} |")
    for r in rs:
        fac=100 if r["tipo"]=="proporcao" else 1
        unit="pontos percentuais" if fac==100 else "por sinistro"
        lines += ["",f"### {r['rotulo']}","",
f"Diferença populacional 2024 − 2023: {fmt(fac*r['diferenca_populacional_historica'])} {unit}. Erro amostral observado (estimativa − parâmetro2024): {fmt(fac*r['erro_amostral_observado'])} {unit}. O IC {'contém' if r['ic_cobre_populacao_2024'] else 'não contém'} o parâmetro conhecido de 2024 e {'contém' if r['ic_cobre_referencia_2023'] else 'não contém'} a referência de 2023.","",
("Há evidência amostral contra a igualdade com a referência histórica, sob as condições adotadas." if r["rejeita_h0"] else "A amostra não fornece evidência suficiente para rejeitar igualdade com a referência histórica. Isso não prova igualdade nem ausência de mudança.")+" A diferença realizada nos arquivos completos é conhecida descritivamente, independentemente da decisão do teste."]
        if r["tipo"]=="proporcao":
            lines += ["",f"Condições: {r['sucessos']} sucessos e {r['fracassos']} fracassos na amostra; esperados sob H₀: {fmt(r['esperados_h0'][0],2)} e {fmt(r['esperados_h0'][1],2)}. Critério de pelo menos 10 em cada contagem: {'atendido' if r['condicao_contagens_10'] else 'NÃO atendido; interpretar aproximação com cautela adicional'}."]
        else:
            bc=r["bootstrap_ic95_sensibilidade"]
            lines += ["",f"Diagnóstico: assimetria amostral {fmt(r['assimetria_amostra'],3)}, máximo {r['max_amostra']}, P95 {fmt(r['p95_amostra'],2)}; maior valor responde por {fmt(100*r['parcela_soma_maior_observacao'],2)}% da soma. Os dados brutos não são assumidos normais.","",
f"IC bootstrap de sensibilidade: [{fmt(bc[0])}; {fmt(bc[1])}], que {'contém' if r['bootstrap_cobre_referencia'] else 'não contém'} a referência. É diagnóstico aproximado, sem substituir o IC t definido previamente ou eliminar a fragilidade a extremos raros ausentes da amostra."]
    lines += ["","## Sensibilidade e limitações","",
"Para as duas médias: 10.000 reamostragens empíricas com reposição, semente separada 202405, ordem feridos/veiculos. Médias bootstrap centradas na estimativa e reescaladas por √[(1−n/N)n/(n−1)], compatibilizando a variância com a estimativa AAS. IC percentil aproximado, não bootstrap exato do desenho. Nenhum novo sorteio na população, nenhuma variância populacional usada.","",
"Os quatro testes primários usam 5% individualmente. Como sensibilidade à multiplicidade, aplica-se Holm com nível familiar 5%, sem escolher o resultado mais favorável:","",
"| Indicador | Valor-p | Valor-p Holm | Decisão Holm |","| --- | ---: | ---: | --- |"]
    for r in rs:
        lines.append(f"| {r['rotulo']} | {fmt(r['p_valor'],6)} | {fmt(r['p_holm_sensibilidade'],6)} | {'Rejeitar' if r['rejeita_holm_sensibilidade'] else 'Não rejeitar'} |")
    lines += ["",
"Valores extremos são mantidos: máximos de veículos 131 em 2023 e 26 em 2024; máximos de feridos 62 e 85. Os registros não foram auditados individualmente. Poucos eventos podem influenciar médias, e uma amostra de 383 pode não capturar caudas raras. O dimensionamento de proporções não garante precisão nem poder das médias.","",
"Os ICs são marginais, não simultâneos. Não se espera que exatamente 95% de apenas quatro ICs cubram os parâmetros. Significância não é relevância prática; não rejeitar H₀ não demonstra igualdade.","",
"Os arquivos completos permitem verificar diferenças realizadas, mas não causalidade. Composição dos registros, cobertura, exposição e práticas de registro podem mudar entre anos. Não se mede risco por quilômetro ou viagem e não se atribui causa às diferenças. A fonte pode ser revisada; o estudo vale para os ZIPs preservados.","",
"## Painéis e reprodução","",
"Painel 1: população2024. Painel 2: a mesma análise na amostra salva. Painel 3: referência2023, parâmetro2024, estimativa, IC e teste. Filtros exploratórios descritivos não alteram o sorteio ou os testes.","",
"Executar python analise.py regenera inspeção, amostra, resultados e documentação. Executar python iniciar_paineis.py abre os painéis locais. Publicação externa continua pendente.","",
"## Fontes","",
"- [PRF: catálogo oficial]("+b["fontes"]["catalogo"]+"), arquivos obtidos em 05/11/2026.",
"- [ZIP 2024]("+b["fontes"]["2024"]+") e [ZIP 2023]("+b["fontes"]["2023"]+").",
"- [Dicionário oficial]("+b["fontes"]["dicionario"]+"), PDF 2017 indicado para registros a partir de 2017; cópia local em fontes/.",
"- [Penn State STAT 506](https://online.stat.psu.edu/stat506/Lesson02): apoio a AAS, variância e população finita. A inversão do escore com FPC foi explicitada neste relatório.",
"- [SciPy normal](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html) e [t](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.t.html): referências numéricas.",
"- Enunciado local: ../prova_final.txt. Não há prazo indicado no enunciado.","",
"Ambiente: "+json.dumps(b["ambiente"],ensure_ascii=False)+"."]
    write("RELATORIO.md",lines)
    video=["# Roteiro para vídeo de até 5 minutos","",
"Meta: 4min40s com margem para transições. Roteiro para o aluno gravar; nenhum vídeo foi criado ou publicado.","",
"## 0:00–0:35 — Contexto (painel 1)","",
f"Analisei os sinistros registrados pela PRF nas rodovias federais. A população de 2024 contém {d['N']} ocorrências, com 30 colunas e IDs únicos. A unidade é um sinistro, não uma pessoa. O ano de 2023 fornece somente referências históricas. Não estou estimando risco por viagem.","",
"## 0:35–1:15 — AAS e dimensionamento","",
f"Conferi ausências, IDs, datas e contagens. Não excluí ocorrências ou extremos. Usei confiança 95%, margem de cinco pontos percentuais, p de 0,50 e correção finita. O tamanho final foi {d['n']}. Sorteei sem reposição com semente 2024, salvando os IDs para reproduzir a mesma amostra.","",
"## 1:15–2:00 — População e amostra (painéis 1 e 2)","",
"Mostrar proporções de fim de semana e ocorrência com morte, médias de feridos e veículos e distribuições. Explicar que as mesmas escalas permitem comparar as duas bases. A variação amostral é esperada; extremos podem influenciar as médias.","",
"## 2:00–3:40 — Quatro testes (painel 3)","",
"Cada teste é bilateral e compara o parâmetro2024 com a referência fixa de 2023, a 5%. Usei Z com escore para proporções e t aproximado para médias, incorporando a correção finita. A inferência usa só a amostra; o parâmetro2024 é exibido para comparação.",""]
    for r in rs:
        video.append(f"- **{r['rotulo']}**: referência {value(r,r['referencia_2023'])}; população {value(r,r['populacao_2024'])}; amostra {value(r,r['estimativa'])}; IC [{value(r,r['ic95'][0])}; {value(r,r['ic95'][1])}]; valor-p {fmt(r['p_valor'])}. {'Rejeitamos' if r['rejeita_h0'] else 'Não rejeitamos'} H₀.")
    video += ["",
"Manter a tabela visível e priorizar interpretação, sem ler todos os números.","",
"## 3:40–4:25 — Limitações","",
"Não rejeitar não prova igualdade. Os parâmetros completos mostram diferenças realizadas que a amostra pode não detectar. Há aproximação nos testes, assimetria, extremos, quatro comparações e ICs marginais. Holm e bootstrap são apenas sensibilidades. Não atribuo causalidade nem mudanças de risco individual aos resultados.","",
"## 4:25–4:40 — Encerramento","",
"As fontes, o código e os IDs estão documentados. A comparação com a população permite avaliar esta realização amostral. Os links dos painéis, vídeo e dados serão incluídos na entrega.","",
"## Antes de gravar","",
"- Inserir nome e turma, se necessário.",
"- Ensaiar com cronômetro e reduzir a fala caso ultrapasse cinco minutos.",
"- Confirmar que a tela mostra os resultados da amostra salva.",
"- Publicar o vídeo e conferir os links sem autenticação."]
    write("ROTEIRO_VIDEO.md",video)
    write("ENTREGA.md",["# Checklist de entrega","",
"- [x] Fontes oficiais, inspeção, amostra salva, quatro testes e relatório.",
"- [x] Roteiro do vídeo preparado.",
"- [ ] Conferir o relatório de QA dos painéis.",
"- [ ] Identificar aluno/turma, se necessário.",
"- [ ] Definir/publicar hospedagem dos painéis (ponto em aberto).",
"- [ ] Gravar vídeo de até cinco minutos e publicar no YouTube.",
"- [ ] Testar todos os links sem pedido de autorização.","",
"## Links para submissão","",
"- Painéis: **PENDENTE — não há publicação externa nesta etapa.**",
"- Vídeo: **PENDENTE — depende de gravação e publicação.**",
"- Base original 2024: "+b["fontes"]["2024"],
"- Referência histórica 2023: "+b["fontes"]["2023"],
"- Fonte oficial PRF: "+b["fontes"]["catalogo"],"",
"Endereços 127.0.0.1 funcionam somente no computador local e não atendem à entrega externa."])
