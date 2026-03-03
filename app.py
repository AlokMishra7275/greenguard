import pathway as pw

# ---------------- 1️⃣ REAL-TIME INPUT ----------------
input_table = pw.io.csv.read(
    "air_data.csv",
    schema=pw.schema_from_types(
        city=str,
        pm25=float,
        temperature=float,
    ),
    mode="streaming",
)

# ---------------- 2️⃣ RISK CALCULATION ----------------
risk_table = input_table.select(
    city=pw.this.city,
    pm25=pw.this.pm25,
    temperature=pw.this.temperature,
    risk_score=pw.this.pm25 * 0.7 + pw.this.temperature * 0.3,
    level=pw.if_else(
        pw.this.pm25 > 300, "SEVERE",
        pw.if_else(
            pw.this.pm25 > 150, "HIGH",
            pw.if_else(
                pw.this.pm25 > 80, "MODERATE",
                "LOW"
            )
        )
    )
)

# ---------------- 3️⃣ ROLLING AVERAGE PER CITY ----------------
rolling_avg = risk_table.groupby(pw.this.city).reduce(
    city=pw.this.city,
    avg_pm25=pw.reducers.avg(pw.this.pm25)
)

# ---------------- 4️⃣ JOIN CURRENT DATA WITH AVERAGE ----------------
enhanced_table = risk_table.join(
    rolling_avg,
    pw.left.city == pw.right.city
).select(
    city=pw.left.city,
    pm25=pw.left.pm25,
    temperature=pw.left.temperature,
    risk_score=pw.left.risk_score,
    level=pw.left.level,
    avg_pm25=pw.right.avg_pm25,
    spike=pw.if_else(
        pw.left.pm25 > pw.right.avg_pm25 * 1.8,
        "SPIKE",
        "NORMAL"
    )
)

# ---------------- 5️⃣ ALERT TABLE ----------------
alert_table = enhanced_table.filter(
    (pw.this.level == "SEVERE") |
    (pw.this.spike == "SPIKE")
)

# ---------------- 6️⃣ CITY SUMMARY ----------------
city_summary = enhanced_table.groupby(pw.this.city).reduce(
    city=pw.this.city,
    avg_pm25=pw.reducers.avg(pw.this.pm25),
    severe_count=pw.reducers.sum(
        pw.if_else(pw.this.level == "SEVERE", 1, 0)
    ),
    spike_count=pw.reducers.sum(
        pw.if_else(pw.this.spike == "SPIKE", 1, 0)
    )
)

# ---------------- 7️⃣ RISK INDEX CALCULATION ----------------
city_ranking = city_summary.with_columns(
    risk_index=(
        pw.this.avg_pm25 * 0.6 +
        pw.this.severe_count * 50 +
        pw.this.spike_count * 80
    )
)

# ---------------- 8️⃣ OUTPUT FILES ----------------
pw.io.csv.write(enhanced_table, "output.csv")
pw.io.csv.write(alert_table, "alerts.csv")
pw.io.csv.write(city_ranking, "city_ranking.csv")

# ---------------- 9️⃣ RUN ENGINE ----------------
pw.run()
