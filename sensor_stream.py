import time
import json
import random

plants = [
    "Manufacturing Plant A",
    "Chemical Facility B",
    "Steel Mill C",
    "Refinery D",
    "Cement Plant E"
]

with open("sensor_data.jsonl", "a") as f:
    while True:
        data = {
            "plant": random.choice(plants),
            "co2": random.randint(380, 750),
            "aqi": random.randint(60, 180),
            "timestamp": time.time()
        }

        f.write(json.dumps(data) + "\n")
        f.flush()
        time.sleep(2)
