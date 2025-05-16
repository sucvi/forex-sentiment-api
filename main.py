from fastapi import FastAPI, Query
from scraper import get_forexfactory_events

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Sentiment API is live!"}

@app.get("/sentiment-data")
async def sentiment_data(pair: str = Query(..., min_length=6, max_length=7)):
    base = pair[:3].upper()
    quote = pair[3:].upper()
    calendar = await get_forexfactory_events(base, quote)
    return {
        "pair": f"{base}/{quote}",
        "calendar": calendar
    }