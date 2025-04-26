import httpx
import time
import json
from datetime import datetime, timedelta

def make_request(url):
    try:
        resp = httpx.get(url, timeout=10.0)
        resp.raise_for_status()
        return resp
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {url}: {e}")
        raise
    except httpx.HTTPStatusError as e:
        print(f"Error response {e.response.status_code} while requesting {url}")
        raise

def scrape_choose_chicago_events(base_url):
    all_events = []
    page = 1

    today = datetime.now().date()
    one_week_later = today + timedelta(days=7)

    should_continue = True

    while should_continue:
        full_url = f"{base_url}?per_page=20&page={page}"
        print(f"Fetching {full_url}")
        
        resp = make_request(full_url)
        data = resp.json()

        events = data.get('events', [])
        print(f"Scraped page {page} with {len(events)} events")

        for event in events:
            event_start_date_str = event.get('start_date')
            if not event_start_date_str:
                continue  # Skip if no start date

            # Clean the start date
            event_start_date = clean_start_date(event)
            if not event_start_date:
                continue  # Skip events with invalid or missing dates

            # Only include events starting from today to one week later
            if today <= event_start_date <= one_week_later:
                venue_info = event.get('venue')
                if isinstance(venue_info, dict):
                    venue_name = venue_info.get('venue', 'No venue')
                    venue_address = venue_info.get('address', 'No address')
                else:
                    venue_name = "No venue"
                    venue_address = "No address"

                # Convert event_start_date to string format (YYYY-MM-DD) before adding to list
                all_events.append({
                    "event_name": event.get('title', 'No title'),
                    "date": event_start_date.strftime("%Y-%m-%d"),  # Convert to string
                    "venue": venue_name,
                    "location": venue_address,
                    "url": event.get('url', 'No URL'),
                })

            # If we see an event starting **after** one week later, stop scraping
            if event_start_date > one_week_later:
                print("Reached events beyond one week. Stopping scrape.")
                should_continue = False
                break

        page += 1
        time.sleep(0.5)

    # Save the data in the `data` directory
    with open('data/choose_chicago_events.json', 'w') as f:
        json.dump(all_events, f, indent=2)

    print(f"Scraping finished. {len(all_events)} events saved to data/choose_chicago_events.json.")

def clean_start_date(event):
    """
    Cleans and formats the event start date.
    Returns the date as a datetime.date object or None if the date is invalid.
    """
    event_start_date_str = event.get('start_date')
    if not event_start_date_str:
        return None  # No date found

    try:
        # Convert the date string to a datetime object
        event_start_date = datetime.strptime(event_start_date_str, "%Y-%m-%d %H:%M:%S").date()
        return event_start_date  # Return as a datetime.date object
    except ValueError:
        print(f"Warning: Could not parse date: {event_start_date_str}")
        return None  # Return None if the date format is incorrect


if __name__ == "__main__":
    scrape_choose_chicago_events("https://www.choosechicago.com/wp-json/tribe/events/v1/events")
