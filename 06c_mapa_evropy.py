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
    import geopandas as gpd
    from vega_datasets import data
    import marimo as mo

    return Path, alt, gpd, mo, pl, pycountry, re, yaml


@app.cell
def _(alt):
    from src.kristi_promin import kristi_promin
    from src.me_to_neurazi import me_to_neurazi

    alt.themes.register("irozhlas", kristi_promin)
    alt.theme.enable("irozhlas")
    alt.data_transformers.disable_max_rows()
    return (me_to_neurazi,)


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

                    # Extract the filename without the extension (e.g., 'book1' from 'book1.yaml')
                    # Note: If you want the extension included, use `file_path.name` instead.
                    isbn_value = file_path.stem

                    # Flatten lists or append dictionaries, injecting the ISBN
                    if isinstance(content, list):
                        # If it's a list of dictionaries, add the ISBN to each dictionary
                        for item in content:
                            if isinstance(item, dict):
                                item["isbn"] = isbn_value
                        all_data.extend(content)

                    elif isinstance(content, dict):
                        # Add the ISBN to the single dictionary
                        content["isbn"] = isbn_value
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
def _(all_data, datatypy, isbn_ceske_beletrie, nazvy, pl):
    filtered_data = (
        {
            "staty": d.get("staty"),
            "isbn": d.get("isbn"),
            "nasili": d.get("nasili"),
            "obce": d.get("obce"),
            "ulice": d.get("ulice"),
            "alkohol": d.get("alkohol"),
            "sex": d.get("sex"),
            "odpocinek": d.get("odpocinek"),
        }
        for d in all_data
    )

    df_cs = (
        pl.DataFrame(filtered_data, strict=False, schema_overrides=datatypy)
        .filter(pl.col("isbn").is_in(isbn_ceske_beletrie))
        .join(nazvy, how="left", on="isbn")
        .with_columns(pl.col("staty").list.len().alias("pocet_zemi"))
        .sort(by="pocet_zemi", descending=True)
        .unique(subset="autorstvo", keep="first")
    )
    return (df_cs,)


@app.cell
def _(df_cs):
    df_cs
    return


@app.cell
def _(df_cs):
    df_cs.explode("obce").group_by("obce").len().sort(
        by="len", descending=True
    ).drop_nulls()
    return


@app.cell
def _():
    417 / 46
    return


@app.cell
def _():
    return


@app.cell
def _(df_cs):
    df_cs.explode("ulice").group_by("ulice").len().sort(
        by="len", descending=True
    ).drop_nulls()
    return


@app.cell
def _(df_cs):
    df_cs.explode("odpocinek").group_by("odpocinek").len().sort(
        by="len", descending=True
    ).drop_nulls()
    return


@app.cell
def _():
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
        "Byzanc": None,
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
        "Jugoslávie": None,
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
        "Rakousko-Uhersko": None,
        "Rumunsko": "Romania",
        "Rusko": "Russia",
        "Rwanda": "Rwanda",
        "Severní Makedonie": "North Macedonia",
        "Sierra Leone": "Sierra Leone",
        "Singapur": "Singapore",
        "Skotsko": "Scotland",
        "Slovensko": "Slovakia",
        "Sovětský svaz": None,
        "Spojené království": "United Kingdom",
        "Spojené království Velké Británie a Irska": "United Kingdom of Great Britain and Ireland",
        "Spojené státy americké": "United States of America",
        "Srbsko": "Serbia",
        "Srí Lanka": "Sri Lanka",
        "Sunflowerlands": None,
        "Svatá říše římská": None,
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
        "Velká Morava": None,
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
        "Soviet Union": None,
        "Rus": "Russian Federation",
        "Austria-Hungary": None,
        "Czechoslovakia": None,
        "Anglie": "United Kingdom",
        "United Kingdom of Great Britain and Ireland": "United Kingdom",
        "Kingdom of Hungary": None,
        "Izrael": "Israel",
        "Nizozemsko": "Netherlands",
        "Estonsko": "Estonia",
        "Turkey": "Türkiye",
        "Island": "Iceland",
        "Slovinsko": "Slovenia",
        "Británie": "United Kingdom",
        "Spojené království Velké Británie a Severního Irska": "United Kingdom",
        "Great Britain": "United Kingdom",
        "Scotland": "United Kingdom",
        "Černá Hora": "Montenegro",
        "Russia": "Russian Federation",
        "Rakouská republika": "Austria",
        "Uhry": None,
        "USA": "United States of America",
        "People's Republic of China": "China",
        "Monako": "Monaco",
        "Rakouské císařství": None,
        "Bavorsko": "Germany",
        "Německá říše": None,
        "North Macedonia": "Macedonia",
        "Gruzie": "Georgia",
        "Arménie": "Armenia",
        "Rakouské vévodství": "Austria",
        "Maroko": "Morocco",
        "Prusko": None,
        "Ázerbájdžán": "Azerbaijan",
        "Pol": "Poland",
        "Venkov": None,
        "Ler": None,
        "Západ": None,
        "Wales": "United Kingdom",
        "Spojené arabské emiráty": "United Arab Emirates",
        "Bělorusko": "Belarus",
        "Moldavsko": "Moldova",
        "Jordánsko": "Jordan",
        "Bosna": "Bosnia and Herzegovina",
        "Nigérie": "Nigeria",
        "Keňa": "Kenya",
        "Severní Korea": "North Korea",
        "Jižní Súdán": "South Sudan",
        "Lichtenštejnsko": "liechtenstein",
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
        .with_columns(pl.col("id").str.pad_start(3, "0"))
        .with_columns(
            pl.when(pl.col("country_name") == "Kosovo")
            .then(pl.lit("296"))
            .otherwise(pl.col("id"))
            .alias("id")
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
    vickrat = (
        df.group_by("id")
        .len()
        .filter(pl.col("len") > 1)
        .drop_nulls()
        .select(pl.col("id"))
        .to_series()
        .to_list()
    )
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
def _(gpd, pl):
    # 1. Read the dataset directly from Natural Earth's URL
    url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    gdf = gpd.read_file(url)

    # 2. Calculate the centroids for text placement
    # (Using a projected CRS for accurate centroids is generally recommended,
    # but for basic map visualization, doing it on the unprojected data often suffices)
    gdf["lon"] = gdf.geometry.centroid.x
    gdf["lat"] = gdf.geometry.centroid.y

    # 3. Extract and format the numeric ID
    # Convert to string and pad with zeros to ensure it's exactly 3 digits (e.g., "4" -> "004")
    # We also replace '-99' (Natural Earth's placeholder for missing codes) with None/NaN if needed
    gdf["numeric_id"] = gdf["ISO_N3"].astype(str).str.zfill(3)

    print(gdf.columns.to_list())

    gdf_pl = pl.from_pandas(gdf.drop(columns=["geometry"])).select(
        pl.col(
            ["ISO_N3", "ISO_A3", "ISO_A3_EH", "ISO_N3_EH", "lat", "lon", "NAME"]
        )
    )
    return (gdf_pl,)


@app.cell
def _(gdf_pl, pl):
    gdf_pl.filter(pl.col("NAME").str.contains("Franc"))
    return


@app.cell
def _(df, df_cs, gdf_pl, pl):
    do_grafu = (
        df.join(gdf_pl, how="left", left_on="id", right_on="ISO_N3_EH")
        .with_columns(
            pl.when(pl.col("country_name") == "Kosovo")
            .then(pl.lit(42.579367131816994))
            .otherwise(pl.col("lat"))
            .alias("lat"),
            pl.when(pl.col("country_name") == "Kosovo")
            .then(pl.lit(20.895355721342227))
            .otherwise(pl.col("lon"))
            .alias("lon"),
        )
        .with_columns(
            ((pl.col("n") / pl.col("n").max()) * 100)
            .round(1)
            .alias("podil_z_maxima"),
            ((pl.col("n") / len(df_cs)) * 100).round(1).alias("podil"),
        )
        .with_columns(pl.col("podil").sqrt().alias("podil_odmocnica"))
    )
    return (do_grafu,)


@app.cell
def _(do_grafu):
    do_grafu.sort(by="podil", descending=True).with_row_index(offset=1)
    return


@app.cell
def _(do_grafu, pl):
    do_grafu.filter(pl.col("country_name").str.contains("Bela"))
    return


@app.cell
def _(do_grafu, pl):
    do_grafu.filter(pl.col("country_name").str.contains("Kosov"))
    return


@app.cell
def _(do_grafu, pl):
    do_grafu.filter(pl.col("country_name").str.contains("Kos"))
    return


@app.cell
def _(world_map):
    print(world_map)
    return


@app.cell
def _(df_cs):
    podtitul = [
        f"Analýza tří milionů slov ukázek z {len(df_cs)} knih. Každý autor či autorka byli ve vzorku zastoupeni jen jednou.",
        "Zmínky hledala AI. Muselo jít o zeměpisné zmínky zemí či jejich částí („jeli jsme na Sícilii“ je zmínka Itálie), ne o jiné významy („podej mi francouzský klíč“ není zmínka Francie).",
        "Tato strojová práce prošla namátkovou lidskou kontrolou.",
        "Kompletní kód analýzy i seznam knih je k nahlédnutí na github.com/michalkasparek/sloupky-pro-host.",
    ]
    return (podtitul,)


@app.cell
def _(alt, background, do_grafu, podtitul, world_map):
    choropleth = (
        alt.Chart(world_map)
        .mark_geoshape(
            # Removed the hardcoded color from here so the encoding can take over
            stroke="white",  # Country border color
            strokeWidth=0.5,
        )
        .transform_lookup(
            # Look up "podil_z_maxima" instead of "n"
            lookup="id",
            from_=alt.LookupData(do_grafu, "id", ["podil", "country_name"]),
        )
        .encode(
            # Encode color dynamically based on column "podil_z_maxima"
            color=alt.Color(
                "podil:Q",
                scale=alt.Scale(
                    scheme="reds",
                    type="symlog",  # Great for massive outliers, safe for zero
                    constant=10,  # Adjust this if needed; dictates where the log curve starts
                ),
                title="Podíl",
            ),
            # Add hover tooltips
            tooltip=[
                alt.Tooltip("country_name:N", title="Country"),
                alt.Tooltip("podil:Q", title="Podíl"),
            ],
        )
    )

    # 2. Create the Text Layer
    text_layer = (
        alt.Chart(world_map)
        .mark_text(
            align="center",
            baseline="middle",
            color="black",  # Text color (adjust if your map is very dark)
            fontSize=11,
        )
        .transform_lookup(
            # Note: We need 'lat' and 'lon' from your dataframe to know where to place the text
            lookup="id",
            from_=alt.LookupData(
                do_grafu, "id", ["podil", "country_name", "lat", "lon"]
            ),
        )
        .transform_filter(
            # Hide the label for countries that have no data (null values)
            "isValid(datum.podil)"
        )
        .transform_calculate(
            # Dynamically create the string format.
            # You may want to change '×' to '%' depending on how you want to display the share.
            # If it's a raw decimal (e.g., 0.5), you might want to format it: label="round(datum.podil_z_maxima * 100) + '%'"
            label="datum.podil < 1 ? '<1 %' : replace(toString(datum.podil), '.', ',') + ' %'"
        )
        .encode(
            longitude="lon:Q",  # X-coordinate for text
            latitude="lat:Q",  # Y-coordinate for text
            text="label:N",  # Display the calculated label
            # Optional: Add the same tooltips so hover works over the text
            tooltip=[
                alt.Tooltip("country_name:N", title="Country"),
                alt.Tooltip("podil:Q", title="Podíl"),
            ],
        )
    )

    europe_map = (
        (background + choropleth + text_layer)
        .project(
            type="mercator",
            center=[15, 53],  # Longitude/Latitude center point for Europe
            scale=600,  # Zoom factor
        )
        .properties(
            title=alt.Title(
                "Zmínky o evropských zemích v české beletrii této dekády",
                subtitle=podtitul,
                fontSize=20,
            ),
            width=1000,
            height=1000,
        )
    )
    return (europe_map,)


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _(europe_map):
    europe_map
    return


@app.cell
def _(europe_map, me_to_neurazi):
    me_to_neurazi(graf=europe_map, kredity="", soubor="06_mapa_evropy")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fakt tak málo Slovenska?

    TLDR: Není to stoprocentně přesné, ale reálně je ho málo.
    """)
    return


@app.cell
def _(pl):
    isbn_ceske_beletrie = (
        pl.read_csv("data/isbn_beletrie.csv")
        .with_columns(pl.col("020_a").str.replace_all("-", ""))
        .select(pl.col("020_a"))
        .drop_nulls()
        .to_series()
        .to_list()
    )
    return (isbn_ceske_beletrie,)


@app.cell
def _(pl):
    nazvy = (
        pl.read_parquet("../knizni-peoplemetr/data/cnb_vyber.parquet")
        .explode("020_a")
        .with_columns(pl.col("020_a").str.replace_all("-", ""))
        .with_columns(
            (pl.col("100_a") + pl.lit(" | ") + pl.col("245_a")).alias("kniha")
        )
        .rename({"020_a": "isbn", "100_a": "autorstvo"})
        .select(pl.col(["isbn", "kniha", "autorstvo"]))
        .drop_nulls()
    )
    return (nazvy,)


@app.cell
def _(isbn_ceske_beletrie, nazvy, pl):
    ukazky_ceske_beletrie = (
        pl.read_parquet("../knizni-peoplemetr/data/ukazky_ebooku.parquet")
        .filter(pl.col("isbn").is_in(isbn_ceske_beletrie))
        .join(nazvy, how="left", on="isbn")
        .with_columns(pl.col("text").str.split(" ").list.len().alias("slov"))
        .unique(subset="kniha")
        .filter(pl.col("slov") > 10)
    )
    return (ukazky_ceske_beletrie,)


@app.cell
def _(pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.filter(pl.col("text").str.contains("(?i) turec"))
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.filter(pl.col("text").str.contains("(?i) slovens"))
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.with_columns(
        pl.col("text").str.split("Bratisl").list.slice(1, 1)
    ).explode("text").filter(pl.col("text").str.len_bytes() > 5)
    return


@app.cell
def _(df_cs, pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.with_columns(
        pl.col("text").str.split(" Košic").list.slice(1, 1)
    ).explode("text").filter(pl.col("text").str.len_bytes() > 5).join(
        df_cs, how="left", on="isbn"
    )
    return


@app.cell
def _(df_cs, pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.with_columns(
        pl.col("text").str.split(" Bratisl").list.slice(1, 1)
    ).explode("text").filter(pl.col("text").str.len_bytes() > 5).join(
        df_cs, how="left", on="isbn"
    )
    return


@app.cell
def _(df_cs, pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.with_columns(
        pl.col("text").str.split(" Tat[er]").list.slice(1, 1)
    ).explode("text").filter(pl.col("text").str.len_bytes() > 5).join(
        df_cs, how="left", on="isbn"
    )
    return


@app.cell
def _(df_cs, pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.with_columns(
        pl.col("text").str.split(" Žilin").list.slice(1, 1)
    ).explode("text").filter(pl.col("text").str.len_bytes() > 5).join(
        df_cs, how="left", on="isbn"
    )
    return


@app.cell
def _(df_cs, pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.with_columns(
        pl.col("text").str.split(" Slovens").list.slice(1, 1)
    ).explode("text").filter(pl.col("text").str.len_bytes() > 5).join(
        df_cs, how="left", on="isbn"
    )
    return


@app.cell
def _(df_cs, pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.with_columns(
        pl.col("text").str.split(" Německ").list.slice(1, 1)
    ).explode("text").filter(pl.col("text").str.len_bytes() > 5).join(
        df_cs, how="left", on="isbn"
    )
    return


@app.cell
def _(df_cs, pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.filter(pl.col("kniha").str.contains("Fosilie")).join(
        df_cs, how="left", on="isbn"
    )
    return


@app.cell
def _():
    return


@app.cell
def _(df_cs, pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.with_columns(
        pl.col("text").str.split(" slovens").list.slice(1, 1)
    ).explode("text").filter(pl.col("text").str.len_bytes() > 5).join(
        df_cs, how="left", on="isbn"
    )
    return


@app.cell
def _(df_cs, pl, ukazky_ceske_beletrie):
    df_cs.join(ukazky_ceske_beletrie, how="left", on="isbn").select(
        pl.col("slov").sum()
    )
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.select(pl.col("slov").median())
    return


@app.cell
def _(df_cs, pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.join(df_cs, how="left", on="isbn").filter(
        pl.col("text").str.contains("Horom")
    )
    return


@app.cell
def _(df_cs, pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.join(df_cs, how="left", on="isbn").explode(
        "obce"
    ).filter(pl.col("obce") == "Horoměřice")
    return


@app.cell
def _(df_cs, pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.with_columns(
        pl.col("text").str.split("Slovens").list.slice(1, 1)
    ).explode("text").filter(pl.col("text").str.len_bytes() > 5).join(
        df_cs, how="left", on="isbn"
    )
    return


@app.cell
def _(df_cs, pl, prejmenovani, prejmenovani_2, ukazky_ceske_beletrie):
    kontrola = (
        df_cs.join(ukazky_ceske_beletrie, how="left", on="isbn")
        .drop(["text", "autorstvo", "slov"])
        .sort(by="kniha")
        .join(
            df_cs.explode("staty")
            .with_columns(pl.col("staty").replace(prejmenovani))
            .with_columns(pl.col("staty").replace(prejmenovani_2))
            .group_by("isbn")
            .agg(pl.col("staty"))
            .rename({"staty": "staty_ciste"}),
            how="left",
            on="isbn",
        )
    )

    kontrola
    return (kontrola,)


@app.cell
def _(kontrola):
    kontrola.write_ndjson("data/06_kontrola_zminek_zemi_v_beletrii.json")
    return


@app.cell
def _(ukazky_ceske_beletrie):
    ukazky_ceske_beletrie
    return


@app.cell
def _(df_cs, pl):
    df_cs.select(pl.col(["kniha", "staty"])).with_columns(
        pl.col("staty").list.join(", ")
    ).sort(by="kniha").write_csv("06d_seznam_knih_a_statu.csv")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Země versus témata
    """)
    return


@app.cell
def _(df_cs, pl, prejmenovani, prejmenovani_2):
    def podily(sloupec):
        return (
            df_cs.explode("staty")
            .with_columns(pl.col("staty").alias("country"))
            .with_columns(pl.col("country").replace(prejmenovani))
            .with_columns(pl.col("country").replace(prejmenovani_2))
            .group_by(["country", sloupec])
            .len()
            .drop_nulls()
            .pivot(index="country", on=sloupec, values="len")
            .fill_null(1)
            .with_columns(
                (pl.col("true") / (pl.col("true") + pl.col("false"))).alias(
                    "podil"
                ),
                (pl.col("true") + pl.col("false")).alias("celkem"),
            )
            .sort(by="podil")
        )

    return (podily,)


@app.cell
def _(pl, podily):
    podily("sex").filter(pl.col("celkem") > 10)
    return


@app.cell
def _(pl, podily):
    podily("nasili").filter(pl.col("celkem") > 10)
    return


@app.cell
def _(pl, podily):
    podily("alkohol").filter(pl.col("celkem") > 10)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Světové strany
    """)
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    len(ukazky_ceske_beletrie.filter(pl.col("text").str.contains(r"Západ[^n]")))
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    len(
        ukazky_ceske_beletrie.filter(pl.col("text").str.contains(r"\w Západ[^no]"))
    )
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    len(ukazky_ceske_beletrie.filter(pl.col("text").str.contains(r"Východ[^n]")))
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    len(
        ukazky_ceske_beletrie.filter(
            pl.col("text").str.contains(r"\w Východ[^no]")
        )
    )
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    len(ukazky_ceske_beletrie.filter(pl.col("text").str.contains(r"(?i)západn")))
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    len(ukazky_ceske_beletrie.filter(pl.col("text").str.contains(r"(?i)východn")))
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    len(ukazky_ceske_beletrie.filter(pl.col("text").str.contains(r"(?i)severn")))
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    len(ukazky_ceske_beletrie.filter(pl.col("text").str.contains(r"(?i)jižn")))
    return


@app.cell
def _():
    136 / 117
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fulltext
    """)
    return


@app.cell
def _(pl, re, ukazky_ceske_beletrie):
    def hledej(termin):
        # Escape the term so special regex characters (like . or ?) don't break the pattern
        escaped_termin = re.escape(termin)

        # Build the regex pattern:
        # (?s)        -> Dotall modifier (allows '.' to match newlines)
        # ( ... )     -> Capture group 1 (this is what .extract will return)
        # .{0,150}    -> Grabs up to 150 characters before the term
        # .{0,150}    -> Grabs up to 150 characters after the term
        pattern = rf"(?s)(.{{0,70}}{escaped_termin}.{{0,70}})"

        return (
            ukazky_ceske_beletrie
            # Added literal=True to ensure it searches for the exact word, not a regex string
            .filter(pl.col("text").str.contains(termin, literal=True))
            .with_columns(
                # Extract the matching pattern from the text column
                pl.col("text").str.extract(pattern, 1).alias("text")
            )
            .select(pl.col(["text", "kniha"]))
        )

    return (hledej,)


@app.cell
def _(hledej):
    hledej("Západ")
    return


@app.cell
def _(hledej):
    hledej("Polsk")
    return


@app.cell
def _(hledej):
    hledej(" saud")
    return


@app.cell
def _(hledej):
    hledej("Slovensk")
    return


if __name__ == "__main__":
    app.run()
