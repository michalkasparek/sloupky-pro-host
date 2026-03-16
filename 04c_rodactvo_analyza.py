import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import yaml
    import polars as pl

    return mo, pl


@app.cell
def _(pl):
    df_doplnene = pl.read_json("data/rodactvo/rodactvo_nereprezentovane.json")
    return (df_doplnene,)


@app.cell
def _(pl):
    print(", ".join(pl.scan_csv(
        "../who-is-who/cross-verified-database.csv", 
        ignore_errors=True, 
        encoding="utf8-lossy"
    ).collect().columns))
    return


@app.cell
def _():
    sloupce = ["name","cs_to_de","birth","death","gender","level1_main_occ","level2_main_occ","freq_second_occ","level3_main_occ","number_wiki_editions","ranking_visib_5criteria","languages","cs_length","de_length","wikidata_id"]
    return (sloupce,)


@app.cell
def _(df_doplnene, pl, sloupce):
    df = pl.scan_csv(
        "../who-is-who/cross-verified-database.csv", 
        ignore_errors=True, 
        encoding="utf8-lossy"
    ).filter(
        pl.col("bplo1").is_between(10,20) & pl.col("bpla1").is_between(47,53)
    ).collect(
    ).join(
        df_doplnene,
        right_on="wikidata_id",
        left_on="wikidata_code",
        how="right"
    ).with_columns(
        (pl.col("cs_length") / pl.col("de_length")).alias("cs_to_de"),
        pl.col("cs_length").fill_null(0),
        pl.col("de_length").fill_null(0)
    ).select(
        pl.col(sloupce)
    ).unique(
        subset="wikidata_id"
    ).sort(
        by="ranking_visib_5criteria"
    ).filter(
        (pl.col("level1_main_occ").is_in(["Culture","Discovery/Science"])) & (pl.col('birth') >= 1848)
    )
    return (df,)


@app.cell
def _():
    hranice_znamosti = 1800
    return (hranice_znamosti,)


@app.cell
def _(df):
    len(df)
    return


@app.cell
def _(df):
    df.columns
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Čeští rodáci známí po světě
    """)
    return


@app.function
def vypis(frejm, rank=False):
    pocitadlo = 1
    for radek in frejm.iter_rows(named=True):
        if rank == True:
            poradi = f"| #{round(radek['ranking_visib_5criteria'])}"
        else:
            poradi = ""
        print(f"{pocitadlo}. {radek['name'].split("(")[0].strip()} | *{radek['birth']} †{radek['death']} | {radek['level3_main_occ']} {poradi}".replace('None','').replace('_',' ').replace('† |','|').replace("  "," "))
        pocitadlo += 1


@app.cell
def _(df):
    df
    return


@app.cell
def _(df):
    vypis(df.head(15), rank=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Čeští rodáci neznámi v Česku a známí v Německu
    """)
    return


@app.cell
def _(df, hranice_znamosti, pl):
    nemecka = df.filter((pl.col("cs_length") <= hranice_znamosti) & (pl.col('de_length') != 0)).sort(by="de_length",descending=True)
    nemecka
    return (nemecka,)


@app.cell
def _(nemecka):
    vypis(nemecka.head(15))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Čeští rodáci známí po světě, neznámí v Česku i Německu
    """)
    return


@app.cell
def _(df, pl):
    ani_cs_ani_de = df.filter(
        (pl.col("cs_length") == 0) & (pl.col("de_length") == 0)
    ).select(pl.col('name')).to_series().to_list()
    return


@app.cell
def _(df, pl):
    df.filter(
        (pl.col("cs_length") == 0) & (pl.col("de_length") == 0)
    )
    return


@app.cell
def _(df, hranice_znamosti, pl):
    df.filter(
        (pl.col("cs_length") <= hranice_znamosti) & (pl.col("de_length") <= hranice_znamosti)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Čeští rodáci známí v Česku a neznámi v Německu
    """)
    return


@app.cell
def _(df, hranice_znamosti, pl):
    ceska = df.filter((pl.col("de_length") <= hranice_znamosti) & (pl.col('cs_length') != 0)).sort(by="cs_length",descending=True)
    ceska 
    return (ceska,)


@app.cell
def _(ceska):
    vypis(ceska.head(15))
    return


if __name__ == "__main__":
    app.run()
