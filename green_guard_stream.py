import pathway as pw

class SensorSchema(pw.Schema):
    plant: str
    co2: int
    aqi: int
    timestamp: float


# Read streaming JSONLines file
sensor_stream = pw.io.jsonlines.read(
    "sensor_data.jsonl",
    schema=SensorSchema,
    mode="streaming"
)

sensor_stream = sensor_stream.with_columns(
    event_time=pw.this.timestamp
)

windowed = (
    sensor_stream
    .windowby(
        pw.this.event_time,
        pw.temporal.tumbling(duration=10)
    )
    .reduce(
        plant=pw.this.plant,
        avg_co2=pw.reducers.avg(pw.this.co2),
        avg_aqi=pw.reducers.avg(pw.this.aqi),
        max_co2=pw.reducers.max(pw.this.co2),
        max_aqi=pw.reducers.max(pw.this.aqi),
    )
)

SAFE_CO2 = 420
CRITICAL_CO2 = 650
SAFE_AQI = 100
CRITICAL_AQI = 150

windowed = windowed.with_columns(
    overall_risk=pw.if_else(
        (pw.this.max_co2 > CRITICAL_CO2) |
        (pw.this.max_aqi > CRITICAL_AQI),
        "CRITICAL",
        pw.if_else(
            (pw.this.max_co2 > SAFE_CO2) |
            (pw.this.max_aqi > SAFE_AQI),
            "WARNING",
            "SAFE"
        )
    )
)

pw.io.print(windowed)

pw.run()
