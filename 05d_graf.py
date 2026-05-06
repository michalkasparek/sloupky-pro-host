import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import altair as alt

    return alt, pl


@app.cell
def _():
    from src.kristi_promin import kristi_promin
    from src.me_to_neurazi import me_to_neurazi

    return kristi_promin, me_to_neurazi


@app.cell
def _(alt, kristi_promin):
    alt.themes.register('irozhlas', kristi_promin)
    alt.theme.enable('irozhlas')
    alt.data_transformers.disable_max_rows()
    return


@app.cell
def _(pl):
    df1 = pl.read_json("data/podobnost/tela_embeddings.json").unique(subset="DK_titul")
    df1.sort(by="similarity_score")
    return (df1,)


@app.cell
def _(df1, pl):
    df1.filter(pl.col("DK_titul").str.contains("Křehká"))
    return


@app.cell
def _(df1, pl):
    df1.filter(pl.col("DK_titul").str.contains("Praskliny"))
    return


@app.cell
def _():
    return


@app.cell
def _(pl):
    df2 = pl.read_json("data/podobnost/tela_pujcuji_take.json").unique(subset="TITUL_NAZEV")
    df2.sort(by="r_vazeny")
    return (df2,)


@app.cell
def _(df2, pl):
    df2.filter(pl.col("TITUL_NAZEV").str.contains("Blízcí"))
    return


@app.cell
def _(df1, df2, pl):
    df = df1.join(
        df2, how="full", left_on="DK_titul", right_on="TITUL_NAZEV"
    ).with_columns(
       (0.48 - pl.col("similarity_score").pow(2.3)).alias("similarity_score"),
        (1 - pl.col("r_vazeny")).pow(6).alias("r_vazeny")
    ).with_columns(
        pl.when(pl.col("TITUL_NAZEV") == "Těla")
        .then(pl.lit(0))
        .otherwise(pl.col("similarity_score"))
        .alias("similarity_score"),
        pl.when(pl.col("TITUL_NAZEV") == "Těla")
        .then(pl.lit(0))
        .otherwise(pl.col("r_vazeny"))
        .alias("r_vazeny"),
        pl.when(pl.col("TITUL_NAZEV") == "Těla")
        .then(pl.lit("Těla"))
        .otherwise(pl.col("DK_titul"))
        .alias("DK_titul"),
        (pl.col("similarity_score") * pl.col("r_vazeny")).alias('blizkost'),
        pl.when(pl.col("TITUL_NAZEV") == "Těla")
        .then(pl.lit("Klára Vlasáková"))
        .otherwise(pl.col("DK_autorstvo"))
        .alias("DK_autorstvo")
    ).with_columns(
        pl.when(pl.col("TITUL_NAZEV") == "Těla")
        .then(pl.lit(0))
        .otherwise(pl.col("blizkost"))
        .alias("blizkost"),
        (pl.col("DK_autorstvo") + pl.lit(": ") + pl.col("DK_titul")).alias("popisek")
    ).with_columns(
        pl.when(pl.col("TITUL_NAZEV") == "Těla")
        .then(pl.lit(True))
        .otherwise(pl.lit(False))
        .alias("tela"))
    return (df,)


@app.cell
def _(df, pl):
    df.filter(pl.col("DK_titul") == "Těla")
    return


@app.cell
def _(df):
    df.drop_nulls(
        subset='blizkost'
    ).sort(
        by='blizkost'
    )
    return


@app.cell
def _(df):
    do_grafu = df.drop_nulls(subset='blizkost') # .filter((pl.col('r_vazeny') < 0.5) & (pl.col('similarity_score') < 0.4))
    return (do_grafu,)


@app.cell
def _(do_grafu):
    len(do_grafu)
    return


@app.cell
def _(do_grafu):
    do_grafu.sort(by='similarity_score')
    return


@app.cell
def _(do_grafu):
    do_grafu.sort(by='r_vazeny')
    return


@app.cell
def _():
    return


@app.cell
def _():
    nechceme = [
        "Myšlenky za volantem",
        "Zpíváš, jako bys plakala",
        "Srdce Evropy",
        "Anděl smrti",
        "15 roků lásky",
        "Úlice",
        "Přechodné období",
        "Křehkost",
        "Skutečná",
        "Po povrchu",
        "Šmírák",
        "Země",
        "Marta děti nechce",
        "Fosilie",
        "Dvojí život",
        "Návrat nežádoucí",
        "Jeřabinový dům",
        "Dýchej za mě",
        "Z mého severoitalského deníku",
        "Dlouhá trať",
        "Lenka",
        "Národní opruzení",
        "Krutý měsíc"
    ]
    return (nechceme,)


@app.cell
def _(do_grafu, nechceme, pl):
    chceme1 = (
        do_grafu.sort(by="blizkost")
        .head(20)
        .select(pl.col("DK_titul"))
        .to_series()
        .to_list()
        + do_grafu.sort(by="blizkost")
        .tail(5)
        .select(pl.col("DK_titul"))
        .to_series()
        .to_list()
    )

    chceme2 = (
        do_grafu.filter(~pl.col("DK_titul").is_in(chceme1))
        .select(pl.col("DK_titul"))
        .sample(n=45, seed=1)
        .to_series()
        .to_list()
    )

    chceme3 = chceme1 + chceme2

    chceme = [x for x in chceme3 if x not in nechceme]
    return (chceme,)


@app.cell
def _(nechceme):
    nechceme
    return


@app.cell
def _(chceme, do_grafu, pl):
    do_grafu_final = do_grafu.filter(pl.col("DK_titul").is_in(chceme))
    return (do_grafu_final,)


@app.cell
def _(do_grafu_final):
    len(do_grafu_final)
    return


@app.cell
def _(alt, do_grafu_final):
    # 1. Define the base chart with the shared X, Y, and tooltip encodings
    base = alt.Chart(
        do_grafu_final, height=400, width=800,
        title=alt.Title(
            "Dva rozměry podobnosti Tělům",
            subtitle=[
                "Jak se mohou lišit seznamy „podobných“ knih podle pramene této podobnosti? Příkladem budiž román Kláry Vlasákové z roku 2023, Těla.","Čtenáři a čtenářky si v Městské knihovně v Praze nejčastěji půjčují též Křehká příměří Michaely Štěchové, které však mají relativně odlišnou anotaci.","Popiskem se Tělům blíží Chalupa Pavlíny Křivánkové nebo Nikdo není sám Petry Soukupové, jenže ty si zase tak často nepůjčují stejní lidé.","Obě kritéria podobnosti nejlépe naplňuje Mezi nimi Veroniky González a nejhůř Prvok, Šampón, Tečka a Karel Patrika Hartla."
            ]
        )
    ).encode(
        alt.X(
            "similarity_score:Q",
            axis=alt.Axis(
                domainColor="white",
                grid=False,
                labelColor="white",
                tickColor="white",
                title="<-- anotace se více podobají anotaci Těl",

            ),
            scale=alt.Scale(domain=[0,0.43]),
        ),
        alt.Y(
            "r_vazeny:Q",
            axis=alt.Axis(
                domainColor="white",
                grid=False,
                labelColor="white",
                tickColor="white",
                title="<-- čtenářstvo si častěji půjčuje i Těla",

            ),

        ),
        alt.Color("tela:N",legend=None),
        alt.Shape("tela:N",legend=None),
        tooltip=["DK_titul", "similarity_score", "r_vazeny"],
    )

    # 2. Create the points layer
    points = base.mark_point(filled=True)

    velikost=10

    # 3. Create the text labels layer
    text1 = base.mark_text(
        align="left",
        baseline="middle",
        fontSize=velikost,
        dx=6,  # Shifts the text 7 pixels to the right so it doesn't overlap the point
        color="black",  # You can adjust the text color here (e.g., "white" if your background is dark)
    ).encode(text="DK_titul:N")

    # 4. Combine them and apply your view configuration
    finalni_graf = (points + text1).configure_view(strokeWidth=0)

    finalni_graf
    return (finalni_graf,)


@app.cell
def _(finalni_graf, me_to_neurazi):
    me_to_neurazi(finalni_graf, kredity="zdroj dat: Městská knihovna v Praze a Databáze knih", soubor="05_podobnost")
    return


if __name__ == "__main__":
    app.run()
