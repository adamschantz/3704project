import requests

API_URL = "http://localhost:8000/api/v1/recommend"

def main():
    print("Club Match AI - CLI Version")
    print("Type your interests (example: engineering, robotics, art):")

    interests = input("> ").strip()

    if not interests:
        print("You must enter at least one interest.")
        return

    payload = {"interests": interests}

    print("\nRequesting recommendations...\n")

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error contacting API: {e}")
        return

    data = response.json()

    recs = data.get("recommendations", [])

    if not recs:
        print("No clubs matched your interests.")
        return

    print("Recommended Clubs:")
    for i, club in enumerate(recs, start=1):
        print(f"\n{i}. {club.get('name', 'Unknown Club')}")
        print(f"   Short Name: {club.get('shortName', 'N/A')}")
        print(f"   Summary: {club.get('summary', 'No summary available.')}")


if __name__ == "__main__":
    main()
