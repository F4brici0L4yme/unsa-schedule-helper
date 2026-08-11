import polars as pl
df = pl.read_csv("export/data/cleaned_schedule.csv")
print(df.filter(pl.col("curso_sigla").str.starts_with("NEGOCIOS") | pl.col("curso_nombre").str.contains("NEGOCIOS")))
