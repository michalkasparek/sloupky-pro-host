import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import re
    import json
    import polars as pl

    return os, pl


@app.cell
def _(os, pl):
    df = pl.scan_parquet(os.path.join("../knizni-peoplemetr/data","cnb_vyber.parquet"))
    return (df,)


@app.cell
def _(df, pl):
    dfp = df.explode("250_a").explode("072_x").filter(
        pl.col("250_a").str.to_lowercase().str.contains_any(["1.", "první"])
        & (pl.col("008").str.slice(7, 4).str.contains_any([str(x) for x in range(2020,2030)]))
        & (pl.col("072_x") == "Česká próza")
    ).collect()

    dfp
    return (dfp,)


@app.cell
def _(dfp, pl):
    overeni = ['Pitínský','Hlaučo','Hamplová','Kausc','Zbořil']
    for o in overeni:
        print(o)
        print(dfp.filter(pl.col("100_a").str.contains(o)).select(pl.col(['100_a','245_a'])))
    return


@app.cell
def _(dfp, pl):
    dfp.explode("020_a").with_columns(pl.col("020_a").str.replace("-", "")).select(
        pl.col("020_a")
    ).write_csv("data/isbn_beletrie.csv")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
