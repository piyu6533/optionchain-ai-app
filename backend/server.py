from fastapi import FastAPI, WebSocket
import requests
import asyncio

app = FastAPI()

URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

def fetch_data():

    headers = {"User-Agent": "Mozilla/5.0"}

    s = requests.Session()
    s.get("https://www.nseindia.com", headers=headers)

    data = s.get(URL, headers=headers).json()

    call_oi = 0
    put_oi = 0

    for row in data["records"]["data"]:
        if "CE" in row:
            call_oi += row["CE"]["openInterest"]
        if "PE" in row:
            put_oi += row["PE"]["openInterest"]

    pcr = round(put_oi / call_oi,2) if call_oi else 0

    signal = "NEUTRAL"

    if pcr > 1.2:
        signal = "BULLISH"
    elif pcr < 0.8:
        signal = "BEARISH"

    return {
        "spot": data["records"]["underlyingValue"],
        "pcr": pcr,
        "signal": signal
    }

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    await ws.accept()

    while True:

        data = fetch_data()

        await ws.send_json(data)

        await asyncio.sleep(5)
