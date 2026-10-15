import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import json

    import altair as alt
    import polars as pl

    from src.kristi_promin import kristi_promin
    from src.me_to_neurazi import me_to_neurazi

    pl.Config.set_tbl_rows(150)
    pl.Config.set_fmt_str_lengths(150)
    pl.Config.set_tbl_width_chars(200)

    alt.themes.register("irozhlas", kristi_promin)
    alt.theme.enable("irozhlas")
    alt.data_transformers.disable_max_rows()
    return alt, json, me_to_neurazi, pl


@app.cell
def _(json):
    with open("../hodiny-literatury/cifernik.json", "r", encoding="utf-8") as f:
        cifernik = json.loads(f.read())
    return (cifernik,)


@app.cell
def _(cifernik):
    cifernik_seznam = []
    for cas, texty in cifernik.items():
        cifernik_seznam.append({"cas": cas, "uryvek": texty[0], "zdroj": texty[1]})
    return cas, cifernik_seznam


@app.cell
def _(cifernik_seznam):
    cifernik_seznam


@app.cell
def _(cifernik_seznam, pl):
    df = pl.DataFrame(cifernik_seznam).with_columns(
        pl.col("cas")
        .str.split(":")
        .list.slice(0, 1)
        .list.join("")
        .cast(int)
        .alias("h"),
        pl.col("cas")
        .str.split(":")
        .list.slice(1, 1)
        .list.join("")
        .cast(int)
        .alias("m"),
        pl.col("uryvek").str.len_bytes().alias("delka"),
    )
    return (df,)


@app.cell
def _(df, pl):
    for paral in (
        df.filter(pl.col("zdroj").str.contains("Páral"))
        .select(pl.col("uryvek"))
        .sample(10)
        .to_series()
        .to_list()
    ):
        print(paral)


@app.cell
def _(df, pl):
    for uryvek in (
        df.filter(pl.col("delka") <= 100)
        .select(pl.col("uryvek"))
        .sample(10)
        .to_series()
        .to_list()
    ):
        print(uryvek)


@app.cell
def _(df):
    len(" ".join(df.select("uryvek").to_series().to_list()))


@app.cell
def _(df):
    vypis = ""
    for radek in df.iter_rows(named=True):
        vypis += f"{radek['cas']} | {radek['uryvek']} | {radek['zdroj']}"
        vypis += "\n"
    return (vypis,)


@app.cell
def _(vypis):
    with open("07_hodiny_casy.txt", "w+", encoding="utf-8") as h:
        h.write(vypis)


@app.cell
def _(df):
    df


@app.cell
def _(df):
    cetnost_hodin = df.group_by("h").len()

    cetnost_hodin.sort(by="len", descending=True)
    return (cetnost_hodin,)


@app.cell
def _(alt, cetnost_hodin):
    alt.Chart(cetnost_hodin).mark_bar().encode(alt.X("h:Q"), alt.Y("len:Q"))


@app.cell
def _(df, pl):
    cetnost_minut = (
        df.group_by("m")
        .len()
        .with_columns(
            pl.when(pl.col("len") <= 8)
            .then(pl.lit(True))
            .otherwise(pl.lit(False))
            .alias("fakt_malo")
        )
    )

    cetnost_minut.sort(by="len", descending=True)
    return (cetnost_minut,)


@app.cell
def _(alt, cetnost_minut):
    alt.Chart(cetnost_minut).mark_bar().encode(
        alt.X("m:Q"), alt.Y("len:Q"), alt.Color("fakt_malo:N")
    )


@app.cell
def _(cifernik_seznam):
    cifernik_og = {}
    for minuta in cifernik_seznam:
        cifernik_og[minuta["cas"]] = True
    cifernik_og
    return (cifernik_og,)


@app.cell
def _(cas, cifernik_og):
    prehled = "Chybějící časy v české beletrii v Digitální knihovně\n\n-----↓0---↓5---↓10--↓15--↓20--↓25--½--35↓--40↓--45↓--50↓--55↓-min \n"
    nejsou_zanesene = []
    for i in range(24):
        radka = f"{i:02} h "
        for m in range(60):
            c = f"{i:02}:{m:02}"
            try:
                blabla = cifernik_og[c]
                radka += " "
            except:
                radka += "▓"
                if i in [12, 13, 14, 20, 21, 22, 23]:
                    v = "ve"
                else:
                    v = "v"
                nejsou_zanesene.append(f"{v} {cas.replace(':', '.')}")
                nejsou_zanesene.append(f"{i} hod {m:02}")
                nejsou_zanesene.append(f"{i} hodin {m:02}")
        prehled += radka + "  \n"
    print(prehled)
    with open("07_hodiny_prehled_chybejicich.txt", "w+", encoding="utf-8") as f_prehled:
        f_prehled.write(prehled)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pokus o překreslení grafu
    """)


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(cifernik_og, pl):
    do_grafu = []
    for hodiny in range(24):
        for minuty in range(60):
            try:
                if cifernik_og[f"{hodiny:02}:{minuty:02}"] == True:
                    do_grafu.append(
                        {
                            "h": f"{hodiny:02}",
                            "m": f"{minuty:02}",
                            "existuje": True,
                        }
                    )
            except:
                do_grafu.append(
                    {"h": f"{hodiny:02}", "m": f"{minuty:02}", "existuje": False}
                )
    do_grafu = pl.DataFrame(do_grafu)
    return (do_grafu,)


@app.cell
def _(do_grafu):
    do_grafu


@app.cell
def _(alt, do_grafu):
    chart = (
        alt.Chart(
            do_grafu,
            title=alt.Title(
                "Časy nezachycené v české beletrii v Digitální knihovně (šedé čtverce)"
            ),
        )
        .mark_rect(
            stroke="lightgray",  # This creates the "grid" lines around each rectangle
            strokeWidth=1,  # Thickness of the grid lines
        )
        .encode(
            x=alt.X(
                "m:N",
                axis=alt.Axis(orient="top", domain=False, title="minuta", grid=False),
            ),  # Turn off actual axis grid
            y=alt.Y(
                "h:N", axis=alt.Axis(domain=False, title="hodina", grid=False)
            ),  # Turn off actual axis grid
            color=alt.Color(
                "existuje:N",
                scale=alt.Scale(domain=[True, False], range=["white", "darkgray"]),
                legend=None,
            ),
        )
    )

    chart
    return (chart,)


@app.cell
def _(me_to_neurazi):
    help(me_to_neurazi)


@app.cell
def _(chart, me_to_neurazi):
    me_to_neurazi(
        chart,
        kredity="Hodiny zobrazující čas prostřednictvím ukázek z české beletrie běží na michalkasparek.cz/hodiny.html",
        soubor="07_hodiny",
    )


if __name__ == "__main__":
    app.run()
