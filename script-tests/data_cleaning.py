# imports
import polars as pl

# reading

df = pl.read_csv(
        "courses_2017.csv",
        has_header  = False,
        new_columns = ["year", "semester_num", "asignature_code", "asignature_name"])

# delete title rows
df_filtered = df.filter(
        pl.col("asignature_name").is_not_null()
        & (pl.col("asignature_name").str.strip_chars() != "")
)

headers_to_delete = ["CASI", "ASIGNATURA", "CASI ASIGNATURA"]
df_filtered = df_filtered.filter(
        ~pl.col("asignature_name").is_in(headers_to_delete)
)

# cleaning
years_list = df_filtered["year"]
counter = 0
last_seen_text = None
numbers_list= []

for current_text in years_list:
    if current_text != last_seen_text:
        counter += 1
        last_seen_text = current_text

    numbers_list.append(counter)

df_filtered = df_filtered.with_columns(
        pl.Series("year_num", numbers_list)
)

df_filtered = df_filtered.drop("year")

semester_mapping = {
        "PrimerSemestre": 1,
        "SegundoSemestre": 2,
}

df_filtered = df_filtered.with_columns(
        pl.col("semester_num")
            .str.replace_all(" ", "")
            .replace(semester_mapping)
            .alias("semester_num")
        )


# output
df_filtered = df_filtered.select(["year_num", "semester_num", "asignature_code", "asignature_name"])
df_filtered.write_csv("../export/data/courses_unsa_2017.csv")
