import requests
from collections import defaultdict
import constants

HEADERS = {"Authorization": f"Basic {constants.API_TOKEN}"}
BASE_URL = "https://ftc-api.firstinspires.org/v2.0"
SEASON_RANGE = range(2019, 2025)
REGION = "USNC"

# Global counter for API calls
api_call_count = 0

def get_json(url):
    global api_call_count
    api_call_count += 1
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch {url} (status {response.status_code})")
        return {}
    return response.json()

def get_events_by_region(season, region):
    url = f"{BASE_URL}/{season}/events"
    data = get_json(url)
    return [
        event["code"]
        for event in data.get("events", [])
        if isinstance(event.get("regionCode"), str)
        and region.lower() in event["regionCode"].lower()
        and event.get("type") in ["2", "4"]  # Qualifier or Championship
    ]

def get_awards_for_team_at_event(season, team_number, event_code):
    url = f"{BASE_URL}/{season}/awards/{team_number}?eventCode={event_code}"
    data = get_json(url)
    return [award.get("name", "") for award in data.get("awards", [])]

def tally_awards_by_team(team_numbers):
    team_award_tally = defaultdict(lambda: {
        "inspire": {"won": 0, "placed": 0},
        "award": {"won": 0, "placed": 0},
        "winning_alliance": 0
    })

    for team in team_numbers:
        print(f"Processing team {team}...")
        for season in SEASON_RANGE:
            print(f"  Season {season}")
            events = get_events_by_region(season, REGION)
            for event_code in events:
                awards = get_awards_for_team_at_event(season, team, event_code)
                for award in awards:
                    if not ("Dean's List" in award or "Alliance" in award or "Top Ranked" in award):
                        with open("awards.py", "a", encoding="utf-8") as f:
                            f.write(f"{team = }, {award = }, {season = }\n")
                        team_award_tally[team]["award"]["placed"] += 1
                        if not ("2nd Place" in award or "3rd Place" in award):
                            team_award_tally[team]["award"]["won"] += 1

                    if award == "Inspire Award":
                        team_award_tally[team]["inspire"]["won"] += 1
                        team_award_tally[team]["inspire"]["placed"] += 1
                    elif award in ["Inspire Award 2nd Place", "Inspire Award 3rd Place"]:
                        team_award_tally[team]["inspire"]["placed"] += 1

                    if "Winning Alliance" in award:
                        team_award_tally[team]["winning_alliance"] += 1

    return team_award_tally

if __name__ == "__main__":
    team_numbers = [731, 5795, 6183, 10195]
    results = tally_awards_by_team(team_numbers)

    print(f"\n=== API Call Summary ===")
    print(f"Total API calls made: {api_call_count}")

    print("\n=== Inspire Award Summary (2019–2024) ===")
    total_won = total_placed = 0
    for team, data in results.items():
        print(f"Team {team}: {data['inspire']['won']} won, {data['inspire']['placed']} placed")
        total_won += data["inspire"]["won"]
        total_placed += data["inspire"]["placed"]
    print(f"\nTOTAL: {total_won} Inspire wins, {total_placed} Inspire placements")

    print("\n=== Winning Alliance Summary (2019–2024) ===")
    total_winning_alliances = 0
    for team, data in results.items():
        print(f"Team {team}: {data['winning_alliance']} Winning Alliance")
        total_winning_alliances += data["winning_alliance"]
    print(f"\nTOTAL: {total_winning_alliances} Competition wins")

    print("\n=== Awards Summary (2019-2024) ===")
    total_awards_won = total_awards_placed = 0
    for team, data in results.items():
        print(f"Team {team}: {data['award']['won']} awards won, {data['award']['placed']} awards placed")
        total_awards_won += data["award"]["won"]
        total_awards_placed += data["award"]["placed"]
    print(f"\nTOTAL: {total_awards_won} Awards won, {total_awards_placed} Awards placed")
