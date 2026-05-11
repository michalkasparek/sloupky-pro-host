import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import time
    from dotenv import load_dotenv
    import polars as pl
    from google import genai
    import marimo as mo

    return genai, load_dotenv, os, pl, time


@app.cell
def _(load_dotenv, os):
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    return (GEMINI_API_KEY,)


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
        .rename({"020_a": "isbn","100_a":"autorstvo"})
        .select(pl.col(["isbn", "kniha","autorstvo"]))
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
        .unique(subset="kniha").filter(pl.col("slov") > 10)
    )

    ukazky_ceske_beletrie
    return (ukazky_ceske_beletrie,)


@app.cell
def _(pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.filter(pl.col("text").str.contains("Budape"))
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.select(pl.col("slov").sum())
    return


@app.cell
def _(ukazky_ceske_beletrie):
    ukazky_ceske_beletrie
    return


@app.cell
def _(ukazky_ceske_beletrie):
    prvni_zminky = ukazky_ceske_beletrie.unique(subset="autorstvo",keep="first")
    return (prvni_zminky,)


@app.cell
def _(pl, prvni_zminky, ukazky_ceske_beletrie):
    druhe_zminky = ukazky_ceske_beletrie.filter(~pl.col("kniha").is_in(prvni_zminky.select("kniha").to_series().to_list())).unique(subset="autorstvo", keep="first")
    return (druhe_zminky,)


@app.cell
def _(druhe_zminky, pl, prvni_zminky):
    nejvys_dve_od_stejneho_cloveka = pl.concat(
        [prvni_zminky,druhe_zminky]
    )
    return (nejvys_dve_od_stejneho_cloveka,)


@app.cell
def _(nejvys_dve_od_stejneho_cloveka):
    len(nejvys_dve_od_stejneho_cloveka)
    return


@app.cell
def _(nejvys_dve_od_stejneho_cloveka, pl):
    print("\n".join(nejvys_dve_od_stejneho_cloveka.sort(by="kniha").select(pl.col("kniha")).drop_nulls().to_series().to_list()))
    return


@app.cell
def _(nejvys_dve_od_stejneho_cloveka, pl):
    nejvys_dve_od_stejneho_cloveka.select(pl.col("slov").sum())
    return


@app.cell
def _(pl, ukazky_ceske_beletrie):
    ukazky_ceske_beletrie.filter(pl.col("isbn") == "9788026721659")
    return


@app.cell
def _():
    with open("06b_prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    print(prompt)
    return (prompt,)


@app.cell
def _():
    kam = "data/gemini-analyza-ukazek"
    return (kam,)


@app.cell
def _(kam, os):
    os.makedirs(kam, exist_ok=True)
    return


@app.cell
def _(GEMINI_API_KEY, genai):
    client = genai.Client(api_key=GEMINI_API_KEY)
    return (client,)


@app.cell
def _(client, kam, nejvys_dve_od_stejneho_cloveka, os, prompt, time):
    zanalyzovane = [os.listdir(kam)]

    for radek in nejvys_dve_od_stejneho_cloveka.iter_rows(named=True):
        soubor = radek['isbn'] + ".txt"
        if soubor not in zanalyzovane:
            try:
                kompletni_prompt = prompt + radek['text']
                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite", contents=kompletni_prompt
                )
                with open(os.path.join(kam, soubor), 'w+', encoding="utf-8") as file:
                    file.write(str(response.text))
            except Exception as e:
                print(e)
                time.sleep(20)
    return


if __name__ == "__main__":
    app.run()
