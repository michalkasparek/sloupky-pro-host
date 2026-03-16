import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import yaml
    import polars as pl
    import geopandas as gpd
    import geodatasets
    from shapely.geometry import Point
    import altair as alt
    import marimo as mo

    return Point, gpd, mo, os, pl, yaml


@app.cell
def _(os):
    os.makedirs("data/rodactvo/",exist_ok=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Data lze stáhnout odtud: [A cross-verified database of notable people, 3500BC-2018AD](https://www.nature.com/articles/s41597-022-01369-4)
    """)
    return


@app.cell
def _(os, pl):
    df = pl.scan_csv(
        os.path.join("../who-is-who/","cross-verified-database.csv"), 
        ignore_errors=True, 
        encoding="utf8-lossy"
    ).filter(
        pl.col("bplo1").is_between(10,20) & pl.col("bpla1").is_between(47,53)
    ).collect(
    )
    return (df,)


@app.cell
def _(gpd):
    url = "https://github.com/siwekm/czech-geojson/raw/refs/heads/master/czech_republic.json"
    czechia_gdf = gpd.read_file(url)
    czechia_geom = czechia_gdf.geometry.iloc[0]
    return (czechia_geom,)


@app.cell
def _(Point, czechia_geom):
    def is_in_czechia(lon, lat):
        # Handle nulls gracefully so Shapely doesn't crash
        if lon is None or lat is None:
            return False
        return czechia_geom.contains(Point(lon, lat))

    return (is_in_czechia,)


@app.cell
def _(df, is_in_czechia, pl):
    df_cz = df.with_columns(
        pl.struct(["bplo1", "bpla1"])
        .map_elements(
            lambda row: is_in_czechia(row["bplo1"], row["bpla1"]),
            return_dtype=pl.Boolean
        )
        .alias("Czechia_born")
    ).filter(
        pl.col("Czechia_born") == True
    ).with_columns(
        pl.struct(["dplo1", "dpla1"])
        .map_elements(
            lambda row: is_in_czechia(row["dplo1"], row["dpla1"]),
            return_dtype=pl.Boolean
        )
        .alias("Czechia_died")
    )
    return (df_cz,)


@app.cell
def _(df_cz):
    df_cz.sample()
    return


@app.cell
def _(df_cz, pl):
    df_cz.filter(pl.col("Czechia_died") == False).sort(by="ranking_visib_5criteria")
    return


@app.cell
def _(df_cz, pl, yaml):
    narozeni_cr = df_cz.sort(by="ranking_visib_5criteria").select(pl.col("name","wikidata_code"))

    print(len(narozeni_cr))

    print(narozeni_cr.head(10))

    with open("data/rodactvo/narozeni_cr.yaml", "w", encoding="utf-8") as f_1000:
        yaml.dump(narozeni_cr.select(pl.col('wikidata_code')).to_series().to_list(), f_1000, allow_unicode=True, default_flow_style=False)
    return


@app.cell
def _(df_cz, pl, yaml):
    narozeni_cr_zemreli_mimo_cr = df_cz.filter(~pl.col("list_wikipedia_editions").str.contains("cswiki")).filter(pl.col("Czechia_died") == False).sort(by="ranking_visib_5criteria").select(pl.col("name","wikidata_code")).head(100)

    print(narozeni_cr_zemreli_mimo_cr.head(10))

    with open("data/rodactvo/narozeni_cr_zemreli_mimo_cr.yaml", "w", encoding="utf-8") as f:
        yaml.dump(narozeni_cr_zemreli_mimo_cr.select(pl.col('wikidata_code')).to_series().to_list(), f, allow_unicode=True, default_flow_style=False)
    return


@app.cell
def _(df_cz, pl, yaml):
    narozeni_cr_bez_ceske_wiki = df_cz.filter(~pl.col("list_wikipedia_editions").str.contains("cswiki")).sort(by="ranking_visib_5criteria").select(pl.col("name","wikidata_code")).head(200)

    print(narozeni_cr_bez_ceske_wiki.head(10))

    with open("data/rodactvo/narozeni_cr_bez_ceske_wiki.yaml", "w", encoding="utf-8") as f2:
        yaml.dump(narozeni_cr_bez_ceske_wiki.select(pl.col('wikidata_code')).to_series().to_list(), f2, allow_unicode=True, default_flow_style=False)
    return


@app.cell
def _(df_cz, pl, yaml):
    narozeni_cr_bez_nemecke_wiki = df_cz.filter(~pl.col("list_wikipedia_editions").str.contains("dewiki")).sort(by="ranking_visib_5criteria").select(pl.col("name",'wikidata_code')).head(200)

    print(narozeni_cr_bez_nemecke_wiki.head(10))

    with open("data/rodactvo/narozeni_cr_bez_nemecke_wiki.yaml", "w", encoding="utf-8") as f3:
        yaml.dump(narozeni_cr_bez_nemecke_wiki.select(pl.col('wikidata_code')).to_series().to_list(), f3, allow_unicode=True, default_flow_style=False)
    return


if __name__ == "__main__":
    app.run()
