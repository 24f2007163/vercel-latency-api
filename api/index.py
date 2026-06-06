# api/index.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "telemetry.json", "r") as f:
    DATA = json.load(f)


class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: int

@app.get("/")
def home():
    return {"hello": "world"}
    
@app.post("/")
def analyze(body: RequestBody):

    result = {}

    for region in body.regions:

        rows = [
            r for r in DATA
            if r["region"] == region
        ]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 4),
            "breaches": sum(
                1
                for x in latencies
                if x > body.threshold_ms
            )
        }

    return result
