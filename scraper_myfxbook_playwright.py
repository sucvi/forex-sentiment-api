# scraper_fxstreet_playwright.py
import asyncio
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

async def scrape_fxstreet():
    events = []
    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days=7)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://www.fxstreet.com/economic-calendar", timeout=60000)
        await page.wait_for_selector("#calendar-filters")

        # Otevřít výběr data
        await page.click("#calendar-date-range")

        # Nastavit rozsah od - do
        await page.fill("input[name='calendar-start-date']", seven_days_ago.strftime("%Y-%m-%d"))
        await page.fill("input[name='calendar-end-date']", today.strftime("%Y-%m-%d"))

        await page.click("button:has-text('Apply')")
        await page.wait_for_timeout(3000)

        rows = await page.query_selector_all("tr.calendar-row")

        for row in rows:
            try:
                time = await row.query_selector("td.event-time")
                currency = await row.query_selector("td.event-currency")
                event = await row.query_selector("td.event-name")
                impact = await row.query_selector("td.event-impact .impact-bar")
                actual = await row.query_selector("td.event-actual span")
                forecast = await row.query_selector("td.event-consensus span")
                previous = await row.query_selector("td.event-previous span")

                event_data = {
                    "time": await time.inner_text() if time else "",
                    "currency": await currency.inner_text() if currency else "",
                    "event": await event.inner_text() if event else "",
                    "impact": await impact.get_attribute("title") if impact else "",
                    "actual": await actual.inner_text() if actual else "",
                    "forecast": await forecast.inner_text() if forecast else "",
                    "previous": await previous.inner_text() if previous else "",
                }
                events.append(event_data)
            except Exception as e:
                print("Chyba na radku:", e)

        await browser.close()

    with open("sentiment_data.json", "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

    print(f"Ulozeno {len(events)} udalosti do sentiment_data.json")

if __name__ == "__main__":
    asyncio.run(scrape_fxstreet())
