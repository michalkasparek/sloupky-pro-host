import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import altair as alt
    import marimo as mo
    import polars as pl

    return alt, mo, pl


@app.cell
def _(alt):
    from src.kristi_promin import kristi_promin
    from src.me_to_neurazi import me_to_neurazi

    alt.themes.register("irozhlas", kristi_promin)
    alt.theme.enable("irozhlas")
    alt.data_transformers.disable_max_rows()
    return (me_to_neurazi,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Které pátky
    """)


@app.cell
def _():
    patky26 = {
        "prazdniny": [
            "30/1",
            "12/7",
            "19/7",
            "26/7",
            "3/8",
            "10/8",
            "17/8",
            "24/8",
            "30/8",
            "30/11",
        ],
        "svatky": ["3/4", "1/5", "8/5", "5/7", "25/12"],
        "divne": ["2/1", "30/9"],
    }
    return (patky26,)


@app.cell
def _(patky26):
    total = 0
    for kategorie, datum in patky26.items():
        total += len(datum)
        print(f"{kategorie}: {len(datum)}")

    print(total)
    print(total / 52)


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Z datasetu poledních menu vyfiltrujeme týdny, kdy má v pátek polední menu +- stejně restaurací jako v jiné všední dny.
    """)


@app.cell
def _(pl):
    lf_menu = pl.scan_parquet("../poledni-menu/data/menicka.parquet").with_columns(
        pl.col("datum").dt.date()
    )
    return (lf_menu,)


@app.cell
def _(lf_menu):
    lf_menu.head(10).collect()


@app.cell
def _(lf_menu):
    lf_menu.group_by("datum").len().collect()


@app.cell
def _(lf_menu, pl):
    komplet_tydny = (
        lf_menu.with_columns(pl.col("datum").alias("datum2"))
        .group_by_dynamic(index_column="datum", every="1w", start_by="monday")
        .agg(pl.col("datum2").unique().len())
        .filter(pl.col("datum2") == 7)
        .select(pl.col("datum"))
        .collect()
        .to_series()
        .sort()
        .to_list()
    )
    komplet_tydny[0:5]
    return (komplet_tydny,)


@app.cell
def _(lf_menu, pl):
    tydny_s_normalnim_patkem = (
        lf_menu.filter(pl.col("datum").dt.weekday() == 5)
        .group_by_dynamic("datum", every="1w", start_by="monday")
        .len()
        .filter(pl.col("len") > 15000)
        .select(pl.col("datum"))
        .collect()
        .to_series()
        .sort()
        .to_list()
    )
    tydny_s_normalnim_patkem[0:5]
    return (tydny_s_normalnim_patkem,)


@app.cell
def _(komplet_tydny, tydny_s_normalnim_patkem):
    nenormalni = [x for x in komplet_tydny if x not in tydny_s_normalnim_patkem]
    nenormalni[0:5]


@app.cell
def _(komplet_tydny, tydny_s_normalnim_patkem):
    nekomplet = [x for x in tydny_s_normalnim_patkem if x not in komplet_tydny]
    nekomplet[0:5]


@app.cell
def _(komplet_tydny, tydny_s_normalnim_patkem):
    komplet_a_normalni = [x for x in komplet_tydny if x in tydny_s_normalnim_patkem]
    return (komplet_a_normalni,)


@app.cell
def _(komplet_a_normalni):
    komplet_a_normalni


@app.cell
def _(komplet_a_normalni):
    from datetime import timedelta

    sledujeme = [
        monday + timedelta(days=i) for monday in komplet_a_normalni for i in range(7)
    ]

    sledujeme = [str(x) for x in sledujeme]
    return (sledujeme,)


@app.cell
def _(sledujeme):
    sledujeme[0:14]


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Funkce pro tvorbu grafů
    """)


@app.cell
def _(alt, barvy, pl):
    def graf(data, nazev, popisek=""):
        dny = ["po", "út", "st", "čt", "pá", "so", "ne"]
        patecni_hodnota = data.filter(pl.col("d") == 5).select(pl.col("n")).item()
        nejblizsi_den = (
            data.filter(pl.col("d") != 5)
            .with_columns(abs(pl.col("n") - patecni_hodnota))
            .sort(by="n")
            .head(1)
            .select("d")
            .item()
        )

        # Osa y: procenta jen pokud celý graf leží v intervalu 0-1
        maximum = data.select(pl.col("n").max()).item()

        if maximum <= 1:
            label_expr = "format(datum.value * 100, '.0f') + ' %'"
        else:
            label_expr = "replace(format(datum.value, ','), /,/g, ' ')"

        osa_y = alt.Axis(labelExpr=label_expr)

        return (
            alt.Chart(
                data.with_columns(
                    pl.when(pl.col("d").is_in([5, nejblizsi_den]))
                    .then(pl.lit(True))
                    .otherwise(pl.lit(False))
                    .alias("blizko")
                ).with_columns(
                    pl.col("d")
                    .cast(str)
                    .str.replace_many(["1", "2", "3", "4", "5", "6", "7"], dny)
                ),
                title=alt.Title(nazev, subtitle=f"({popisek})"),
                width=330,
                height=140,
            )
            .mark_bar()
            .encode(
                alt.X("d:N", sort=dny, title=None),
                alt.Y("n:Q", title=None, axis=osa_y),
                alt.Color("blizko:N", legend=None, scale=alt.Scale(range=barvy)),
            )
        )

    return (graf,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Obsazenost vlaků
    """)


@app.cell
def _(pl):
    lf_rj = pl.scan_ndjson("../ceny-jizdenek/data_raw/RJ/*/*.ndjson")
    return (lf_rj,)


@app.cell
def _(lf_rj):
    lf_rj.tail(5).collect()


@app.cell
def _():
    cz_months = {
        "ledna": "01",
        "února": "02",
        "března": "03",
        "dubna": "04",
        "května": "05",
        "června": "06",
        "července": "07",
        "srpna": "08",
        "září": "09",
        "října": "10",
        "listopadu": "11",
        "prosince": "12",
    }
    return (cz_months,)


@app.cell
def _(cz_months, lf_rj, pl, sledujeme):
    df_rj = (
        lf_rj.with_columns(
            pl.col("datum")
            .str.replace(r"^.*?,\s*", "")
            .str.replace_many(list(cz_months.keys()), list(cz_months.values()))
            .str.to_date("%d. %m %Y")
        )
        .filter(pl.col("oscrapovano").str.slice(0, 10).str.to_date() == pl.col("datum"))
        .with_columns(pl.col("datum").cast(str))
        .filter(pl.col("datum").is_in(sledujeme))
        .with_columns(pl.col("cas").str.slice(0, 2).cast(int).alias("hodina"))
        .filter(pl.col("hodina").is_between(12, 16))
        .filter(
            pl.col("odkud").str.contains_any(["Praha", "Ostrava"])
            & pl.col("kam").str.contains_any(["Praha", "Ostrava"])
        )
        .with_columns(
            pl.col("volnych_mist").str.extract(r"(\d+)").cast(int).alias("mist")
        )
        .collect()
    )
    return (df_rj,)


@app.cell
def _(df_rj):
    df_rj


@app.cell
def _(df_rj, pl):
    stats_rj = (
        df_rj.group_by(pl.col("datum").str.to_date().dt.weekday())
        .agg(pl.col("mist").mean())
        .sort(by="datum")
        .rename({"datum": "d", "mist": "n"})
    )

    stats_rj
    return (stats_rj,)


@app.cell
def _(graf, stats_rj):
    graf_rj = graf(
        stats_rj,
        nazev="Volná místa v regiojetech mezi Prahou a Ostravou",
        popisek="počet míst v prům. odpoledním vlaku v den nákupu, zdroj: regiojet.cz",
    ).properties(usermeta={"id": "rj"})

    graf_rj
    return (graf_rj,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Segmenty na Stravě
    """)


@app.cell
def _(pl):
    lf_strava = pl.scan_parquet("../strava/data/segments.parquet")
    return (lf_strava,)


@app.cell
def _(lf_strava, pl):
    lf_strava.select(pl.col("date").max()).collect()


@app.cell
def _(lf_strava, pl):
    lf_strava.group_by(["city", "name"]).agg(pl.col("athlete_count").max()).sort(
        by="athlete_count", descending=True
    ).collect()


@app.cell
def _(lf_strava, pl):
    df_klinovec = (
        lf_strava.filter(pl.col("name") == "Klinovec Top")
        .sort("date")
        .with_columns(
            daily_difference=(
                (pl.col("effort_count") - pl.col("effort_count").shift(1))
                / (
                    pl.col("date").dt.date() - pl.col("date").dt.date().shift(1)
                ).dt.total_days()
            )
        )
        .with_columns(
            pl.when(pl.col("daily_difference") < 0)
            .then(pl.lit(0))
            .otherwise(pl.col("daily_difference"))
        )
        .collect()
    )
    return (df_klinovec,)


@app.cell
def _(df_klinovec):
    df_klinovec


@app.cell
def _(df_klinovec, pl):
    df_klinovec.sort(by="daily_difference", descending=True).head(10).select(
        pl.col("date", "daily_difference")
    )


@app.cell
def _(df_klinovec, pl, sledujeme):
    stats_klinovec = (
        df_klinovec.filter(pl.col("date").cast(str).str.slice(0, 10).is_in(sledujeme))
        .filter(pl.col("date").cast(str).str.slice(0, 10) != "2025-07-19")
        .group_by(pl.col("date").dt.weekday())
        .agg(pl.col("daily_difference").mean())
        .sort(by="date")
        .rename({"date": "d", "daily_difference": "n"})
    )

    stats_klinovec
    return (stats_klinovec,)


@app.cell
def _(graf, stats_klinovec):
    graf_klinovec = graf(
        stats_klinovec,
        nazev="Cyklovýjezdy na Klínovec",
        popisek="bez závodu v sobotu 19. 7. 2025, zdroj. strava.com",
    ).properties(usermeta={"id": "klinovec"})

    graf_klinovec
    return (graf_klinovec,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Polední menu
    """)


@app.cell
def _(lf_menu, pl, sledujeme):
    stats_rizky = (
        lf_menu.with_columns(pl.col("datum").cast(str).alias("datum_string"))
        .filter(pl.col("datum_string").is_in(sledujeme))
        .group_by_dynamic(index_column="datum", every="1d")
        .agg(pl.col(["obec", "podnik"]).unique().len())
        .join(
            lf_menu.filter(pl.col("pokrm").str.contains("(?i)říz[ke]"))
            .with_columns(pl.col("datum").cast(str).alias("datum_string"))
            .filter(pl.col("datum_string").is_in(sledujeme))
            .group_by_dynamic(index_column="datum", every="1d")
            .agg(pl.col(["obec", "podnik"]).unique().len()),
            how="left",
            on="datum",
        )
        .with_columns((pl.col("podnik_right") / pl.col("podnik")).alias("r"))
        .group_by(pl.col("datum").dt.weekday())
        .agg(pl.col("r").mean())
        .rename({"datum": "d", "r": "n"})
        .sort(by="d")
        .collect()
    )
    return (stats_rizky,)


@app.cell
def _(graf, stats_rizky):
    graf_rizky = graf(
        stats_rizky,
        "Podíl restaurací s řízkem na poledním menu",
        popisek="z restaurací zveřeňujících nabídku na menicka.cz",
    ).properties(usermeta={"id": "rizky"})

    graf_rizky
    return (graf_rizky,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Hledání
    """)


@app.cell
def _(pl):
    lf_hledani = pl.scan_parquet("../online-hledani/data_raw/seznam/*.parquet")
    return (lf_hledani,)


@app.cell
def _(lf_hledani, pl):
    lf_hledani.filter(pl.col("co").str.contains("(?i)bábovk")).group_by("co").agg(
        pl.col("values").sum()
    ).sort(by="values", descending=True).collect()


@app.cell
def _(lf_hledani, pl, sledujeme):
    stats_babovka = (
        lf_hledani.filter(pl.col("co").str.contains("(?i)bábovk"))
        .with_columns(pl.col("date").cast(str).str.slice(0, 10).alias("date_str"))
        .filter(pl.col("date_str").is_in(sledujeme))
        .group_by(pl.col("date").dt.weekday().alias("d"))
        .agg(pl.col("values").mean().alias("n"))
        .sort(by="d")
        .collect()
    )
    return (stats_babovka,)


@app.cell
def _(graf, stats_babovka):
    graf_babovka = graf(
        stats_babovka, "Hledání receptů na bábovku", popisek="zdroj: seznam.cz"
    ).properties(usermeta={"id": "seznam"})

    graf_babovka
    return (graf_babovka,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Ubytka
    """)


@app.cell
def _(pl):
    lf_airbnb = pl.scan_parquet("../obsazenost-ubytovani/data/airbnb.parquet")
    return (lf_airbnb,)


@app.cell
def _(lf_airbnb):
    lf_airbnb.head(10).collect()


@app.cell
def _(lf_airbnb):
    lf_airbnb.group_by("search").len().sort(by="len", descending=True).collect()


@app.cell
def _(lf_airbnb, pl):
    lf_airbnb.filter(pl.col("checkin") == pl.col("search_date")).filter(
        pl.col("search") == "Beskydy"
    ).group_by("beds").len().sort(by="len", descending=True).collect()


@app.cell
def _(lf_airbnb, pl, sledujeme):
    stats_airbnb = (
        lf_airbnb.filter(pl.col("price_numeric") < 15000)
        .filter(pl.col("checkin") == pl.col("search_date"))
        .filter(pl.col("search") == "Beskydy")
        .with_columns(pl.col("checkin").cast(str).alias("date_str"))
        .filter(pl.col("date_str").is_in(sledujeme))
        .filter(pl.col("beds").is_in(["2 lůžka", "1 manželská postel", "1 dvoulůžko"]))
        .group_by(pl.col("search_date").dt.weekday())
        .agg(pl.col("price_numeric").mean())
        .rename({"search_date": "d", "price_numeric": "n"})
        .sort(by="d")
        .collect()
    )
    return (stats_airbnb,)


@app.cell
def _(graf, stats_airbnb):
    graf_beskydy = graf(
        stats_airbnb,
        "Cena za dvojlůžkový pokoj v Beskydech",
        popisek="v korunách, zdroj: airbnb.com",
    ).properties(usermeta={"id": "airbnb"})

    graf_beskydy
    return (graf_beskydy,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Doprava Brno
    """)


@app.cell
def _(pl):
    lf_brno = pl.scan_ndjson(
        "../kniha-rok/downloads/doprava-brno/*/*.ndjson",
        schema={
            "usek": pl.String,
            "hodnota": pl.String,
            "cas": pl.String,
            "datum": pl.String,
        },
    )
    return (lf_brno,)


@app.cell
def _(lf_brno, pl):
    lf_brno.tail(100).with_columns(
        pl.col("cas")
        .str.split(" ")
        .list.slice(1, 1)
        .list.join("")
        .str.split(":")
        .list.slice(0, 1)
        .list.join("")
        .cast(int)
    ).collect()


@app.cell
def _(lf_brno):
    lf_brno.group_by("usek").len().sort(by="len", descending=True).collect()


@app.cell
def _(lf_brno, pl):
    lf_brno.with_columns(pl.col("hodnota").cast(int)).group_by("usek").agg(
        pl.col("hodnota").mean()
    ).sort(by="hodnota", descending=True).collect()


@app.cell
def _(lf_brno, pl, sledujeme):
    stats_rohlenka = (
        lf_brno.filter(pl.col("usek") == "D1 : km 205 > Rohlenka")
        .filter(pl.col("datum").is_in(sledujeme))
        .with_columns(pl.col("datum").str.to_date())
        .with_columns(
            pl.col("cas")
            .str.split(" ")
            .list.slice(1, 1)
            .list.join("")
            .str.split(":")
            .list.slice(0, 1)
            .list.join("")
            .cast(int)
        )
        .filter(pl.col("cas").is_between(12, 17))
        .with_columns(pl.col("hodnota").cast(int))
        .group_by(pl.col("datum").dt.weekday())
        .agg(pl.col("hodnota").mean())
        .collect()
        .sort(by="datum")
        .rename({"datum": "d", "hodnota": "n"})
    )

    stats_rohlenka
    return (stats_rohlenka,)


@app.cell
def _(graf, stats_rohlenka):
    graf_rohlenka = graf(
        stats_rohlenka,
        "Odpolední dopravní situace na D1 u Rohlenky",
        popisek="škála od 0-plynulá, po 5-neprůjezdná, zdroj: doprava-brno.cz",
    ).properties(usermeta={"id": "rohlenka"})

    graf_rohlenka
    return (graf_rohlenka,)


@app.cell
def _(lf_brno, pl, sledujeme):
    stats_troubsko = (
        (
            lf_brno.filter(pl.col("usek") == "D1 : Brno-západ > Troubsko")
            .filter(pl.col("datum").is_in(sledujeme))
            .with_columns(pl.col("datum").str.to_date())
            .with_columns(
                pl.col("cas")
                .str.split(" ")
                .list.slice(1, 1)
                .list.join("")
                .str.split(":")
                .list.slice(0, 1)
                .list.join("")
                .cast(int)
            )
            .filter(pl.col("cas").is_between(12, 17))
            .with_columns(pl.col("hodnota").cast(int))
            .group_by(pl.col("datum").dt.weekday())
            .agg(pl.col("hodnota").mean())
            .collect()
        )
        .sort(by="datum")
        .rename({"datum": "d", "hodnota": "n"})
    )

    stats_troubsko
    return (stats_troubsko,)


@app.cell
def _(graf, stats_troubsko):
    graf(
        stats_troubsko,
        "Odpolední dopravní situace na výjezdu z Brna na Troubsko",
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Spojení
    """)


@app.cell
def _():
    barvy = ["#6498b1", "#e57439"]
    return (barvy,)


@app.cell
def _(alt):
    alt.SchemaBase.validate = lambda *args, **kwargs: None


@app.cell
def _(
    alt,
    graf_babovka,
    graf_beskydy,
    graf_klinovec,
    graf_rizky,
    graf_rj,
    graf_rohlenka,
):
    small_multiples = alt.vconcat(
        alt.hconcat(graf_rizky, graf_rohlenka, graf_beskydy),
        alt.hconcat(graf_babovka, graf_klinovec, graf_rj),
        title=alt.Title(
            text="Ke kterému dni má pátek nejblíž",
            subtitle=[
                "Pátek a den s hodnotou nejbližší té páteční jsou zvýrazněny stejnou barvou. Sledovány jsou průměry",
                "v „normálních“ týdnech (bez svátků apod.) v posledním roce až dvou – podle zdroje dat.",
            ],
            fontSize=18,
            subtitleFontSize=14,
            anchor="start",  # Left-aligns the title (default is 'middle')
        ),
    ).configure_view(stroke=None)

    small_multiples
    return (small_multiples,)


@app.cell
def _(me_to_neurazi, small_multiples):
    me_to_neurazi(small_multiples, kredity="", soubor="09_patek")


if __name__ == "__main__":
    app.run()
