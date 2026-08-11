import polars as pl

df = pl.read_csv("export/data/cleaned_schedule.csv")
# Group by type, room, day, course, group and count how many slots they have
summary = df.group_by(["tipo", "ambiente", "dia", "curso_sigla", "grupo"]).len().sort("len", descending=True)
print(summary.head(20))
