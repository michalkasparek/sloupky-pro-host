import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import altair as alt
    import marimo as mo
    import polars as pl
    import polars.selectors as cs

    from src.kristi_promin import kristi_promin
    from src.me_to_neurazi import me_to_neurazi

    alt.themes.register("irozhlas", kristi_promin)
    alt.theme.enable("irozhlas")
    alt.data_transformers.disable_max_rows()
    return alt, cs, me_to_neurazi, pl


@app.cell
def _(pl):
    df = (
        pl.read_parquet("../ig/data/messages.parquet")
        .sort(by="timestamp")
        .with_columns(
            pl.col("content").str.count_matches(" ").alias("slov"),
            pl.col("content")
            .str.extract_all(
                r"\p{Emoji_Presentation}|\p{Extended_Pictographic}"
            )
            .alias("emojis"),
        )
    )
    return (df,)


@app.cell
def _(df, pl):
    nejcastejsi_emoji = (
        df.explode("emojis")
        .filter(pl.col("emojis") != "🦕")
        .group_by("emojis")
        .len()
        .filter(pl.col("len") >= 10)
        .select(pl.col("emojis"))
        .to_series()
        .to_list()
    )
    nejcastejsi_emoji
    return (nejcastejsi_emoji,)


@app.cell
def _(df, nejcastejsi_emoji, pl):
    emoji_ratio = (
        df.with_columns(
            pl.when(pl.col("sender") == "Michal Kašpárek")
            .then(pl.lit("ja"))
            .otherwise(pl.lit("ostatni"))
            .alias("kdo")
        )
        .explode("emojis")
        .group_by(["emojis", "kdo"])
        .len()
        .sort(by="emojis")
        .pivot(
            index="emojis",  # The column to keep as rows
            on="kdo",  # The column whose values become the new column names
            values="len",  # The column providing the cell values
        )
        .fill_null(0)
        .with_columns(ratio_ja=pl.col("ja") / pl.col("ostatni"))
        .filter(pl.col("emojis").is_in(nejcastejsi_emoji))
        .sort(by="ratio_ja", descending=True)
    )

    emoji_ratio
    return (emoji_ratio,)


@app.cell
def _():
    zajimava_emoji = list(
        set(
            [
                "💀",
                "😉",
                "🔥",
                "🥳",
                "🍑",
                "✌",
                "🐎",
                "🍆",
                "🔝",
                "🤪",
                # "👀",
                # "🥲",
                "🤌",
                "😔",
                "🙏",
                # "♀",
                "💪",
                "🥰",
                "🤗",
                # "😊",
                # "💦",
                # "👅",
                "😎",
                "🐩",
                "🫶",
                f"✅",
                "‼",
                # "💔",
                "🤦",
                "🫠",
                "⛲",
                # "🐕",
                "😬",
                "🦭",
                "✔",
                "💖",
                "🏆",
                "☑",
                "🤣",
                "🥂",
                "🤭",
                # "♂",
                "💅",
                # "🐒",
                # "🙈",
                "🍸",
                "💯",
                # f"💔",
                "👈",
                "😘",
                "🎉",
                # "🤯"
            ]
        )
    )
    return (zajimava_emoji,)


@app.cell
def _(df, nejcastejsi_emoji, pl):
    time_in_hours = (
        pl.col("timestamp").dt.hour()
        + pl.col("timestamp").dt.minute() / 60
        + pl.col("timestamp").dt.second() / 3600
    )

    raw_diff = time_in_hours - 18.5

    shifted_hours = (
        pl.when(raw_diff < -12).then(raw_diff + 24).otherwise(raw_diff)
    )

    emoji_offset = (
        df.explode("emojis")
        .filter(pl.col("emojis").is_in(nejcastejsi_emoji))
        .with_columns(offset_from_18_30h=shifted_hours)
        # Assuming 'emojis' is your exploded/string column from the pivot step
    ).sort(by="offset_from_18_30h")
    return


@app.cell
def _(df, nejcastejsi_emoji, pl):
    emoji_den_noc = (
        df.filter(pl.col("timestamp").dt.year() >= 2019)
        .with_columns(pl.col("timestamp").dt.hour())
        .with_columns(
            pl.when(
                pl.col("timestamp").is_between(0, 5)
                | pl.col("timestamp").is_between(20, 23)
            )
            .then(pl.lit("noc"))
            .otherwise(pl.lit("den"))
            .alias("kdy")
        )
        .explode("emojis")
        .filter(pl.col("emojis").is_in(nejcastejsi_emoji))
        .group_by(["emojis", "kdy"])
        .len()
        .pivot(index="emojis", on="kdy", values="len")
        .fill_null(0)
        .with_columns(ratio_noc=pl.col("noc") / pl.col("den"))
        .sort(by="ratio_noc")
    )

    emoji_den_noc
    return (emoji_den_noc,)


@app.cell
def _(df):
    pocet_emojis = df.explode("emojis").group_by("emojis").len()
    return


@app.cell
def _(cs, emoji_den_noc, emoji_ratio, pl, zajimava_emoji):
    do_grafu = (
        emoji_den_noc.join(emoji_ratio, how="left", on="emojis")
        .filter(pl.col("emojis").is_in(zajimava_emoji))
        .with_columns(
            pl.when(cs.contains("ratio") <= 1)
            .then(cs.contains("ratio") - 1)
            .otherwise(
                (cs.contains("ratio") - 1) / (cs.contains("ratio").max() - 1)
            )
        )
    )
    return (do_grafu,)


@app.cell
def _(alt, do_grafu):
    rozmer = 500

    kvadranty = (
        alt.Chart(do_grafu)
        .mark_text(
            size=20,  # Adjust emoji size here
            align="center",
            baseline="middle",
        )
        .encode(
            x=alt.X(
                "ratio_noc:Q",
                title="častěji v noci",
                scale=alt.Scale(domain=[-1, 1]),
            ),
            y=alt.Y(
                "ratio_ja:Q",
                title="častěji já",
                scale=alt.Scale(domain=[-1, 1]),
            ),
            text="emojis:N",
            tooltip=[
                "emojis",
                "noc",
                "den",
                "ratio_noc",
                "ratio_ja",
            ],  # Optional: adds hover details
        )
        .properties(title="Emoji Ratios", width=rozmer, height=rozmer)
    )
    return kvadranty, rozmer


@app.cell
def _(kvadranty):
    kvadranty
    return


@app.cell
def _(df):
    pocet_e = round(len(df.explode("emojis").select('emojis').drop_nulls()) / 1000)
    pocet_e
    return


@app.cell
def _(df):
    pocet_zprav = round(len(df) / 1000)
    pocet_zprav
    return (pocet_zprav,)


@app.cell
def _(alt, do_grafu, me_to_neurazi, pocet_zprav, rozmer):
    # 1. Full-bleed background quadrants using the custom palette
    # Left (Day / "ve dne") = warm yellows/ochres (#ebb842, #f0c895)
    # Right (Night / "v noci") = cool blues/teals (#2c5377, #647799)
    quadrant_bg = (
        alt.Chart(
            alt.Data(
                values=[
                    {"x": -1.08, "x2": 0, "y": 0, "y2": 1.08, "color": "#ebb842"},   # Top-Left: Day + Sent by me (warm gold)
                    {"x": 0, "x2": 1.08, "y": 0, "y2": 1.08, "color": "#2c5377"},    # Top-Right: Night + Sent by me (deep night blue)
                    {"x": -1.08, "x2": 0, "y": -1.08, "y2": 0, "color": "#f0c895"},  # Bottom-Left: Day + Received (soft warm sand)
                    {"x": 0, "x2": 1.08, "y": -1.08, "y2": 0, "color": "#647799"},   # Bottom-Right: Night + Received (muted slate blue)
                ]
            )
        )
        .mark_rect(opacity=0.35)
        .encode(
            x="x:Q",
            x2="x2:Q",
            y="y:Q",
            y2="y2:Q",
            color=alt.Color("color:N", scale=None),
        )
    )

    # 2. Thick central crosshairs at x=0 and y=0 (using palette's dark charcoal #3d3c3b)
    x_axis_line = (
        alt.Chart(alt.Data(values=[{"y": 0}]))
        .mark_rule(color="#3d3c3b", size=2.5)
        .encode(y="y:Q")
    )

    y_axis_line = (
        alt.Chart(alt.Data(values=[{"x": 0}]))
        .mark_rule(color="#3d3c3b", size=2.5)
        .encode(x="x:Q")
    )

    # 3. Arrowheads at the very edges of the central axes
    arrows = (
        alt.Chart(
            alt.Data(
                values=[
                    {"x": 0, "y": 1.06, "angle": 0},     # Up
                    {"x": 0, "y": -1.06, "angle": 180},  # Down
                    {"x": 1.06, "y": 0, "angle": 90},    # Right
                    {"x": -1.06, "y": 0, "angle": 270},  # Left
                ]
            )
        )
        .mark_point(shape="triangle", filled=True, color="#3d3c3b", size=140, opacity=1)
        .encode(
            x="x:Q",
            y="y:Q",
            angle=alt.Angle("angle:Q", scale=None),
        )
    )

    # 4a. Vertical axis labels in Asap font
    vertical_labels = (
        alt.Chart(
            alt.Data(
                values=[
                    {"x": 0, "y": 1.02, "label": "častěji posílám já druhým"},
                    {"x": 0, "y": -1.02, "label": "častěji posílají druzí mně"},
                ]
            )
        )
        .mark_text(font="Asap", fontSize=11, fontWeight="normal", color="#3d3c3b", align="left", dx=10)
        .encode(x="x:Q", y="y:Q", text="label:N")
    )

    # 4b. Horizontal axis labels in Asap font
    label_right = (
        alt.Chart(alt.Data(values=[{"x": 1.02, "y": 0, "label": "častěji v noci"}]))
        .mark_text(font="Asap", fontSize=11, fontWeight="normal", color="#3d3c3b", align="right", dy=-12)
        .encode(x="x:Q", y="y:Q", text="label:N")
    )

    label_left = (
        alt.Chart(alt.Data(values=[{"x": -1.02, "y": 0, "label": "častěji ve dne"}]))
        .mark_text(font="Asap", fontSize=11, fontWeight="normal", color="#3d3c3b", align="left", dy=-12)
        .encode(x="x:Q", y="y:Q", text="label:N")
    )

    # 5. Your original emoji layer
    emojis_layer = (
        alt.Chart(do_grafu)
        .mark_text(
            size=22,
            align="center",
            baseline="middle",
        )
        .encode(
            x=alt.X(
                "ratio_noc:Q",
                title=None,
                scale=alt.Scale(domain=[-1.08, 1.08], nice=False),
                axis=alt.Axis(grid=True, domain=False, labels=False, ticks=False),
            ),
            y=alt.Y(
                "ratio_ja:Q",
                title=None,
                scale=alt.Scale(domain=[-1.08, 1.08], nice=False),
                axis=alt.Axis(grid=True, domain=False, labels=False, ticks=False),
            ),
            text="emojis:N",
            tooltip=["emojis", "noc", "den", "ratio_noc", "ratio_ja"],
        )
    )

    # Combine all layers in back-to-front order
    kvadranty2 = (
        (
            quadrant_bg
            + x_axis_line
            + y_axis_line
            + arrows
            + emojis_layer
            + vertical_labels
            + label_right
            + label_left
        )
        .properties(title=f"""Kompas emojis v {pocet_zprav} tisících soukromých zpráv""", width=rozmer, height=rozmer)
        .configure_title(font="Asap", color="#3d3c3b")
        .configure_view(strokeWidth=1, stroke="#6f8685")
    )

    me_to_neurazi(kvadranty2, kredity="", soubor="10_chat", slozka="grafy")

    kvadranty2
    return


if __name__ == "__main__":
    app.run()
