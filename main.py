import os
import math
import datetime as dt
import requests
from garminconnect import Garmin
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def strava_refresh_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    r = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]

def strava_create_walk(access_token: str, name: str, start_date_local: str, distance_m: float, elapsed_time_s: int, description: str):

    r = requests.post(
        "https://www.strava.com/api/v3/activities",
        headers={"Authorization": f"Bearer {access_token}"},
        data={
            "name": name,
            "type": "Walk",
            "start_date_local": start_date_local,   # ISO8601, local time
            "distance": distance_m,                 # meters
            "description": description,                      # seconds
            "elapsed_time": elapsed_time_s,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def main():
    garmin_email = os.environ["GARMIN_EMAIL"]
    garmin_password = os.environ["GARMIN_PASSWORD"]

    # Yesterday (UTC). If you want London-local, shift to Europe/London explicitly.
    day = (dt.date.today() - dt.timedelta(days=1)).isoformat()

    # Garmin login + steps
    g = Garmin(garmin_email, garmin_password)
    g.login()
    summary = g.get_stats_and_body(day)  # library returns a dict; includes steps in most setups
    
    if summary.get("totalSteps") is None:
        print(f"No steps found for {day}. Skipping.")
        return
    
    steps = int(summary.get("totalSteps"))
    distance_m = int(summary.get("totalDistanceMeters"))


    # Strava token + create activity
    access_token = strava_refresh_token(
        os.environ["STRAVA_CLIENT_ID"],
        os.environ["STRAVA_CLIENT_SECRET"],
        os.environ["STRAVA_REFRESH_TOKEN"],
    )

    # Put it at midday local so it doesn't look like a weird 00:00 walk
    start_date_local = f"{day}T12:00:00"

    speed_mps = 1.3
    elapsed_time_s = max(60, int(distance_m / speed_mps))  # minimum 1 minute

    created = strava_create_walk(
        access_token=access_token,
        name=f"Daily walking distance",
        start_date_local=start_date_local,
        distance_m=distance_m,
        elapsed_time_s=elapsed_time_s,
        description=f"Date: {day}. Distance: {distance_m} meters. Steps: {steps}.",
    )
    print(f"Created Strava activity id={created.get('id')} for {day} ({steps} steps)")

if __name__ == "__main__":
    main()
