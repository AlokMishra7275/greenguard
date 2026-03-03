import pathway as pw

# Schema
class AQISchema(pw.Schema):
    Timestamp: str
    AQI: int
    Category: str
    City: str
    Dominant_Pollutant: str

# Read full CSV (static mode)
table = pw.io.csv.read(
    "aqi_data.csv",
    schema=AQISchema,
    mode="streaming" # ← changed here
)

# LIVE AGGREGATION
ranking = (
    table
    .groupby(table.City)
    .reduce(
        City = pw.this.City,
        avg_aqi = pw.reducers.avg(table.AQI),
        max_aqi = pw.reducers.max(table.AQI),
        count = pw.reducers.count()
    )
)

# Risk index formula
ranking = ranking.with_columns(
    risk_index = ranking.avg_aqi * 0.7 + ranking.max_aqi * 0.3
)

# Write output
pw.io.csv.write(ranking, "city_ranking.csv")

pw.run()
