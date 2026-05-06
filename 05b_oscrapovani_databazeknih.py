import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import sys
    import time
    import datetime
    import json
    import requests
    from bs4 import BeautifulSoup
    import polars as pl

    def scrape_dk(isbn):

        try:
            isbn = isbn.replace("-","")
        except:
            pass

        try:
            if len(isbn) == 13:
                url = f"""https://www.databazeknih.cz/search?q={isbn}"""
            elif "databazeknih.cz/" in isbn:
                url = isbn
            else:
                return None
        except:
            pass

        kniha = {
            "ISBN": isbn,
            "DK_date": datetime.datetime.now()
            .replace(microsecond=0)
            .strftime("%Y-%m-%d %H:%M:%S"),
        }

        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            try:
                time.sleep(120)
                r = requests.get(url)
                soup = BeautifulSoup(r.text, "html.parser")
            except:
                return {}

        try:
            kniha["DK_titul"] = soup.find("title").text.split("-")[0].strip()
        except:
            pass
        if kniha["DK_titul"] == "Vyhledávání | Databáze knih":
            return None

        try:
            detail_description = soup.find(class_="detail_description")
            for span in detail_description.find_all("span"):
                if len(span.text.strip()) == 4:
                    kniha["DK_vyslo"] = int(span.text.strip())
        except Exception as E:
            pass

        try:
            kniha["DK_rating"] = int(
                soup.find(class_=lambda c: c and c.startswith("hodnoceni"))
                .text.split(" ")[0]
                .strip()
            )
        except:
            pass

        try:
            kurzivy = soup.find_all("i")
            for k in kurzivy:
                if "hodnocení" in k.text:
                    kniha["DK_ratings_count"] = int(k.text.split(" hodnocení")[0].strip())
        except:
            pass


        try:
            kniha["DK_autorstvo"] = soup.find(class_="author").text.strip()
        except:
            pass

        kniha["DK_tags"] = [s.text for s in soup.find_all(class_="tag")]

        try:
            for potencialni_popisek in soup.find_all(class_="new2 odtop"):
                if (potencialni_popisek.text.strip() != "Chci vypnout reklamy") and ("Nebo se staňte členem DK Premium a využijte" not in potencialni_popisek.text.strip()) and (potencialni_popisek.text.strip() != "Zobrazit vše"):
                    kniha['anotace'] = potencialni_popisek.text.replace('... celý text','').strip()
        except:
            pass

        try:
            tabulka = soup.find(class_="morePadding")
            for tr in tabulka.find_all("tr"):
                try:
                    kniha[
                        f"""DK_{tr.find_all('td')[0].text.strip().replace(" ","_")}"""
                    ] = int(
                        tr.find_all("td")[1].text.replace("x", "").replace(" ", "").strip()
                    )
                except:
                    pass
        except:
            pass

        return kniha

    return datetime, os, pl, scrape_dk


@app.cell
def _(scrape_dk):
    scrape_dk("9788076375031")
    return


@app.cell
def _(datetime):
    current_date = datetime.datetime.now()
    date_string = current_date.strftime("%Y_%m_%d")

    slozka = f"data/databazeknih/{date_string}"
    return date_string, slozka


@app.cell
def _(pl):
    schema = {
        "ISBN": pl.String,
        "DK_titul": pl.String,
        "DK_vyslo": pl.String,
        "DK_date": pl.String,
        "anotace": pl.String,
        "DK_autorstvo": pl.String,
        "DK_tags": pl.List(pl.String),
        "DK_rating": pl.Int64,
        "DK_ratings_count": pl.Int64,
        "DK_v_Přečtených": pl.Int64,
        "DK_v_Doporučených": pl.Int64,
        "DK_v_Mé_knihovně": pl.Int64,
        "DK_v_Právě_čtených": pl.Int64,
        "DK_ve_Čtenářské_výzvě": pl.Int64,
        "DK_v_Chystám_se_číst": pl.Int64,
        "DK_v_Chci_si_koupit": pl.Int64,
        "DK_v_dalších_seznamech": pl.Int64,
    }
    return (schema,)


@app.cell
def _(pl, schema):
    isbns_scraped = set(
        pl.scan_parquet(
            f"data/databazeknih/*/*.parquet",
            schema=schema,
            missing_columns="insert",
            cast_options=pl.ScanCastOptions(integer_cast="upcast"),
        )
        .select(pl.col("ISBN"))
        .collect()
        .to_series()
        .to_list()
    )
    return (isbns_scraped,)


@app.cell
def _(isbns_scraped):
    isbns_scraped
    return


@app.cell
def _(isbns_scraped, pl):
    isbns_pre = [x for x in pl.read_csv('data/isbn_beletrie.csv').to_series().to_list() if x != None]
    isbns = [x.replace('-','') for x in isbns_pre if x.replace('-','') not in isbns_scraped]
    return isbns, isbns_pre


@app.cell
def _(isbns_pre):
    len(isbns_pre)
    return


@app.cell
def _(isbns):
    len(isbns)
    return


@app.cell
def _(isbns):
    isbns[0:10]
    return


@app.cell
def _(date_string, datetime, isbns, os, pl, scrape_dk, slozka):
    if not os.path.exists(slozka):
        os.makedirs(slozka)

    dknih = []
    count = 0
    pribylo = False
    for i in isbns:
        prirustek = scrape_dk(i)
        print(prirustek)
        if prirustek != None:
            count += 1
            pribylo = True
            dknih.append(prirustek)
        if count % 50 == 0:
            time_string = datetime.datetime.now().strftime("%H_%M_%S")
            if pribylo == True:
                pl.DataFrame(dknih).write_parquet(
                    os.path.join(
                        slozka,
                        f"databazeknih_{date_string}_{time_string}.parquet",
                    )
                )
                print(f"databazeknih_{date_string}_{time_string}.parquet")
                dknih = []
                pribylo = False
    pl.DataFrame(dknih).write_parquet(
        os.path.join(
            slozka,
            f"databazeknih_{date_string}_{time_string}.parquet",
        )
    )
    print("Hotovo.")
    return


@app.cell
def _(date_string, os, pl, schema, slozka):
    pl.scan_parquet(
        f"{slozka}/*.parquet",
        schema=schema,
        missing_columns="insert",
        cast_options=pl.ScanCastOptions(integer_cast="upcast"),
    ).filter(~pl.col("DK_titul").str.contains("Vyhledávání knih")).sort(
        by="DK_date", descending=True
    ).unique(subset=["ISBN"]).rename(
        {'anotace':'DK_anotace'}
    ).with_columns(
        pl.col("DK_vyslo").cast(pl.Int64,strict=False)
    ).sink_parquet(
        os.path.join("data/databazeknih", f"databaze_knih_{date_string}.parquet")
    )
    return


if __name__ == "__main__":
    app.run()
