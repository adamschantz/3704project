import requests
import json
import time

BASE_SEARCH_URL = "https://gobblerconnect.vt.edu/api/discovery/search/organizations"
BASE_DETAIL_URL = "https://gobblerconnect.vt.edu/api/discovery/organization/{}"

OUTPUT_FILE = "gobblerconnect_clubs.json"


def fetch_list_page(skip=0, top=50):
    """
    Fetch organizations from Gobblerconnect's organization search API
    """
    params = {
        "orderBy[0]": "UpperName asc",
        "top": top,
        "filter": "",
        "query": "",
        "skip": skip
    }

    response = requests.get(BASE_SEARCH_URL, params=params)
    response.raise_for_status()
    return response.json()


def fetch_club_detail(club_id):
    """
    Fetch club info based on organization id
    """
    url = BASE_DETAIL_URL.format(club_id)
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch details for ID {club_id}")
        return None

    return response.json()


def extract_clean_club_data(detail):
    """
    Converting club info JSON into clean structured records
    """

    if detail is None:
        return None

    return {
        "id": detail.get("id"),
        "name": detail.get("name", "").strip(),
        "shortName": detail.get("shortName"),
        "summary": detail.get("summary"),
        "description_html": detail.get("description"),
        "categories": detail.get("categories", []),
        "status": detail.get("status"),
        "visibility": detail.get("visibility"),
        "email": detail.get("email"),
        "websiteKey": detail.get("websiteKey"),
        "profilePicture": detail.get("profilePicture"),
        "socialMedia": detail.get("socialMedia", {}),

        "startDate": detail.get("startDate"),
        "modifiedOn": detail.get("modifiedOn"),

        "primaryContact": detail.get("primaryContact"),
    }


def scrape_all_clubs():
    print("Starting club scraping...")

    # get total count
    first_page = fetch_list_page(skip=0)
    total_count = first_page.get("@odata.count", 0)
    print(f"Total clubs reported: {total_count}")

    all_ids = []
    skip = 0
    page_size = 50

    # go through all organization ids and get the club info details for each club
    while True:
        page = fetch_list_page(skip=skip, top=page_size)
        values = page.get("value", [])

        if not values:
            break

        ids = [club["Id"] for club in values]
        all_ids.extend(ids)

        print(f"Collected IDs {skip}–{skip+page_size} (total so far: {len(all_ids)})")

        skip += page_size
        if skip >= total_count:
            break

        time.sleep(0.25)  # avoiding rate limiting

    print(f"Finished collecting {len(all_ids)} organization IDs.")

    # calling to get info for all clubs
    club_data = {}
    for idx, club_id in enumerate(all_ids, start=1):
        print(f"Fetching details {idx}/{len(all_ids)} → ID {club_id}")
        detail = fetch_club_detail(club_id)
        clean = extract_clean_club_data(detail)

        if clean:
            club_data[club_id] = clean

        time.sleep(0.1)  # avoiding rate limiting

    # saving all clubs in json file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(club_data, f, indent=4)

    print(f"Saved {len(club_data)} clubs to {OUTPUT_FILE}")


if __name__ == "__main__":
    scrape_all_clubs()
