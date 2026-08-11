import polars as pl
df = pl.read_csv("export/data/cleaned_schedule.csv")
pl.Config.set_tbl_rows(100)
summary = df.group_by(["curso_sigla", "curso_nombre"]).len().sort("curso_sigla")
print(summary)
