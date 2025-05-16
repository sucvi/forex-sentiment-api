import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

async def get_forexfactory_events(base: str, quote: str, days: int = 14):
    result = []
    symbols = [base, quote]
    for i in range(days + 1):
        date = datetime.utcnow() - timedelta(days=i)
        url = f"https://www.forexfactory.com/calendar?day={date.strftime('%Y.%m.%d')}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=20.0)
            soup = BeautifulSoup(r.text, "lxml")
            rows = soup.find_all("tr", {"class": "calendar__row"})

            for row in rows:
                currency = row.get("data-symbol")
                if currency not in symbols:
                    continue

                try:
                    time = row.find("td", {"class": "calendar__time"}).text.strip()
                    event = row.find("td", {"class": "calendar__event"}).text.strip()
                    impact_el = row.find("td", {"class": "calendar__impact"})
                    impact = impact_el.find("span")["title"] if impact_el else "None"
                    actual = row.find("td", {"class": "calendar__actual"}).text.strip()
                    forecast = row.find("td", {"class": "calendar__forecast"}).text.strip()

                    result.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "time": time,
                        "currency": currency,
                        "event_name": event,
                        "impact": impact,
                        "actual": actual if actual != '—' else None,
                        "forecast": forecast if forecast != '—' else None
                    })
                except:
                    continue
    return result
