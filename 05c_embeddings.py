import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import os

    return (os,)


@app.cell
def _():
    import polars as pl
    from sentence_transformers import SentenceTransformer
    from sklearn.decomposition import PCA
    from sklearn.metrics.pairwise import cosine_similarity

    return SentenceTransformer, cosine_similarity, pl


@app.cell
def _(pl):
    df = (
        pl.read_parquet("data/databazeknih/databaze_knih_2026_04_08.parquet")
        .with_columns(
            pl.col("DK_tags")
            .list.filter(~pl.element().str.contains("česk"))
            .list.join(", ")
            .alias("DK_tags_str")
        )
        .fill_null("")
    )
    return (df,)


@app.cell
def _(df):
    df
    return


@app.cell
def _(df):
    df.explode("DK_tags").group_by("DK_tags").len().sort(by="len", descending=True)
    return


@app.cell
def _(SentenceTransformer, df, pl):
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    anotace = df["DK_anotace"].to_list()
    print(len(set(anotace)))
    anotace_embeddings = model.encode(anotace)
    # tagy = df["DK_tags_str"].to_list()
    # tagy_embeddings = model.encode(tagy)

    # Add embeddings to DataFrame
    df_emb = df.with_columns(
        pl.Series(name="embedding_anotace", values=anotace_embeddings.tolist())
    )  # .with_columns(
    # pl.Series(name="embedding_tagy", values=tagy_embeddings.tolist())
    # )
    return anotace_embeddings, df_emb


@app.cell
def _(df_emb, pl):
    df_emb.filter(pl.col("DK_titul") == "Fosilie")
    return


@app.cell
def _(df_emb):
    df_emb.write_parquet("data/databazeknih_embeddings.parquet")
    return


@app.cell
def _(anotace_embeddings, cosine_similarity, df, pl):
    def find_similar_by_name(df, embeddings, title, author, top_n=5):
        # 1. Find the index of the specific book
        # We use a filter to find the row matching both title and author
        match = df.with_row_index().filter(
            (pl.col("DK_titul") == title) & (pl.col("DK_autorstvo") == author)
        )

        if match.is_empty():
            return f"Error: Could not find '{title}' by {author} in the dataset."

        # Extract the original index
        target_idx = match.select("index").item()

        # 2. Perform Similarity Search (Same logic as before)
        target_embedding = embeddings[target_idx].reshape(1, -1)
        similarities = cosine_similarity(target_embedding, embeddings).flatten()

        # 3. Format and return results
        result_df = df.with_columns(
            pl.Series("similarity_score", similarities)
        ).sort("similarity_score", descending=True)

        # Return top_n, skipping the first result (which is the book itself)
        return (
            result_df.head(top_n + 1)
            .tail(top_n)
            .select(["DK_titul", "DK_autorstvo", "similarity_score", "DK_anotace"])
        )


    # --- Example Usage ---
    results = find_similar_by_name(
        df,
        anotace_embeddings,
        title="Šikmý kostel",
        author="Karin Lednická",  # Note: include the comma if it's in your data!
    )

    print(results)
    return (find_similar_by_name,)


@app.cell
def _(os):
    os.makedirs("data/podobnost/",exist_ok=True)
    return


@app.cell
def _(anotace_embeddings, df, find_similar_by_name):
    find_similar_by_name(
        df,
        anotace_embeddings,
        title="Šikmý kostel",
        author="Karin Lednická",
        top_n=5000
    ).write_json("data/podobnost/sikmy_kostel_embeddings.json")
    return


@app.cell
def _(anotace_embeddings, df, find_similar_by_name):
    find_similar_by_name(
        df,
        anotace_embeddings,
        title="Těla",
        author="Klára Vlasáková",
        top_n=5000
    ).write_json("data/podobnost/tela_embeddings.json")
    return


@app.cell
def _(anotace_embeddings, df, find_similar_by_name):
    find_similar_by_name(
        df,
        anotace_embeddings,
        title="Těla",
        author="Klára Vlasáková",
        top_n=5000
    ).write_json("data/podobnost/tela_embeddings.json")
    return


if __name__ == "__main__":
    app.run()
