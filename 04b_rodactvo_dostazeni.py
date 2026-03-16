import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import requests
    import time
    import yaml
    import polars as pl

    return pl, requests, time, yaml


@app.cell
def _(requests, time):
    HEADERS = {
        # Always include contact info so Wikimedia can reach you instead of blocking you
        "User-Agent": "WikiDataBot/1.0 (mailto:your.email@example.com) Python/3.x"
    }

    def get_wikidata_info(q_ids):
        """Batches Q-IDs to get the list of languages and the CS/DE titles."""
        results = []
        chunk_size = 50
    
        for i in range(0, len(q_ids), chunk_size):
            chunk = q_ids[i:i + chunk_size]
            url = "https://www.wikidata.org/w/api.php"
            params = {
                "action": "wbgetentities",
                "ids": "|".join(chunk),
                "props": "sitelinks",
                "format": "json"
            }
        
            response = requests.get(url, headers=HEADERS, params=params)
            data = response.json().get("entities", {})
        
            for qid, info in data.items():
                sitelinks = info.get("sitelinks", {})
                # Extract just the language prefixes (e.g., 'en', 'cs', 'de') for wikipedias
                languages = [
                    site.replace("wiki", "") for site in sitelinks.keys() if site.endswith("wiki")
                ]
            
                results.append({
                    "wikidata_id": qid,
                    "languages": languages, # List of all available languages
                    "cs_title": sitelinks.get("cswiki", {}).get("title"),
                    "de_title": sitelinks.get("dewiki", {}).get("title")
                })
            
            time.sleep(1) # Gentle pause between chunks
        return results

    def get_wikipedia_lengths(titles, lang):
        """Batches Wikipedia titles to get their page lengths in bytes."""
        # Filter out Nones (entities that don't have a page in this language)
        valid_titles = [t for t in titles if t is not None]
        if not valid_titles:
            return []
        
        results = []
        chunk_size = 50
    
        for i in range(0, len(valid_titles), chunk_size):
            chunk = valid_titles[i:i + chunk_size]
            url = f"https://{lang}.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "prop": "info",
                "titles": "|".join(chunk),
                "format": "json"
            }
        
            response = requests.get(url, headers=HEADERS, params=params)
            pages = response.json().get("query", {}).get("pages", {})
        
            for page_id, page_info in pages.items():
                if page_id != "-1":
                    results.append({
                        f"{lang}_title": page_info.get("title"),
                        f"{lang}_length": page_info.get("length")
                    })
                
            time.sleep(1)
        return results

    return get_wikidata_info, get_wikipedia_lengths


@app.cell
def _(yaml):
    with open("data/rodactvo/narozeni_cr.yaml", 'r', encoding='utf-8') as file:
        # safe_load automatically parses a YAML list into a Python list
        narozeni_cr = yaml.safe_load(file)

    with open("data/rodactvo/narozeni_cr_bez_nemecke_wiki.yaml", 'r', encoding='utf-8') as file:
        # safe_load automatically parses a YAML list into a Python list
        narozeni_cr_bez_nemecke_wiki = yaml.safe_load(file)

    with open("data/rodactvo/narozeni_cr_bez_ceske_wiki.yaml", 'r', encoding='utf-8') as file:
        # safe_load automatically parses a YAML list into a Python list
        narozeni_cr_bez_ceske_wiki = yaml.safe_load(file)

    q_ids = narozeni_cr + narozeni_cr_bez_nemecke_wiki + narozeni_cr_bez_ceske_wiki

    len(q_ids)
    return (q_ids,)


@app.cell
def _(get_wikidata_info, get_wikipedia_lengths, pl, q_ids):
    print("1. Fetching Wikidata sitelinks...")
    wiki_data = get_wikidata_info(q_ids)
    df_main = pl.DataFrame(wiki_data)

    print("2. Fetching Czech page lengths...")
    cs_lengths = get_wikipedia_lengths(df_main["cs_title"].to_list(), "cs")
    df_cs = pl.DataFrame(cs_lengths, schema={"cs_title": pl.Utf8, "cs_length": pl.Int64})

    print("3. Fetching German page lengths...")
    de_lengths = get_wikipedia_lengths(df_main["de_title"].to_list(), "de")
    df_de = pl.DataFrame(de_lengths, schema={"de_title": pl.Utf8, "de_length": pl.Int64})

    print("4. Merging data together...")
    # We use left joins so we don't drop entities that lack a CS or DE page
    df_final = (
        df_main
        .join(df_cs, on="cs_title", how="left")
        .join(df_de, on="de_title", how="left")
    )

    # Optional: drop the title columns if you only wanted the lengths
    df_final = df_final.drop(["cs_title", "de_title"])

    df_final.write_json("data/rodactvo/rodactvo_nereprezentovane.json")

    print(df_final)
    return


if __name__ == "__main__":
    app.run()
