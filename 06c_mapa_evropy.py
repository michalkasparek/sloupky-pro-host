import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl
    import altair as alt
    import yaml
    import re
    import pycountry
    from pathlib import Path
    from vega_datasets import data

    return Path, alt, pl, pycountry, re, yaml


@app.cell
def _(alt):
    from src.kristi_promin import kristi_promin
    from src.me_to_neurazi import me_to_neurazi

    alt.themes.register("irozhlas", kristi_promin)
    alt.theme.enable("irozhlas")
    alt.data_transformers.disable_max_rows()
    return


@app.cell
def _(Path, re, yaml):
    folder_path = "data/gemini-analyza-ukazek"
    folder = Path(folder_path)
    all_data = []

    # Find yaml, yml, and txt files (since LLM outputs are often saved as .txt)
    if folder.exists() and folder.is_dir():
        data_files = (
            list(folder.glob("*.yaml"))
            + list(folder.glob("*.yml"))
            + list(folder.glob("*.txt"))
        )

        for file_path in data_files:
            with open(file_path, "r", encoding="utf-8") as file:
                raw_text = file.read().strip()

                # Clean up LLM markdown block formatting if present
                # Removes starting ```yaml (or just ```) and the trailing ```
                raw_text = re.sub(
                    r"^```(?:yaml|yml)?\s*\n", "", raw_text, flags=re.IGNORECASE
                )
                raw_text = re.sub(r"\n\s*```\s*$", "", raw_text)

                try:
                    # Load from the cleaned text string rather than directly from the file
                    content = yaml.safe_load(raw_text)

                    if content is None:
                        continue

                    # Flatten lists or append dictionaries
                    if isinstance(content, list):
                        all_data.extend(content)
                    elif isinstance(content, dict):
                        all_data.append(content)

                except yaml.YAMLError as e:
                    print(f"Error parsing {file_path.name}: {e}")
    else:
        print(f"Directory not found: {folder_path}")
    return (all_data,)


@app.cell
def _(pl):
    datatypy = {
        "staty": pl.List(pl.String),
        "obce": pl.List(pl.String),
        "ulice": pl.List(pl.String),
        "zvirata": pl.List(pl.String),
        "odpocinek": pl.List(pl.String),
        "sex": pl.Boolean,
        "nasili": pl.Boolean,
        "pocasi": pl.Boolean,
        "alkohol": pl.Boolean,
        "praha": pl.Boolean,
        "beletrie": pl.Boolean,
    }
    return (datatypy,)


@app.cell
def _(all_data):
    filtered_data = ({"staty": d.get("staty")} for d in all_data)
    return (filtered_data,)


@app.cell
def _(datatypy, filtered_data, pl):
    df_cs = pl.DataFrame(filtered_data, strict=False, schema_overrides=datatypy)
    return (df_cs,)


@app.cell
def _(df_cs):
    df_cs
    return


@app.cell
def _(df_cs, pl):
    df_cs.explode("staty").filter(pl.col("staty").str.contains("Slovens"))
    return


@app.cell
def _(df_cs, pl):
    staty = (
        df_cs.explode("staty")
        .select(pl.col("staty"))
        .unique()
        .sort(by="staty")
        .to_series()
        .to_list()
    )
    staty
    return (staty,)


@app.cell
def _(staty):
    len(staty)
    return


@app.cell
def _():
    prejmenovani = {
        None: None,
        "Aden": "Aden",
        "Afghánistán": "Afghanistan",
        "Afrika": None,
        "Albánie": "Albania",
        "Alžírsko": "Algeria",
        "Angeldom": None,
        "Argentina": "Argentina",
        "Arkastie": None,
        "Austrálie": "Australia",
        "Avónie": None,
        "Belgie": "Belgium",
        "Bosna a Hercegovina": "Bosnia and Herzegovina",
        "Brazílie": "Brazil",
        "Bulharsko": "Bulgaria",
        "Byzanc": "Byzantine Empire",
        "Centrální impérium": None,
        "Chile": "Chile",
        "Chorvatsko": "Croatia",
        "Dánsko": "Denmark",
        "Egypt": "Egypt",
        "Etiopie": "Ethiopia",
        "Evropa": None,
        "Finsko": "Finland",
        "Francie": "France",
        "Heaven": None,
        "Hengerone": None,
        "Indie": "India",
        "Indonésie": "Indonesia",
        "Irsko": "Ireland",
        "Irák": "Iraq",
        "Itálie": "Italy",
        "Japonsko": "Japan",
        "Jemen": "Yemen",
        "Jihoafrická republika": "South Africa",
        "Jižní Korea": "South Korea",
        "Jugoslávie": "Yugoslavia",
        "Kanada": "Canada",
        "Kazachstán": "Kazakhstan",
        "Kypr": "Cyprus",
        "Ledové pustiny": None,
        "Libanon": "Lebanon",
        "Likario": None,
        "Litva": "Lithuania",
        "Lotyšsko": "Latvia",
        "Lucembursko": "Luxembourg",
        "Luna": None,
        "Mauricius": "Mauritius",
        "Maďarsko": "Hungary",
        "Merodie": None,
        "Mexiko": "Mexico",
        "Mongolsko": "Mongolia",
        "Moravské království": None,  # Moravia was historically a Margraviate, not a sovereign Kingdom
        "Nepál": "Nepal",
        "Norsko": "Norway",
        "Německo": "Germany",
        "Orcigard": None,
        "Palestina": "Palestine",
        "Persie": "Persia",
        "Peru": "Peru",
        "Polsko": "Poland",
        "Portugalsko": "Portugal",
        "Rakousko": "Austria",
        "Rakousko-Uhersko": "Austria-Hungary",
        "Rumunsko": "Romania",
        "Rusko": "Russia",
        "Rwanda": "Rwanda",
        "Severní Makedonie": "North Macedonia",
        "Sierra Leone": "Sierra Leone",
        "Singapur": "Singapore",
        "Skotsko": "Scotland",
        "Slovensko": "Slovakia",
        "Sovětský svaz": "Soviet Union",
        "Spojené království": "United Kingdom",
        "Spojené království Velké Británie a Irska": "United Kingdom of Great Britain and Ireland",
        "Spojené státy americké": "United States of America",
        "Srbsko": "Serbia",
        "Srí Lanka": "Sri Lanka",
        "Sunflowerlands": None,
        "Svatá říše římská": "Holy Roman Empire",
        "Sýrie": "Syria",
        "Tchaj-wan": "Taiwan",
        "Thajsko": "Thailand",
        "Thonnierika": None,
        "Tibet": "Tibet",
        "Tunisko": "Tunisia",
        "Turecko": "Turkey",
        "Tádžikistán": "Tajikistan",
        "Uhersko": "Kingdom of Hungary",
        "Ukrajina": "Ukraine",
        "Uzbekistán": "Uzbekistan",
        "Vatikán": "Vatican City",
        "Velká Británie": "Great Britain",
        "Velká Morava": "Great Moravia",
        "Vietnam": "Vietnam",
        "Východofranská říše": "East Francia",
        "Země": None,
        "Země chladu": None,
        "Země kostí": None,
        "Země králů": None,
        "Země ohně": None,
        "Země růží": None,
        "Země stínů": None,
        "Země světla": None,
        "Írán": "Iran",
        "Česko": "Czechia",
        "Československo": "Czechoslovakia",
        "Česká republika": "Czech Republic",
        "Čína": "China",
        "Čínská lidová republika": "People's Republic of China",
        "Řecko": "Greece",
        "Španělsko": "Spain",
        "Švédsko": "Sweden",
        "Švýcarsko": "Switzerland",
    }
    return (prejmenovani,)


@app.cell
def _():
    prejmenovani_2 = {
        "Czechia": "Czech Republic",
        "Aden": None,
        "Soviet Union": "Russian Federation",
        "Rus": "Russian Federation",
        "Austria-Hungary": "Austria",
        "Czechoslovakia": "Czech Republic",
        "Anglie": "United Kingdom",
        "United Kingdom of Great Britain and Ireland": "United Kingdom",
        "Kingdom of Hungary": "Hungary",
        "Izrael": "Israel",
        "Nizozemsko": "Netherlands",
        "Estonsko": "Estonia",
        'Turkey':'Türkiye',
        "Island":"Iceland",
        "Slovinsko":"Slovenia",
        "Británie": "United Kingdom",
        "Spojené království Velké Británie a Severního Irska":"United Kingdom",
        "Great Britain":"United Kingdom",
        "Scotland": "United Kingdom",
        "Černá Hora": "Montenegro",
        "Russia":"Russian Federation",
        "Rakouská republika":"Austria",
        "Uhry":"Hungary",
        "USA":"United States of America",
        "People's Republic of China":"China"
    }
    return (prejmenovani_2,)


@app.cell
def _(pycountry):
    def get_country_id(name: str) -> int | None:
        try:
            # First, try an exact match (fastest)
            country = pycountry.countries.get(name=name)
            if country:
                return int(country.numeric)

            # If exact match fails, try a fuzzy search (handles USA, Russia, etc.)
            country = pycountry.countries.search_fuzzy(name)[0]
            return int(country.numeric)

        except (LookupError, AttributeError):
            # Return None if the country name is completely unrecognized
            return None

    return (get_country_id,)


@app.cell
def _(df_cs, get_country_id, pl, prejmenovani, prejmenovani_2):
    df = (
        df_cs.explode("staty")
        .with_columns(pl.col("staty").replace(prejmenovani))
        .with_columns(pl.col("staty").replace(prejmenovani_2))
        .group_by("staty")
        .len()
        .sort(by="len", descending=True)
        .drop_nulls()
        .rename({"staty": "country_name", "len": "n"})
        .with_columns(
            pl.col("country_name").map_elements(get_country_id).alias("id")
        )
        .with_columns(pl.col("id").cast(str))
        .with_columns(pl.col("id").str.pad_start(3,"0"))
        .with_columns(
            pl.when(pl.col("country_name") == "Kosovo").then(pl.lit("XK")).otherwise(pl.col('id')).alias('id')
        )
    )
    return (df,)


@app.cell
def _(df):
    df
    return


@app.cell
def _(df, pl):
    df.filter(pl.col("id").is_null())
    return


@app.cell
def _(df, pl):
    df.filter(pl.col("country_name").str.contains("Kosov"))
    return


@app.cell
def _(df, pl):
    vickrat = df.group_by("id").len().filter(pl.col("len") > 1).drop_nulls().select(pl.col("id")).to_series().to_list()
    df.filter(pl.col("id").is_in(vickrat))
    return


@app.cell
def _(alt):
    high_res_map_url = (
        "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json"
    )
    world_map = alt.topo_feature(high_res_map_url, "countries")
    return (world_map,)


@app.cell
def _(alt, world_map):
    background = alt.Chart(world_map).mark_geoshape(
        fill="#ECEADC", stroke="white", strokeWidth=1.5
    )
    return (background,)


@app.cell
def _(alt, df, world_map):
    choropleth = (
        alt.Chart(world_map)
        .mark_geoshape(
            # Removed the hardcoded color from here so the encoding can take over
            stroke="white",  # Country border color
            strokeWidth=0.5,
        )
        .transform_lookup(
            lookup="id", from_=alt.LookupData(df, "id", ["n", "country_name"])
        )
        .encode(
            # Encode color dynamically based on column "n"
            color=alt.Color(
                "n:Q",
                scale=alt.Scale(
                    scheme="purples",  # Try "blues", "viridis", or "reds" depending on your preference
                    domain=[0, 100]    # Adjust domain based on your actual min/max 'n'
                ),
                title="Value"          # This adds a title to your color legend
            ),
            # Add hover tooltips
            tooltip=[
                alt.Tooltip("country_name:N", title="Country"),
                alt.Tooltip("n:Q", title="Value (n)"),
            ],
        )
    )
    return (choropleth,)


@app.cell
def _(alt, background, choropleth):
    europe_map = (
        (background + choropleth)
        .project(
            type="mercator",
            center=[15, 53],  # Longitude/Latitude center point for Europe
            scale=600,  # Zoom factor
        )
        .properties(
            title=alt.Title(
                "Zmínky o evropských zemích v české beletrii 20. let",
                subtitle=[
                    "Analýza čtyř milionů slov ukázek z 943 knih. Každý autor či autorka byli ve vzorku zastoupeni maximálně dvakrát.",
                    "Zmínky hledala AI. Muselo jít o zeměpisné zmínky zemí či jejich částí („jeli jsme na Sícilii“ je zmínka Itálie), ne o jiné významy („podej mi francouzský klíč“ není zmínka Francie).",
                    "Tato strojová práce prošla namátkovou lidskou kontrolou.",
                ],
                fontSize=20,
            ),
            width=900,
            height=530,
        )
    )
    return (europe_map,)


@app.cell
def _(europe_map):
    europe_map
    return


if __name__ == "__main__":
    app.run()
