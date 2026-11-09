"""Análise reproduzível de população finita PRF. Não modifica fontes."""
from pathlib import Path
import sys, os
WORK = Path(__file__).resolve().parent
VENDOR = Path(os.environ.get("PRF_RUNTIME_DIR", str(WORK.parents[2] / "site/ferramentas/vendor")))
if VENDOR.is_dir():
    sys.path.insert(0, str(VENDOR))
import csv, io, zipfile, hashlib, json, math, platform
from datetime import date
import numpy as np
import pandas as pd
from scipy import stats

SEED, ALPHA, MARGIN, PLAN_P = 2024, 0.05, 0.05, 0.50
BOOT_SEED, BOOT_B = 202405, 10000
DAYS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
VARIABLES = {
    "fim_semana": ("Sinistros no fim de semana", "proporcao"),
    "com_morte": ("Sinistros com pelo menos uma morte", "proporcao"),
    "feridos": ("Feridos por sinistro", "media"),
    "veiculos": ("Veículos por sinistro", "media"),
}
SOURCES = {
    "catalogo": "https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf",
    "dicionario": "https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dicionario-acidentes",
    "2024": "https://drive.google.com/file/d/14lB0vqMFkaZj8HZ44b0njYgxs9nAN8KO/view",
    "2023": "https://drive.google.com/file/d/1-WO3SfNrwwZ5_l7fRTiwBKRw7mi1-HUq/view",
    "dicionario_pdf": "https://drive.google.com/file/d/11pXLw_0D0hHVS8fiC8cv2dPX39vpuOH1/view",
}
def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
def load_year(year):
    """Valida o CSV bruto antes de adicionar variáveis, sem excluir linhas."""
    path = WORK / f"datatran{year}.zip"
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        raw = z.read(f"datatran{year}.csv")
    text = raw.decode("cp1252", errors="strict")
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    columns = reader.fieldnames
    rows = list(reader)
    irregular = sum(None in r or any(v is None for v in r.values()) for r in rows)
    assert not irregular, "CSV com linhas irregulares: exige revisão antes do sorteio"
    df = pd.DataFrame(rows)
    missing = {c: int(df[c].str.strip().eq("").sum()) for c in columns}
    selected = ["dia_semana", "mortos", "feridos", "veiculos"]
    assert all(missing[c] == 0 for c in ["id", *selected]), "Ausência em variável de análise"
    assert df.id.is_unique, "Identificador duplicado: exige decisão antes do sorteio"
    assert df.dia_semana.isin(DAYS).all()
    for c in ["mortos", "feridos", "veiculos", "feridos_leves", "feridos_graves", "pessoas"]:
        val = pd.to_numeric(df[c], errors="raise")
        assert np.isfinite(val).all() and (val >= 0).all() and (val % 1 == 0).all(), c
        df[c] = val.astype("int64")
    assert (df.veiculos >= 1).all()
    assert (df.feridos == df.feridos_leves + df.feridos_graves).all()
    parsed = pd.to_datetime(df.data_inversa, format="%Y-%m-%d", errors="raise")
    assert parsed.dt.year.eq(year).all()
    assert all(DAYS[d.weekday()] == name for d, name in zip(parsed, df.dia_semana))
    info = {
        "ano": year, "linhas_dados": len(df), "colunas_originais": len(columns),
        "colunas": columns, "separador": ";", "encoding": "cp1252",
        "linhas_irregulares": irregular, "ids_unicos": int(df.id.nunique()),
        "id_ausente": missing["id"], "ausentes_todas_colunas": missing,
        "ausentes_variaveis_escolhidas": {c: missing[c] for c in selected},
        "datas_validas_e_ano_correto": True, "dias_correspondem_datas": True,
        "feridos_igual_leves_mais_graves": True,
        "limites_numericos": {c: {"min": int(df[c].min()), "max": int(df[c].max())} for c in selected[1:]},
        "linhas_excluidas": 0, "imputacoes": 0, "duplicatas_removidas": 0,
        "tratamento": "Nenhuma exclusão, imputação, deduplicação, winsorização ou alteração dos valores originais.",
        "sha256_zip": hashlib.sha256(path.read_bytes()).hexdigest(),
        "sha256_csv_interno": hashlib.sha256(raw).hexdigest(),
        "primeira_data": str(parsed.min().date()), "ultima_data": str(parsed.max().date()),
    }
    df["fim_semana"] = df.dia_semana.isin(["sábado", "domingo"]).astype("int64")
    df["com_morte"] = (df.mortos >= 1).astype("int64")
    df["mes"] = parsed.dt.month
    df["posicao_csv"] = np.arange(len(df))  # zero-based; cabeçalho excluído
    return df, info

def proportion_interval(phat, n, N, alpha=ALPHA):
    """Inversão do escore normal, com correção finita k=(N-n)/(N-1). Aproximado."""
    k = (N-n)/(N-1)
    z = stats.norm.ppf(1-alpha/2)
    a = z*z*k/n
    center = (phat+a/2)/(1+a)
    half = math.sqrt(a*phat*(1-phat)+a*a/4)/(1+a)
    return [max(0.0, center-half), min(1.0, center+half)]

def holm(pvalues):
    m = len(pvalues)
    order = np.argsort(pvalues)
    adjusted = np.empty(m)
    previous = 0.0
    for rank, i in enumerate(order):
        previous = max(previous, min(1., (m-rank)*pvalues[i]))
        adjusted[i] = previous
    return adjusted.tolist()

def summary(df, ddof):
    data = {}
    for key, (label, kind) in VARIABLES.items():
        x = df[key]
        data[key] = {"rotulo": label, "tipo": kind, "n": len(x), "estimativa": float(x.mean())}
        if kind == "proporcao":
            data[key].update({"sucessos": int(x.sum()), "fracassos": int(len(x)-x.sum())})
        else:
            data[key].update({
                "soma": int(x.sum()), "mediana": float(x.median()),
                "dp": float(x.std(ddof=ddof)), "variancia": float(x.var(ddof=ddof)),
                "min": int(x.min()), "q1": float(x.quantile(.25)),
                "q3": float(x.quantile(.75)), "p95": float(x.quantile(.95)),
                "max": int(x.max()), "assimetria": float(stats.skew(x, bias=False)),
            })
    return data

def compute_tests(pop, historical, sample):
    N, n = len(pop), len(sample)
    k = (N-n)/(N-1)
    rng = np.random.default_rng(BOOT_SEED)
    results = []
    for key, (label, kind) in VARIABLES.items():
        x = sample[key].to_numpy(dtype=float)
        theta0, thetaN, estimate = float(historical[key].mean()), float(pop[key].mean()), float(x.mean())
        r = {"variavel": key, "rotulo": label, "tipo": kind, "n": n, "N": N,
             "referencia_2023": theta0, "populacao_2024": thetaN, "estimativa": estimate,
             "diferenca_amostra_referencia": estimate-theta0, "erro_amostral_observado": estimate-thetaN,
             "diferenca_populacional_historica": thetaN-theta0, "alpha": ALPHA,
             "hipotese_nula": f"{'p' if kind=='proporcao' else 'μ'}2024 = {'p' if kind=='proporcao' else 'μ'}2023",
             "hipotese_alternativa": f"{'p' if kind=='proporcao' else 'μ'}2024 ≠ {'p' if kind=='proporcao' else 'μ'}2023"}
        if kind == "proporcao":
            se0 = math.sqrt(k*theta0*(1-theta0)/n)
            statistic = (estimate-theta0)/se0
            pvalue = 2*stats.norm.sf(abs(statistic))
            ci = proportion_interval(estimate, n, N)
            successes = int(x.sum())
            r.update({
                "metodo": "Z de uma proporção com FPC sob H0; IC de escore (Wilson) com FPC, ambos aproximados",
                "estatistica_nome": "Z", "estatistica": float(statistic), "p_valor": float(pvalue),
                "erro_padrao_h0": se0, "sucessos": successes, "fracassos": n-successes,
                "esperados_h0": [n*theta0, n*(1-theta0)], "condicao_contagens_10": min(successes,n-successes,n*theta0,n*(1-theta0)) >= 10,
                "ic95": ci, "k_fpc": k,
            })
        else:
            s = float(x.std(ddof=1))
            se = math.sqrt((1-n/N)*s*s/n)
            statistic = (estimate-theta0)/se
            pvalue = 2*stats.t.sf(abs(statistic), df=n-1)
            ci = [estimate-stats.t.ppf(.975,n-1)*se, estimate+stats.t.ppf(.975,n-1)*se]
            # Sensibilidade aproximada: bootstrap empírico centrado e reescalado
            # para coincidir com Var_AAS estimada. Não é bootstrap exato do desenho.
            boot = rng.choice(x, size=(BOOT_B,n), replace=True).mean(axis=1)
            boot = estimate + (boot-estimate)*math.sqrt((1-n/N)*n/(n-1))
            bci = np.quantile(boot,[.025,.975]).tolist()
            r.update({
                "metodo": "t de uma média com erro-padrão de AAS sem reposição; referência t e IC aproximados",
                "estatistica_nome": "t", "estatistica": float(statistic), "p_valor": float(pvalue),
                "erro_padrao": se, "dp_amostral": s, "graus_liberdade": n-1, "ic95": [float(v) for v in ci],
                "assimetria_amostra": float(stats.skew(x,bias=False)), "max_amostra": int(x.max()),
                "p95_amostra": float(np.quantile(x,.95)),
                "parcela_soma_maior_observacao": float(x.max()/x.sum()),
                "bootstrap_ic95_sensibilidade": bci,
                "bootstrap_cobre_referencia": bci[0] <= theta0 <= bci[1],
            })
        r["rejeita_h0"] = bool(r["p_valor"] < ALPHA)
        r["ic_cobre_populacao_2024"] = bool(r["ic95"][0] <= thetaN <= r["ic95"][1])
        r["ic_cobre_referencia_2023"] = bool(r["ic95"][0] <= theta0 <= r["ic95"][1])
        results.append(r)
    for r, adjusted in zip(results, holm([r["p_valor"] for r in results])):
        r["p_holm_sensibilidade"] = adjusted
        r["rejeita_holm_sensibilidade"] = bool(adjusted < ALPHA)
    return results

def main():
    (WORK/"resultados").mkdir(exist_ok=True)
    (WORK/"dados").mkdir(exist_ok=True)
    pop, info24 = load_year(2024)
    hist, info23 = load_year(2023)
    inspection = {"2024": info24, "2023": info23, "definicao_populacao": "Todas as ocorrências do CSV 2024, sem filtros; unidade: um sinistro registrado."}
    # Escrever a inspeção antes de selecionar quaisquer posições.
    dump(WORK/"resultados/inspecao.json",inspection)
    N = len(pop)
    z = float(stats.norm.ppf(.975))
    n0 = z*z*PLAN_P*(1-PLAN_P)/(MARGIN*MARGIN)
    n_real = N*n0/(N-1+n0)
    n = math.ceil(n_real)
    positions = np.sort(np.random.default_rng(SEED).choice(N,size=n,replace=False))
    sample = pop.iloc[positions].copy()
    assert sample.id.is_unique and len(sample)==n
    sample.to_csv(WORK/"dados/amostra_2024.csv",index=False,encoding="utf-8-sig",sep=";")
    ids = {"semente": SEED, "gerador": "numpy.random.default_rng(2024), PCG64", "criterio_ordenacao": "Ordem física do CSV original; seleção sem reposição, posições ordenadas apenas para salvar.",
           "posicoes_zero_based": positions.tolist(), "ids_na_ordem_csv": sample.id.tolist()}
    dump(WORK/"dados/sorteio.json",ids)
    design = {"N": N, "n": n, "z": z, "confianca": .95, "margem_planejada": MARGIN, "p_planejamento": PLAN_P,
              "n0": n0, "n_finito_antes_arredondamento": n_real, "semente": SEED, "fracao": n/N,
              "probabilidade_inclusao": n/N, "peso_expansao": N/n,
              "margem_maxima_atingida_aproximada": z*math.sqrt((N-n)/(N-1)*.25/n)}
    results = compute_tests(pop,hist,sample)
    bundle = {"desenho": design, "testes": results,
              "resumos": {"populacao_2024": summary(pop,0), "amostra_2024": summary(sample,1), "referencia_2023": summary(hist,0)},
              "fontes": SOURCES, "bootstrap": {"B": BOOT_B, "semente": BOOT_SEED, "ordem_variaveis": ["feridos","veiculos"],"metodo": "Percentil empírico centrado/reescalado; diagnóstico aproximado, não inferência primária"},
              "ambiente": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": __import__("scipy").__version__}}
    dump(WORK/"resultados/analise.json",bundle)
    flat = [{k:v for k,v in r.items() if not isinstance(v,(list,dict))} | {"ic95_inferior":r["ic95"][0], "ic95_superior":r["ic95"][1]} for r in results]
    pd.DataFrame(flat).to_csv(WORK/"resultados/testes.csv",index=False,sep=";",encoding="utf-8-sig")
    # Dados agregados para consulta e auditoria sem novo sorteio.
    records=[]
    for origin,df in [("populacao_2024",pop),("amostra_2024",sample)]:
        for day,count in df.dia_semana.value_counts().items():
            records.append({"conjunto":origin,"dia_semana":day,"n":int(count),"proporcao":float(count/len(df))})
    pd.DataFrame(records).to_csv(WORK/"resultados/dias_semana.csv",index=False,sep=";",encoding="utf-8-sig")
    from relatorio import generate
    generate(bundle,inspection)
    print(json.dumps({"desenho":design,"testes":[{k:r[k] for k in ["variavel","estimativa","referencia_2023","populacao_2024","ic95","p_valor","rejeita_h0"]} for r in results]},ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
