"""Três painéis Streamlit, sem sorteio durante a navegação."""
from pathlib import Path
import sys,os
WORK=Path(__file__).resolve().parent
vendor=Path(os.environ.get("PRF_RUNTIME_DIR",str(WORK.parents[2]/"site/ferramentas/vendor")))
if vendor.is_dir(): sys.path.insert(0,str(vendor))
import json
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from analise import load_year,DAYS,VARIABLES

st.set_page_config(page_title="Sinistros PRF | IA003",page_icon="📊",layout="wide")
st.markdown("""
<style>
.stApp { background: #f5f6f8; }
h1,h2,h3 {color:#25364b;}
[data-testid="stMetric"] {background:white;border:1px solid #dce2e9;border-radius:12px;padding:15px;}
[data-testid="stTabs"] button {font-weight:600;}
</style>
""",unsafe_allow_html=True)
if not (WORK/"resultados/analise.json").exists():
    st.error("Resultados ainda não gerados. Execute python analise.py antes de abrir os painéis.")
    st.stop()

@st.cache_data
def data(stamp):
    pop,_=load_year(2024)
    sample=pd.read_csv(WORK/"dados/amostra_2024.csv",sep=";",encoding="utf-8-sig",dtype={"id":str})
    b=json.loads((WORK/"resultados/analise.json").read_text(encoding="utf-8"))
    assert len(sample)==b["desenho"]["n"] and sample.id.is_unique
    return pop,sample,b
pop,sample,b=data(tuple((WORK/name).stat().st_mtime_ns for name in ["datatran2024.zip","dados/amostra_2024.csv","resultados/analise.json"]))
design=b["desenho"]
def fmt(x,d=2):
    return f"{x:,.{d}f}".replace(",","X").replace(".",",").replace("X",".")
def metric_value(r,x):
    return fmt(100*x)+"%" if r["tipo"]=="proporcao" else fmt(x,3)
def chart_style(fig,title,xlabel="",ylabel=""):
    fig.update_layout(title=title,xaxis_title=xlabel,yaxis_title=ylabel,
        template="plotly_white",font={"family":"Arial","color":"#25364b"},
        margin={"l":15,"r":15,"t":55,"b":25},height=340,
        paper_bgcolor="white",plot_bgcolor="white")
    return fig
def frequencies(df,col,levels):
    counts=df[col].value_counts().reindex(levels,fill_value=0)
    return counts.to_numpy(),100*counts.to_numpy()/len(df)
def bars(df,col,levels,title,key,color,labels=None):
    counts,pcts=frequencies(df,col,levels)
    fig=go.Figure(go.Bar(x=labels or levels,y=pcts,marker_color=color,customdata=counts,
        hovertemplate="%{x}<br>%{y:.2f}%<br>%{customdata} sinistros<extra></extra>"))
    chart_style(fig,title,ylabel="Percentual de sinistros (%)")
    fig.update_yaxes(range=[0,100])
    fig.update_xaxes(tickangle=-25)
    st.plotly_chart(fig,width="stretch",key=key)
def descriptive(df,prefix,title,color,ddof):
    st.subheader(title)
    st.caption("Universo: registros PRF de 2024. A unidade é um sinistro; percentuais não são risco por viagem.")
    c1,c2=st.columns([1,2])
    uf=c1.selectbox("Unidade da Federação",["Todas",*sorted(pop.uf.unique())],key=prefix+"_uf")
    months=c2.slider("Meses de 2024",1,12,(1,12),key=prefix+"_months")
    mask=df.mes.between(*months)
    if uf!="Todas": mask &= df.uf.eq(uf)
    sub=df.loc[mask]
    st.caption(f"Recorte exibido: {len(sub):,} de {len(df):,} sinistros. Filtros são exploratórios; não refazem amostra, ICs ou testes.".replace(",","."))
    if sub.empty:
        st.info("Nenhum sinistro neste recorte. Amplie os filtros.")
        return
    m=st.columns(5)
    m[0].metric("Sinistros",fmt(len(sub),0))
    m[1].metric("Sábado ou domingo",fmt(100*sub.fim_semana.mean())+"%")
    m[2].metric("Com pelo menos uma morte",fmt(100*sub.com_morte.mean())+"%")
    m[3].metric("Feridos por sinistro",fmt(sub.feridos.mean(),3))
    m[4].metric("Veículos por sinistro",fmt(sub.veiculos.mean(),3))
    left,right=st.columns(2)
    with left: bars(sub,"dia_semana",DAYS,"Distribuição por dia da semana",prefix+"_days",color)
    with right: bars(sub,"com_morte",[0,1],"Ocorrências com ou sem morte",prefix+"_fatal",color,["Sem morte","Com morte"])
    left,right=st.columns(2)
    for area,col,label in [(left,"feridos","Feridos"),(right,"veiculos","Veículos")]:
        with area:
            # Agrega apenas a visualização da cauda, sem alterar valores numéricos.
            temporary=sub.assign(faixa=sub[col].clip(upper=10))
            bars(temporary,"faixa",list(range(11)),label+" por sinistro",prefix+"_"+col,color,[str(i) for i in range(10)]+["10+"])
    st.caption("Nas distribuições, 10+ reúne toda a cauda a partir de dez. Os valores extremos continuam nos indicadores e tabelas. Todas as escalas percentuais vão de 0% a 100% nos dois painéis.")
    records=[]
    for col,label in [("feridos","Feridos"),("veiculos","Veículos")]:
        x=sub[col]
        records.append({"Variável":label,"N":len(x),"Média":x.mean(),"Mediana":x.median(),
            "Desvio-padrão":x.std(ddof=ddof) if len(x)>ddof else None,
            "Mínimo":x.min(),"Q1":x.quantile(.25),"Q3":x.quantile(.75),"P95":x.quantile(.95),"Máximo":x.max()})
    st.markdown("**Medidas descritivas, com os valores extremos preservados**")
    st.dataframe(pd.DataFrame(records),hide_index=True,width="stretch")
    st.caption("Desvio-padrão: divisor N no painel populacional; divisor n−1 no painel amostral. Pequenos recortes podem não ter desvio-padrão definido.")
    monthly=sub.mes.value_counts().reindex(range(1,13),fill_value=0)
    fig=go.Figure(go.Scatter(x=list(range(1,13)),y=100*monthly/len(sub),mode="lines+markers",
        line={"color":color},customdata=monthly,hovertemplate="Mês %{x}<br>%{y:.2f}%<br>%{customdata} sinistros<extra></extra>"))
    chart_style(fig,"Distribuição mensal do recorte",xlabel="Mês de 2024",ylabel="Percentual (%)")
    fig.update_xaxes(dtick=1);fig.update_yaxes(range=[0,100])
    st.plotly_chart(fig,width="stretch",key=prefix+"_monthly")
    with st.expander("Consultar registros do recorte"):
        st.dataframe(sub[["id","data_inversa","dia_semana","uf","mortos","feridos","veiculos"]],hide_index=True,width="stretch")
st.title("Sinistros nas rodovias federais")
st.markdown("**PRF · 2024** — da população à amostra, com referência histórica de 2023")
sample_size_help = (
    "**Dimensionamento da amostra para proporções**\n\n"
    "Com correção para população finita:\n\n"
    "n = N × z² × p × (1 − p) / [(N − 1) × E² + z² × p × (1 − p)]\n\n"
    f"- N = {fmt(design['N'], 0)} sinistros (população).\n"
    f"- Confiança = {fmt(100 * design['confianca'], 0)}%; z ≈ {fmt(design['z'], 5)}.\n"
    f"- E = {fmt(design['margem_planejada'])}: margem de {fmt(100 * design['margem_planejada'], 0)} pontos percentuais.\n"
    f"- p = {fmt(design['p_planejamento'])}: proporção conservadora de planejamento.\n\n"
    f"Resultado: {fmt(design['n_finito_antes_arredondamento'], 4)}; "
    f"arredondando para cima, **{design['n']} sinistros**.\n\n"
    "AAS significa amostra aleatória simples, selecionada sem reposição. "
    "Este planejamento para proporções não garante a mesma precisão para médias."
)
st.caption(f"População: {design['N']:,} ocorrências · Semente {design['semente']} · IC 95% · α = 5% por teste".replace(",","."))
st.caption(f"Tamanho da amostra (AAS): {design['n']} sinistros", help=sample_size_help)
tabs=st.tabs(["1 · População 2024","2 · Amostra 2024","3 · Inferência e comparação"])
with tabs[0]:
    descriptive(pop,"pop","Painel 1 — População de estudo","#1f5d88",0)
with tabs[1]:
    st.info(f"Amostra fixa de {design['n']} sinistros, sorteada sem reposição. Os filtros não sorteiam novas observações.")
    descriptive(sample,"sample","Painel 2 — A mesma análise na amostra","#c8343b",1)
    st.download_button("Baixar a amostra e seus IDs",(WORK/"dados/amostra_2024.csv").read_bytes(),"amostra_2024.csv","text/csv",key="download_sample")
with tabs[2]:
    st.subheader("Painel 3 — Referência, parâmetro e estimativa")
    st.caption("Resultados da amostra completa salva. Os filtros dos painéis 1 e 2 não afetam esta análise.")
    options=[r["variavel"] for r in b["testes"]]
    key=st.selectbox("Indicador inferencial",options,format_func=lambda k:VARIABLES[k][0],key="inference_variable")
    r=next(r for r in b["testes"] if r["variavel"]==key)
    hypothesis_subjects = {
        "fim_semana": "a proporção de sinistros ocorridos no sábado ou domingo",
        "com_morte": "a proporção de sinistros com pelo menos uma pessoa morta",
        "feridos": "a média de feridos leves e graves por sinistro, incluindo ocorrências sem feridos",
        "veiculos": "a média de veículos envolvidos por sinistro",
    }
    subject = hypothesis_subjects[key]
    reference = metric_value(r, r["referencia_2023"])
    parameter_help = (
        "p representa uma proporção populacional. "
        if r["tipo"] == "proporcao" else
        "μ (mu) representa uma média populacional. "
    )
    null_help = (
        "**H₀ — hipótese nula**\n\n"
        f"Neste indicador, H₀ afirma que {subject} em 2024 é igual à referência histórica de 2023: **{reference}** (valor arredondado).\n\n"
        + parameter_help +
        "A referência foi calculada no arquivo completo de 2023 e é tratada como fixa. "
        "O teste usa a amostra de 2024 para avaliar a compatibilidade com essa hipótese; "
        "não é uma comparação entre duas amostras."
    )
    alternative_help = (
        "**H₁ — hipótese alternativa**\n\n"
        f"Neste indicador, H₁ afirma que {subject} em 2024 é diferente da referência histórica de 2023: **{reference}** (valor arredondado).\n\n"
        "A diferença pode ser para mais ou para menos, por isso o teste é bilateral. "
        "A hipótese se refere à população; a amostra fornece a evidência para avaliá-la."
    )
    hypotheses = st.columns(2)
    hypotheses[0].markdown("**H₀:** " + r["hipotese_nula"], help=null_help)
    hypotheses[1].markdown("**H₁:** " + r["hipotese_alternativa"], help=alternative_help)
    c=st.columns(3)
    c[0].metric("Referência fixa · 2023",metric_value(r,r["referencia_2023"]))
    c[1].metric("População completa · 2024",metric_value(r,r["populacao_2024"]))
    c[2].metric("Estimativa da amostra · 2024",metric_value(r,r["estimativa"]))
    factor=100 if r["tipo"]=="proporcao" else 1
    values=[r["referencia_2023"],r["populacao_2024"],r["estimativa"]]
    lo,hi=r["ic95"]
    fig=go.Figure()
    labels=["Referência histórica 2023","Parâmetro populacional 2024","Estimativa amostral 2024"]
    for i,(label,point,color) in enumerate(zip(labels,values,["#667085","#1f5d88","#c8343b"])):
        fig.add_trace(go.Scatter(x=[factor*point],y=[label],mode="markers",
            marker={"size":14,"color":color},name=label,
            error_x={"type":"data","array":[factor*(hi-point) if i==2 else 0],
                "arrayminus":[factor*(point-lo) if i==2 else 0],"visible":i==2,"color":color},
            hovertemplate=label+"<br>%{x:.4f}<extra></extra>"))
    chart_style(fig,"Comparação com IC de 95% da estimativa",xlabel="Percentual de sinistros (%)" if factor==100 else "Média por sinistro")
    fig.update_layout(showlegend=False);fig.update_yaxes(categoryorder="array",categoryarray=labels[::-1])
    st.plotly_chart(fig,width="stretch",key="inference_ci")
    st.caption("A barra horizontal é o IC amostral. Os outros dois pontos são calculados nos arquivos completos, tratados como valores conhecidos neste exercício.")
    estimate = r["estimativa"]
    reference_value = r["referencia_2023"]
    n, N = r["n"], r["N"]
    if r["tipo"] == "proporcao":
        k = (N - n) / (N - 1)
        a = design["z"] ** 2 * k / n
        center = (estimate + a / 2) / (1 + a)
        half_width = np.sqrt(a * estimate * (1 - estimate) + a * a / 4) / (1 + a)
        interval_calculation = (
            "IC de escore (Wilson aproximado), com correção para população finita. "
            "p̂ é a proporção amostral; z ≈ 1,96; k = (N − n)/(N − 1); a = z²k/n.\n\n"
            "Centro = (p̂ + a/2)/(1 + a).\n\n"
            "Margem = √[a × p̂ × (1 − p̂) + a²/4]/(1 + a).\n\n"
            f"Aqui, p̂ = {fmt(estimate, 6)}, n = {n}, N = {N}; "
            f"centro = {fmt(100 * center, 4)}% e margem = {fmt(100 * half_width, 4)} pontos percentuais. "
            "Os limites são centro − margem e centro + margem."
        )
        standard_error = r["erro_padrao_h0"]
        statistic_calculation = (
            "Z = (p̂ − p₀)/EP₀, com EP₀ = √[k × p₀ × (1 − p₀)/n]. "
            "p₀ é a proporção histórica de 2023; k = (N − n)/(N − 1).\n\n"
            f"Z = ({fmt(estimate, 6)} − {fmt(reference_value, 6)}) / "
            f"{fmt(standard_error, 6)} ≈ {fmt(r['estatistica'], 4)}."
        )
        probability_calculation = "Valor-p = 2 × [1 − Φ(|Z|)], em que Φ é a função de distribuição da normal padrão."
    else:
        from scipy.stats import t as student_t
        critical = student_t.ppf(0.975, r["graus_liberdade"])
        standard_error = r["erro_padrao"]
        interval_calculation = (
            "IC aproximado para a média: x̄ ± t crítico × EP. "
            "x̄ é a média amostral; EP = √[(1 − n/N) × s²/n]; s é o desvio-padrão amostral.\n\n"
            f"Com n = {n}, N = {N}, s = {fmt(r['dp_amostral'], 6)}, "
            f"EP = {fmt(standard_error, 6)} e {r['graus_liberdade']} graus de liberdade: "
            f"{fmt(estimate, 6)} ± {fmt(critical, 6)} × {fmt(standard_error, 6)}."
        )
        statistic_calculation = (
            "Para médias usamos t, em vez de Z, pois o erro-padrão é estimado com o desvio-padrão da amostra. "
            "t = (x̄ − μ₀)/EP; EP = √[(1 − n/N) × s²/n]. μ₀ é a média histórica de 2023.\n\n"
            f"t = ({fmt(estimate, 6)} − {fmt(reference_value, 6)}) / "
            f"{fmt(standard_error, 6)} ≈ {fmt(r['estatistica'], 4)}, "
            f"com {r['graus_liberdade']} graus de liberdade."
        )
        probability_calculation = (
            f"Valor-p = 2 × [1 − Fₜ(|t|)], usando a distribuição t com {r['graus_liberdade']} "
            "graus de liberdade. Fₜ é sua função de distribuição acumulada."
        )
    ic_help = (
        f"**IC 95%: {metric_value(r, lo)} a {metric_value(r, hi)}**\n\n"
        "Expressa a incerteza da estimativa do parâmetro de 2024 com base apenas na amostra. "
        "Em repetições da amostragem, este procedimento aproximado cobre o parâmetro em cerca de 95% dos casos. "
        "Não é uma faixa contendo 95% dos sinistros.\n\n"
        + interval_calculation + "\n\nOs valores mostrados no cálculo estão arredondados; "
        "os resultados usam precisão completa. IC individual, não simultâneo para os quatro indicadores."
    )
    statistic_help = (
        "A estatística mede a distância entre a estimativa amostral e a referência de 2023 em unidades de erro-padrão. "
        "Sinal negativo indica estimativa menor; positivo, maior. Quanto maior o valor absoluto, maior a distância.\n\n"
        + statistic_calculation + "\n\nA correção finita considera o sorteio sem reposição. O teste é aproximado."
    )
    p_value_help = (
        "Sob H₀ e as condições do método, é a probabilidade de obter uma estatística tão extrema quanto a observada "
        "ou mais, em qualquer uma das duas direções. Não é a probabilidade de H₀ ser verdadeira.\n\n"
        + probability_calculation +
        f"\n\nPara {r['estatistica_nome']} = {fmt(r['estatistica'], 4)}, "
        f"o resultado é **{fmt(r['p_valor'], 6)}**, aproximadamente **{fmt(100 * r['p_valor'], 2)}%**. "
        "Multiplicamos a probabilidade de uma cauda por dois porque o teste é bilateral."
    )
    decision_help = (
        "**Decisão por comparação do valor-p com α**\n\n"
        "α = 0,05 é o nível de significância escolhido antes dos resultados. "
        "Ele fixa em aproximadamente 5% o risco de rejeitar H₀ quando ela é verdadeira, por teste, sob as condições do método.\n\n"
        "Regra: valor-p ≤ 0,05 → rejeitar H₀; valor-p > 0,05 → não rejeitar H₀.\n\n"
        f"Aqui: {fmt(r['p_valor'], 6)} "
        + ("≤" if r["rejeita_h0"] else ">") + " 0,05. "
        + ("Há evidência amostral contra a igualdade com a referência histórica."
           if r["rejeita_h0"] else
           "Não há evidência amostral suficiente para rejeitar a igualdade com a referência histórica. "
           "Isso não prova igualdade: a amostra pode não detectar diferenças pequenas.")
        + "\n\nNão é uma probabilidade de 95% de a decisão estar correta. "
        "O nível de 5% é individual; o ajuste de Holm para os quatro testes aparece em Método, condições e sensibilidade."
    )
    c=st.columns(4)
    c[0].metric("IC 95%",f"{metric_value(r,lo)} a {metric_value(r,hi)}", help=ic_help)
    c[1].metric("Estatística "+r["estatistica_nome"],fmt(r["estatistica"],4), help=statistic_help)
    c[2].metric("Valor-p bilateral",fmt(r["p_valor"],6), help=p_value_help)
    c[3].metric("Decisão · α = 0,05","Rejeitar H₀" if r["rejeita_h0"] else "Não rejeitar H₀", help=decision_help)
    if r["rejeita_h0"]:
        st.warning("Há evidência amostral contra a igualdade com a referência histórica, sob as condições adotadas. Isso não demonstra causalidade.")
    else:
        st.info("Não há evidência amostral suficiente para rejeitar igualdade com a referência histórica. Isso não comprova igualdade ou ausência de mudança.")
    unit="p.p." if factor==100 else "por sinistro"
    st.write(f"Diferença populacional 2024 − 2023: **{fmt(factor*r['diferenca_populacional_historica'],4)} {unit}**. Erro amostral observado: **{fmt(factor*r['erro_amostral_observado'],4)} {unit}**.")
    st.write("O IC "+("contém" if r["ic_cobre_populacao_2024"] else "não contém")+" o parâmetro conhecido de 2024 nesta realização.")
    with st.expander("Método, condições e sensibilidade"):
        st.write(r["metodo"])
        if r["tipo"]=="proporcao":
            st.write(f"Sucessos/fracassos: {r['sucessos']}/{r['fracassos']}. Esperados sob H₀: {fmt(r['esperados_h0'][0])}/{fmt(r['esperados_h0'][1])}. Contagens mínimas de dez: "+("atendidas." if r["condicao_contagens_10"] else "não atendidas."))
            st.latex(r"Z=\frac{\hat p-p_0}{\sqrt{\frac{N-n}{N-1}\frac{p_0(1-p_0)}{n}}}")
            st.caption("IC de escore com FPC obtido por inversão, aproximação de Wilson; não é intervalo hipergeométrico exato.")
        else:
            st.write(f"DP amostral {fmt(r['dp_amostral'],3)}; assimetria {fmt(r['assimetria_amostra'],3)}; máximo {r['max_amostra']}; graus de liberdade {r['graus_liberdade']}.")
            st.latex(r"t=\frac{\bar x-\mu_0}{\sqrt{(1-n/N)s^2/n}}")
            bc=r["bootstrap_ic95_sensibilidade"]
            st.write(f"IC bootstrap aproximado, somente sensibilidade: {fmt(bc[0],4)} a {fmt(bc[1],4)}. Dez mil reamostragens empíricas centradas/reescaladas. Não garante robustez a caudas raras não observadas.")
        st.write(f"Holm, sensibilidade para quatro testes: valor-p ajustado {fmt(r['p_holm_sensibilidade'],6)}; "+("rejeitar H₀." if r["rejeita_holm_sensibilidade"] else "não rejeitar H₀."))
        st.caption("Os ICs são marginais de 95%. O planejamento de proporções não garante a precisão das médias. Testes e intervalos são aproximados.")
    st.markdown("**Resumo dos quatro testes**")
    table=[]
    for item in b["testes"]:
        table.append({"Indicador":item["rotulo"],"Referência2023":metric_value(item,item["referencia_2023"]),
            "População2024":metric_value(item,item["populacao_2024"]),"Amostra2024":metric_value(item,item["estimativa"]),
            "IC95%":f"{metric_value(item,item['ic95'][0])} a {metric_value(item,item['ic95'][1])}",
            "Valor-p":item["p_valor"],"Decisão":"Rejeitar H₀" if item["rejeita_h0"] else "Não rejeitar H₀"})
    st.dataframe(pd.DataFrame(table),hide_index=True,width="stretch")
    c1,c2=st.columns(2)
    c1.download_button("Baixar resultados dos testes",(WORK/"resultados/testes.csv").read_bytes(),"testes.csv","text/csv")
    c2.download_button("Baixar relatório completo",(WORK/"RELATORIO.md").read_bytes(),"RELATORIO.md","text/markdown")
    with st.expander("Inspeção e desenho amostral"):
        st.json(design)
        inspection=json.loads((WORK/"resultados/inspecao.json").read_text(encoding="utf-8"))
        st.dataframe(pd.DataFrame([{"Ano":y,"Linhas":inspection[y]["linhas_dados"],"Colunas":inspection[y]["colunas_originais"],
            "IDs únicos":inspection[y]["ids_unicos"],"Exclusões":inspection[y]["linhas_excluidas"]} for y in ["2024","2023"]]),hide_index=True)
st.divider()
st.markdown("**Fonte:** [Dados abertos PRF]("+b["fontes"]["catalogo"]+") · [2024]("+b["fontes"]["2024"]+") · [Referência 2023]("+b["fontes"]["2023"]+") · [Dicionário]("+b["fontes"]["dicionario"]+")")
st.caption("Arquivos preservados em 05/11/2026. Sem exclusões ou imputação. Esta análise descreve registros; não estima risco por viagem nem efeitos causais. Publicação externa ainda não definida.")
