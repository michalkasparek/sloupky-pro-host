import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import re

    import altair as alt
    import marimo as mo
    import polars as pl

    from src.kristi_promin import kristi_promin
    from src.me_to_neurazi import me_to_neurazi

    pl.Config.set_tbl_rows(150)
    pl.Config.set_fmt_str_lengths(150)
    pl.Config.set_tbl_width_chars(200)

    alt.themes.register("irozhlas", kristi_promin)
    alt.theme.enable("irozhlas")
    alt.data_transformers.disable_max_rows()
    return alt, me_to_neurazi, mo, pl, re


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Různé výpočty:
    """)


@app.cell
def _(pl):
    lf = (
        pl.scan_parquet(
            "../stenoprotokoly/data/*.parquet",
            hidden_file_prefix=["projevy", "mluvci"],
            missing_columns="insert",
        )
        .with_columns(
            pl.col("mluvci")
            .str.split(" ")
            .list.slice(-2, 2)
            .list.join(" ")
            .alias("jmeno")
        )
        .filter(
            ~pl.col("text").str.contains("majetok rozdelený a ten na rovné čiasti na")
        )
    )
    return (lf,)


@app.cell
def _(lf):
    lf.group_by(["komora", "komora_komplet"]).len().collect().sort(
        by="len", descending=True
    )


@app.cell
def _():
    zajima = ["ps", "fs", "cnr", "ns"]
    return (zajima,)


@app.cell
def _(lf, pl, zajima):
    lf.filter(pl.col("komora").is_in(zajima)).filter(
        pl.col("text").str.contains(r"Kar\w{1,5} Čap[ek]")
    ).collect()


@app.cell
def _(lf, pl, zajima):
    lf.filter(pl.col("komora").is_in(zajima)).filter(
        pl.col("text").str.contains(r"Milan\w{0,5} Kunder")
    ).collect()


@app.cell
def _(lf, pl, zajima):
    lf.filter(pl.col("komora").is_in(zajima)).filter(
        pl.col("text").str.contains(r"(?i)orwell")
    ).collect()


@app.cell
def _(lf, pl, zajima):
    def po_letech_abs(dotaz):
        return (
            lf.filter(pl.col("komora").is_in(zajima))
            .filter(pl.col("text").str.contains(dotaz))
            .group_by(pl.col("datum").dt.year())
            .len()
            .sort(by="datum")
            .collect()
            .join(
                pl.DataFrame({"datum": range(1918, 2026)}, schema={"datum": pl.Int32}),
                how="right",
                on="datum",
            )
            .fill_null(0)
        )


@app.cell
def _(lf, pl, zajima):
    def po_letech(dotaz):
        return (
            lf.filter(pl.col("komora").is_in(zajima))
            .filter(pl.col("text").str.contains(dotaz))
            .group_by(pl.col("datum").dt.year())
            .len()
            .join(
                lf.group_by(pl.col("datum").dt.year()).len(),
                how="right",
                on="datum",
            )
            .sort(by="datum")
            .with_columns((pl.col("len") / pl.col("len_right")).alias("r"))
            .filter(pl.col("datum") >= 1918)
            .collect()
            .fill_null(0)
        )

    return (po_letech,)


@app.cell
def _(po_letech):
    po_letech(r"Václ\w{0,5} Hav[el]")


@app.cell
def _(alt, pl, po_letech):
    def graf(co_hledame):
        frejm = po_letech(co_hledame)
        print(f"n={frejm.select(pl.col('len').sum()).item()}")
        return (
            alt.Chart(frejm, title=co_hledame, height=100, width=900)
            .mark_bar()
            .encode(alt.X("datum:Q"), alt.Y("r:Q"))
        )

    return (graf,)


@app.cell
def _(graf):
    graf("(?i)orwell")


@app.cell
def _(graf):
    graf(r"Farm\w* zvířat")


@app.cell
def _(graf):
    graf(r"romá\w* 1984")


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)F\w* Kafk")


@app.cell
def _(vyzobni):
    vyzobni("(?i)orwell")


@app.cell
def _(vyzobni):
    vyzobni("(?i)orwell").tail(10)


@app.cell
def _(pl, vyzobni):
    vyzobni("(?i)orwell").group_by(pl.col("datum").dt.year()).len().sort(by="datum")


@app.cell
def _(graf):
    graf("(?i)velk.{1,10} bratr")


@app.cell
def _(vyzobni):
    vyzobni("(?i)velk.{1,10} bratr")


@app.cell
def _(vyzobni):
    vyzobni("Velk.{1,10} bratr")


@app.cell
def _(vyzobni):
    vyzobni("Orwell")


@app.cell
def _(vyzobni):
    vyzobni(r"Orwell").group_by("jmeno").len().sort(by="len", descending=True)


@app.cell
def _(vyzobni):
    vyzobni("(?i) válka je mír")


@app.cell
def _(graf):
    graf("(?i)Huxley")


@app.cell
def _(graf):
    graf(r"(?i)Vál\w{2,5} s [mM]lok")


@app.cell
def _(graf):
    graf(r"(?i)Továr\w{2,5} na absolutno")


@app.cell
def _(graf):
    graf(r"RUR")


@app.cell
def _(graf):
    graf("R.U.R.")


@app.cell
def _(graf):
    graf(r"Mar(x|xe|xovi|xův|xem)[^\w]")


@app.cell
def _(vyzobni):
    vyzobni(r"Mar(x|xe|xovi|xův|xem)[^\w]", nove=True)


@app.cell
def _(graf):
    graf("(?i)hokej")


@app.cell
def _(graf):
    graf(r"Kar\w{1,5} Čap[ek]")


@app.cell
def _(graf):
    graf(r"Milan\w{0,5} Kunder")


@app.cell
def _(graf):
    graf(r"Václ\w{0,5} Hav[el]")


@app.cell
def _(graf):
    graf(r"(?i)bibl")


@app.cell
def _(graf):
    graf(r"(?i)v básni")


@app.cell
def _(graf):
    graf(r"(?i)jak se píše v")


@app.cell
def _(lf, pl):
    lf.filter(pl.col("text").str.contains(r"Václ\w{0,5} Hav[el]")).sort(
        by="datum"
    ).drop_nulls(subset="datum").collect()


@app.cell
def _(lf, pl, zajima):
    def cele_projevy(dotaz, n=3):
        for radek in (
            lf.filter(pl.col("komora").is_in(zajima))
            .filter(pl.col("text").str.contains(dotaz))
            .sort(by="datum")
            .head(n)
            .collect()
            .iter_rows(named=True)
        ):
            print(f"{radek['mluvci']} {radek['datum']}")
            print(radek["text"])
            print("***")

    return (cele_projevy,)


@app.cell
def _(cele_projevy):
    cele_projevy(r"Václ\w{0,5} Hav[el]")


@app.cell
def _(cele_projevy):
    cele_projevy(r"Milan\w{0,5} Kunder")


@app.cell
def _(cele_projevy):
    cele_projevy(r"Božen\w{0,5} Němcov")


@app.cell
def _(graf):
    graf(r"Božen\w{0,5} Němcov")


@app.cell
def _(graf):
    graf(r"J[uú]li\w{0,5} Fučík")


@app.cell
def _(graf):
    graf(r"Čtyři dohody")


@app.cell
def _(vyzobni):
    vyzobni(r"Čtyři dohody")


@app.cell
def _(graf):
    graf(r"Měl jsem psa")


@app.cell
def _(graf):
    graf(r"Švejk")


@app.cell
def _(graf):
    graf(r"Dostojev")


@app.cell
def _(graf):
    graf(r"Čechov")


@app.cell
def _(graf):
    graf(r"Tolst")


@app.cell
def _(graf):
    graf(r"Jaros\w{1,5} Haš")


@app.cell
def _(graf):
    graf(r"P")


@app.cell
def _():
    return


@app.cell
def _(graf):
    graf(r"Rowlingov")


@app.cell
def _(vyzobni):
    vyzobni(r"(Fran\w{1,5} Kafk|[Kk]afkovsk)")


@app.cell
def _(graf):
    graf(r"(?i)kafkovsk")


@app.cell
def _(graf):
    graf(r"(?i)haškovsk")


@app.cell
def _(graf):
    graf(r"(?i)k[aá]m[aá]s[ůúu]")


@app.cell
def _(graf):
    graf("Ayn Rand")


@app.cell
def _(graf):
    graf("Nietzch")


@app.cell
def _(graf):
    graf(r"Mein Kampf")


@app.cell
def _(cele_projevy):
    cele_projevy(r"(?i)kafkovsk")


@app.cell
def _(graf):
    graf(r"(?i)kašpár")


@app.cell
def _(graf):
    graf(r"(?i)Fran\w{1,5} Kafk")


@app.cell
def _(graf):
    graf(r"(?i)Jan\w{0,3} Skácel")


@app.cell
def _(graf):
    graf(r"(?i)Jarosl\w{0,5} Seifert")


@app.cell
def _(graf):
    graf(r"(?i)Kar[el]\w{0,5} Kryl")


@app.cell
def _(graf):
    graf(r"(?i)Coelh")


@app.cell
def _(graf):
    graf(r"(?i)Kar[el]\w{0,5} Kryl")


@app.cell
def _(graf):
    graf(r"(?i)sionských mudrc")


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)sionských mudrc")


@app.cell
def _(vyzobni):
    vyzobni(r"Mein Kampf")


@app.cell
def _(alt, graf):
    alt.vconcat(graf(r"Korán"), graf(r"Bibl(e|í|i[^\w])")).resolve_scale(y="shared")


@app.cell
def _(graf):
    graf(r"Däniken")


@app.cell
def _(graf):
    graf(r"Jáchy\w{0,10} Topol")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Obecné fráze
    """)


@app.cell
def _(lf, pl):
    def vyzobni(hledani, nove=False):
        return (
            lf.filter(pl.col("text").str.contains(hledani))
            .with_columns(
                pl.col("text")
                .str.replace_all(hledani, "\u0000")  # sentinel delimiter
                .str.split("\u0000")
                .list.slice(0, 1)
                .list.join(" ")
                .str.strip_chars()
                .str.slice(-30, 30)
                .alias("pred"),
                pl.col("text")
                .str.replace_all(hledani, "\u0000")  # sentinel delimiter
                .str.split("\u0000")
                .list.slice(1, 1)
                .list.join(" ")
                .str.strip_chars()
                .alias("po"),
            )
            .select(pl.col(["mluvci", "datum", "pred", "po", "jmeno"]))
            .sort(by="datum", descending=nove)
            .collect()
        )

    return (vyzobni,)


@app.cell
def _(vyzobni):
    vyzobni(r"román")


@app.cell
def _():
    testy_jmen = [
        "a politolog Milan Znoj v deníku Právo ze dne 14. prosince 2010 v článku nazvaném Zase ten správný obraz, kde píše: Chystaný zákon ani tolik nehodlá pomáhat obětem, jako hodlá vytvářet ten správný obraz o komunistické době a za tímto účelem umožňuje konstruovat protikomunistický odboj. Zákon by tak vytvářel novou podobu let 1948 až 1989. Ne však takovou, jakou skutečně ona léta byla. O výkladu doby minulé by nakonec rozhodoval Ústav pro studium totalitních režimů, Archiv bezpečnostních složek a Ministerstvo obrany na základě interpretace zde předloženého návrhu zákona. Chci zde na tomto místě upozornit, popřípadě vznést dotazy na to, co je vlastně skutečným cílem předloženého návrhu zákona o údajném třetím odboji. Nejde v první řadě o přepisování minulosti a o zkreslení let 1948 až 1989? Není dalším cílem zvýraznit postavení Ústavu pro studium totalitních režimů? Jeho důležitost, podstata a nenahraditelnost v dalším období? Případná nová vláda si totiž po legitimizování tohoto návrhu zákona nebude moci Ústav pro studium totalitních režimů dovolit zrušit, protože by to mohlo být posuzováno jako neúcta k veteránům údajného třetího odboje. Ústav pro studium totalitních režimů společně s Archivem bezpečnostních složek a Ministerstvem obrany tak bude vytvářet nový pohled na minulost. Vznikne tak vlastně arbitr složený ze tří institucí a ten bude určovat správný obraz o letech 1948 až 1989. Není proto divu, že proti návrhu zákona o tzv. protikomunistickém odboji jsou historici, filozofové i mnozí další akademičtí a vědečtí pracovníci. Kromě toho zcela logicky tento návrh zákona rozděluje i veřejnost. V neposlední řadě jsou proti také někteří z historiků samotného Ústavu pro studium totalitních režimů, protože si uvědomují chybu zákona, jehož cílem není uznání lidí, kteří nějakým způsobem trpěli, ale jehož prvotním cílem je v uvozovkách správný výklad dějin, rozumí se v duchu Ústavu pro studium totalitních režimů. Na závěr svého vystoupení chci požádat předkladatele návrhu zákona o údajném třetím odboji, aby stále neutíkali do minulosti a ke kritice režimu před rokem 1989. Všechny tyto spory nás odvádějí od problémů, které trápí naši republiku. Je potřebné, abychom se zaměřili na současnost, na řešení toho, co bolí a zajímá občany v jejich každodenním životě. Myslet na zabezpečení lidí, na to, aby se ne svou vinou dostávali na hranici chudoby. Řešme tedy společně tyto i další problémy a nezabředávejme opakovaně do minulosti, protože minulost již nezměníme, ale změnit můžeme zítřek. Z výše uvedených důvodů navrhuji tento zákon, sněmovní tisk 204, na zamítnutí. Děkuji za pozornost. (Potlesk poslanců KSČM.)",
        "Joseph Paul Overton popsal metodu, jak probíhá manipulace s veřejným míněním v otevřených demokratických společnostech",
        "pana Bělohradského, který říká, že oligarcha dělá všechno ve svůj prospěch. A vlastně Aristoteles říkal, že politici jsou elity národa. A pan Bělohradský v tom rozhovoru říká, že já mám šanci, protože teď dělám všechno pro tento stát a pro lidi, přejít z toho oligarchy na tu elitu, jako jste vy. Tak mi držte palce a snad to dokážu. (Smích v sále, potlesk.)",
    ]
    return (testy_jmen,)


@app.cell
def _(re):
    def jmeno(retezec):
        match = re.search(
            r"\b[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]*+(?:\s+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]*+)*\b",
            retezec,
        )
        return match.group(0) if match else None

    return (jmeno,)


@app.cell
def _(jmeno, testy_jmen):
    jmeno(testy_jmen[0])


@app.cell
def _(jmeno, pl, vyzobni):
    vyzobni(r"(?i)filo[zs]o(f|fa|fem) ").with_columns(
        pl.col("po").map_elements(jmeno, return_dtype=str)
    ).group_by("po").len().sort(by="len", descending=True)


@app.cell
def _(graf):
    graf(r"Plat[óo]n")


@app.cell
def _(graf):
    graf(r"K\w* Marx")


@app.cell
def _(graf):
    graf(r"(?i)filo[zs]o(f|fa|fem) ")


@app.cell
def _():
    return


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)filo[zs]o(f|fa|fem) ")


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)filo[zs]o(f|fa|fem) ").group_by("jmeno").len().sort(
        by="len", descending=True
    )


@app.cell
def _(lf, pl):
    lf.filter(pl.col("jmeno").str.contains("Tomio Okamura")).with_columns(
        pl.col("text").str.len_bytes()
    ).select(pl.col("text")).sum().collect()


@app.cell
def _(lf, pl):
    lf.filter(pl.col("jmeno").str.contains("Ransdorf")).with_columns(
        pl.col("text").str.len_bytes()
    ).select(pl.col("text")).sum().collect()


@app.cell
def _(graf):
    graf(r"(?i)[^\w]v knize")


@app.cell
def _(vyzobni):
    vyzobni(r"(?i) s klasikem")


@app.cell
def _(jmeno, pl, vyzobni):
    vyzobni(r"(?i)spisovate(l|le|lem|li|lka|lky|lkou|lce) ").with_columns(
        pl.col("po").map_elements(jmeno, return_dtype=str)
    ).group_by("po").len().sort(by="len", descending=True)


@app.cell
def _(vyzobni):
    vyzobni(r"Wells")


@app.cell
def _(graf):
    graf(r"H.{1,20}Wells")


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)jak (napsal|napsala|píše)")


@app.cell
def _(vyzobni):
    vyzobni(
        r"(?i)[vz] (knize|knížce|knihy|publikac[ie]{0,1}|románu{0,1}|povíd[kc]|manifestu{0,1})"
    )


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)[vz] (knize|knížce|knihy|románu{0,1}|povíd[kc])").group_by(
        "jmeno"
    ).len().sort(by="len", descending=True)


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)verš").group_by("jmeno").len().sort(by="len", descending=True)


@app.cell
def _():
    return


@app.cell
def _(vyzobni):
    vyzobni(r"na blogu")


@app.cell
def _(vyzobni):
    vyzobni(r"(?i) ocituji")


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)leporel")


@app.cell
def _(graf):
    graf(r"(?i) ocituji")


@app.cell
def _(graf):
    graf("(i?)(slovy klasika|řečeno s klasikem|jak říká klasik|jak praví klasik)")


@app.cell
def _(graf):
    graf("(i?)(slovy básníka)")


@app.cell
def _(graf):
    graf(r" verše ")


@app.cell
def _(vyzobni):
    vyzobni("verše")


@app.cell
def _(graf):
    graf(r"(?i)absurdn.{0,10} drama")


@app.cell
def _(graf):
    graf(r"(?i)červen.{0,10} knihovn")


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Antika
    """)


@app.cell
def _(graf):
    graf(r"Odys{1,2}e")


@app.cell
def _(vyzobni):
    vyzobni(r"Odys{1,2}e")


@app.cell
def _(graf):
    graf(r"Sisyf")


@app.cell
def _(graf):
    graf(r"Herkul")


@app.cell
def _(graf):
    graf(r"(?i)prométh")


@app.cell
def _(graf):
    graf(r"(?i)penelop")


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)penelop")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fantasy a scifi
    """)


@app.cell
def _(graf):
    graf(r"Harry\w{0,5} Potter")


@app.cell
def _(graf):
    graf(r"Voldemort")


@app.cell
def _():
    return


@app.cell
def _(graf):
    graf(r"Rowling")


@app.cell
def _(graf):
    graf(r"Pán\w{0,5} prsten")


@app.cell
def _(vyzobni):
    vyzobni(r"Pán\w{0,5} prsten")


@app.cell
def _(vyzobni):
    vyzobni("Glum")


@app.cell
def _(graf):
    graf("Tolkien")


@app.cell
def _(graf):
    graf(r"Pratchet")


@app.cell
def _(graf):
    graf(r"Stanis\w{2,6} Lem")


@app.cell
def _(graf):
    graf(r"(?i)společenstv\w{1,5} prsten")


@app.cell
def _(graf):
    graf(r"Frodo")


@app.cell
def _(graf):
    graf(r"apitán\w{0,4} Nem")


@app.cell
def _(vyzobni):
    vyzobni(r"apitán\w{0,4} Nem")


@app.cell
def _(graf):
    graf(r"verneov")


@app.cell
def _(graf):
    graf(r"verneov")


@app.cell
def _(graf):
    graf(r"Vern[ea][^\w]")


@app.cell
def _(graf):
    graf(r"Star Trek")


@app.cell
def _(graf):
    graf(r"Solaris")


@app.cell
def _(vyzobni):
    vyzobni(r"Solaris")


@app.cell
def _(graf):
    graf(r"kolem světa za")


@app.cell
def _(graf):
    graf(r"mil pod mořem")


@app.cell
def _(vyzobni):
    vyzobni("mil pod mořem")


@app.cell
def _(graf):
    graf("Saruman")


@app.cell
def _(graf):
    graf("Darth Vader")


@app.cell
def _(graf):
    graf(r"(?i)hvězd\w{1,2} smrt")


@app.cell
def _(graf):
    graf(r"(?i)stopař\w{1,5} průvodce")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Dětská literatura
    """)


@app.cell
def _(graf):
    graf(r"(?i)brouk\w{0,3} pytl")


@app.cell
def _(graf):
    graf(r"(?i)ferd\w{1,5} mraven")


@app.cell
def _(graf):
    graf(r"(?i)baron\w{0,5} prášil")


@app.cell
def _(graf):
    graf("(?i)stolečku,{0,1} prostři")


@app.cell
def _(graf):
    graf(r"Rychl.{0,10} šíp")


@app.cell
def _(graf):
    graf(r"[Ff]oglar")


@app.cell
def _():
    return


@app.cell
def _(graf):
    graf(r"pejs\w{0,5} [as] kočičk")


@app.cell
def _(graf):
    graf(r"[Oo]tesán[ek]")


@app.cell
def _(graf):
    graf(r"(?i)císař.{1,10} nové šat")


@app.cell
def _(graf):
    graf(r"(?i)kocourkov")


@app.cell
def _(graf):
    graf(r"(?i)bratrstv.{1,10} kočičí")


@app.cell
def _(graf):
    graf(r"Alen.{0,13} [řŘ]íši div")


@app.cell
def _(vyzobni):
    vyzobni(r"Alen.{0,13} [řŘ]íši div")


@app.cell
def _(graf):
    graf("Vinnet")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Detektivky
    """)


@app.cell
def _(graf):
    graf(r"Sherl.{0,10} Holmes")


@app.cell
def _(graf):
    graf(r"Poirot")


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Klasika
    """)


@app.cell
def _(graf):
    graf(r"Korán")


@app.cell
def _(graf):
    graf(r"Bibl")


@app.cell
def _(graf):
    graf(r"Ayn Rand")


@app.cell
def _(graf):
    graf(r"Cesta do otroctví")


@app.cell
def _(graf):
    graf(r"(Exupér|Mal\w* princ)")


@app.cell
def _(graf):
    graf(r"Ferdi\w* Perout")


@app.cell
def _(graf):
    graf(r"(?i)pandoř\w* skří")


@app.cell
def _(graf):
    graf(r"(?i)tr[oó]jsk\w* k(ůň|oně|oni)")


@app.cell
def _(graf):
    graf(r"Hlav\w* (XXII|22)")


@app.cell
def _(graf):
    graf(r"(?i)don quijo")


@app.cell
def _(graf):
    graf(r"(?i)boj.{0,10} s větrnými ml")


@app.cell
def _(graf):
    graf(r"Jekyll.{0,13} Hyde")


@app.cell
def _(graf):
    graf(r"Souostroví Gulag")


@app.cell
def _(graf):
    graf(r"Solženicin")


@app.cell
def _(graf):
    graf(r"Peroutk")


@app.cell
def _(graf):
    graf(r"vlevo dole")


@app.cell
def _(graf):
    graf("Machiavelli")


@app.cell
def _(graf):
    graf("Faust")


@app.cell
def _(graf):
    graf("Mefisto")


@app.cell
def _(graf):
    graf("Saturnin")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Současná
    """)


@app.cell
def _(graf):
    graf(r"Vlasti\w* Vondrušk")


@app.cell
def _(vyzobni):
    vyzobni(r"Vlasti\w* Vondrušk")


@app.cell
def _(graf):
    graf(r"Lucem\w* epope")


@app.cell
def _(graf):
    graf(r"Steph\w* King")


@app.cell
def _(graf):
    graf(r"Jarosl\w* Rudiš")


@app.cell
def _(vyzobni):
    vyzobni(r"Jarosl\w* Rudiš")


@app.cell
def _(graf):
    graf(r"Alen\w* Mornštajn")


@app.cell
def _(graf):
    graf(r"Kateřin\w* Tučkov")


@app.cell
def _(graf):
    graf("Vyhnání Gerty")


@app.cell
def _(vyzobni):
    vyzobni("Vyhnání Gerty")


@app.cell
def _(graf):
    graf(r"Denemark")


@app.cell
def _(graf):
    graf(r"Biler")


@app.cell
def _(graf):
    graf(r"Micha\w* Kašp")


@app.cell
def _(graf):
    graf(r"Jách\w* Topol")


@app.cell
def _(vyzobni):
    vyzobni(r"Jách\w* Topol")


@app.cell
def _(graf):
    graf(r"Simon\w* Mony")


@app.cell
def _(graf):
    graf(r"Micha\w* Vieweg")


@app.cell
def _(vyzobni):
    vyzobni(r"Micha\w* Vieweg")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cimrmani
    """)


@app.cell
def _(graf):
    graf(r"Cimrma")


@app.cell
def _(graf):
    graf(r"(?i), to nemohu říct")


@app.cell
def _(graf):
    graf(r"(?i)není to málo,{0,1} anton")


@app.cell
def _():
    return


@app.cell
def _(graf):
    graf(r"(?i)mu tam lidi")


@app.cell
def _(vyzobni):
    vyzobni(r"mu tam lidi")


@app.cell
def _(vyzobni):
    vyzobni(r"by chtěl žít každý")


@app.cell
def _(vyzobni):
    vyzobni(r"zvrácené rozkazy")


@app.cell
def _(vyzobni):
    vyzobni(r"(?i)náčelníku")


@app.cell
def _(vyzobni):
    vyzobni(r"Cimrman")


@app.cell
def _(pl, vyzobni):
    vyzobni(r"Cimrman").group_by(pl.col("datum").dt.year()).len().sort(by="datum")


@app.cell
def _(vyzobni):
    vyzobni(r"Cimrman").group_by("jmeno").len().sort(by="len", descending=True)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Graf
    """)


@app.cell
def _():
    vyber = {
        "George Orwell, orwellovský": r"(?i)orwell",
        "Cimrman": r"Cimrman",
        "„v knize“": r"(?i)[^\w]v knize",
        "„jak praví/říká/atp. klasik“": r"(i?)(slovy klasika|řečeno s klasikem|jak říká klasik|jak praví klasik)",
        "Harry Potter": r"Harry\w{0,5} Potter",
        "Mein Kampf": r"Mein Kampf",
        "Božena Němcová": r"Božen\w{0,5} Němcov",
        "Niccolò Machiavelli": r"(?i)machiavelli",
        "Alenka v Říši divů": r"Alen.{0,13} [řŘ]íši div",
        "Bratrstvo kočičí pracky": r"(?i)bratrstv.{1,10} kočičí",
        "Kocourkov": r"(?i)kocourkov",
        "Pejsek a kočička": r"pejs\w{0,5} [as] kočičk",
        "Rychlé šípy": r"Rychl.{0,10} šíp",
        "Švejk": r"Švejk",
        "Julius Fučík": r"J[uú]li\w{0,5} Fučík",
        "Karl Marx": r"K\w* Marx",
        "Pandořina skříňka": r"(?i)pandoř\w* skří",
        "Karel Čapek": r"Kar\w{1,5} Čap[ek]",
        "Korán": "Korán",
        "Bible": "Bibl",
        "Franz Kafka, kafkovský": r"(Fran\w{1,5} Kafk|[Kk]afkovsk)",
    }
    return (vyber,)


@app.cell
def _(pl, vyber, vyzobni):
    do_grafu = pl.DataFrame()

    for popisek, regex in vyber.items():
        vyzobnute = vyzobni(regex)
        pocet = len(vyzobnute)

        do_grafu = pl.concat(
            [
                do_grafu,
                vyzobnute.group_by(pl.col("datum").dt.year().alias("rok"))
                .agg(pl.col("jmeno").unique().len().alias("poslanců"))
                .filter(pl.col("rok") >= 1918)
                .sort(by="rok")
                .with_columns(pl.lit(popisek).alias("co"))
                .with_columns(pl.lit(pocet).alias("len"))
                .with_columns(
                    (
                        pl.col("co")
                        + pl.lit(" (")
                        + pl.col("len").cast(str)
                        + pl.lit("×)")
                    ).alias("co_n")
                ),
            ]
        )

    razeni = (
        do_grafu.group_by("co")
        .agg(pl.col("rok").min())
        .sort(by="rok")
        .select(pl.col("co"))
        .to_series()
        .to_list()
    )
    return do_grafu, razeni


@app.cell
def _(do_grafu):
    do_grafu


@app.cell
def _(alt, do_grafu, pl, razeni):
    alt.Chart(
        do_grafu.filter(pl.col("rok").is_between(1918, 2026)), width=800, height=50
    ).mark_bar().encode(
        alt.X("rok:Q", scale=alt.Scale(domain=[1918, 2026])),
        alt.Y("poslanců:Q"),
        alt.Row("co:N", sort=razeni),  # sort=vyber.keys())
    )


@app.cell
def _(alt, do_grafu, pl, razeni):
    alt.Chart(
        do_grafu.filter(pl.col("rok").is_between(1918, 2026)),
        width=600,
        title=alt.Title(
            "Literární reference v projevech poslanců a poslankyň",
            subtitle="Velikost kolečka odpovídá počtu jednotlivých mluvčích, kteří v daném roce dropli referenci. Největší odpovídá dvanácti.",
        ),
    ).mark_circle().encode(
        alt.X("rok:Q", scale=alt.Scale(domain=[1918, 2026])),
        alt.Size("poslanců:Q"),
        alt.Y("co:N", sort=razeni),  # sort=vyber.keys())
    )


@app.cell
def _(alt, do_grafu, pl, razeni):
    # 1. Update the points chart with axis formatting and grid lines
    points = (
        alt.Chart(
            do_grafu.filter(pl.col("rok").is_between(1918, 2026)),
            width=500,
            title=alt.Title(
                "Literární reference v projevech poslanců a poslankyň",
                subtitle=[
                    f"Velikost kolečka odpovídá počtu jednotlivých mluvčích, kteří použili danou referenci, v rozsahu od {do_grafu.select(pl.col('poslanců')).min().item()} do {do_grafu.select(pl.col('poslanců')).max().item()}.",
                    "Šlo o reference v různých pádech, tedy např. „v Bibli“, ovšem ne reference formulované jinak; do Bible se tedy nepočítá „podle Nového Zákona“.",
                    "Šedě je podbarvené období 2. světové války, kdy české zákonodárné sbory nezasedaly, červeně období vlády KSČ.",
                ],
            ),
        )
        .mark_circle()
        .encode(
            alt.X(
                "rok:Q",
                scale=alt.Scale(domain=[1918, 2026]),
                axis=alt.Axis(
                    format="d"
                ),  # "d" forces standard digit formatting (removes the comma),
                title=None,
            ),
            alt.Size("poslanců:Q", legend=None),
            alt.Y(
                "co:N",
                sort=razeni,
                # Enables the grid line stemming from the vertical axis categories
                axis=alt.Axis(grid=True, gridColor="lightgray", gridWidth=0.5),
                title=None,
            ),
        )
    )

    # 2. Keep the rectangle exactly as you had it
    rect1 = (
        alt.Chart(alt.Data(values=[{"start": 1948, "end": 1989}]))
        .mark_rect(color="red", opacity=0.2)
        .encode(
            x=alt.X("start:Q", scale=alt.Scale(domain=[1918, 2026]), title=None),
            x2="end:Q",
        )
    )

    rect2 = (
        alt.Chart(alt.Data(values=[{"start": 1939, "end": 1944}]))
        .mark_rect(color="gray", opacity=0.3)
        .encode(
            x=alt.X("start:Q", scale=alt.Scale(domain=[1918, 2026]), title=None),
            x2="end:Q",
        )
    )

    # 3. Layer the charts
    final_chart = (rect1 + rect2 + points).configure_view(strokeWidth=0)

    final_chart
    return (final_chart,)


@app.cell
def _(final_chart, me_to_neurazi):
    me_to_neurazi(
        final_chart, kredity="Zdroj dat: psp.cz", soubor="08_poslanecke_projevy"
    )


if __name__ == "__main__":
    app.run()
