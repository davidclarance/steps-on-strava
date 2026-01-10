import os
import datetime as dt
import requests
from garminconnect import Garmin
from dotenv import load_dotenv

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

def strava_create_walk(
    access_token: str,
    name: str,
    start_date_local: str,
    distance_m: float,
    elapsed_time_s: int,
    description: str,
):
    r = requests.post(
        "https://www.strava.com/api/v3/activities",
        headers={"Authorization": f"Bearer {access_token}"},
        data={
            "name": name,
            "type": "Walk",
            "start_date_local": start_date_local,
            "distance": float(distance_m),
            "elapsed_time": int(elapsed_time_s),
            "description": description,
            # "private": 1,  # optionally uncomment to keep these out of your feed
        },
        timeout=30,
    )
    if r.status_code >= 400:
        print("Strava error:", r.status_code, r.text)
    r.raise_for_status()
    return r.json()

def env_str(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()

def env_int(name: str):
    v = env_str(name)
    return int(v) if v else None

def env_float(name: str):
    v = env_str(name)
    return float(v) if v else None

def env_bool(name: str, default: bool = False) -> bool:
    v = env_str(name, str(default)).lower()
    return v in ("1", "true", "yes", "y", "on")

def main():
    # Manual overrides (optional)
    override_date = env_str("OVERRIDE_DATE")            # YYYY-MM-DD
    override_steps = env_int("OVERRIDE_STEPS")          # integer
    override_distance_m = env_int("OVERRIDE_DISTANCE_M")# integer meters
    override_speed_mps = env_float("OVERRIDE_SPEED_MPS")# e.g. 1.3
    dry_run = env_bool("DRY_RUN", False)

    day = override_date or (dt.date.today() - dt.timedelta(days=1)).isoformat()

    if override_steps is not None and override_distance_m is not None:
        steps = override_steps
        distance_m = override_distance_m
        source = "overrides"
    else:
        garmin_email = os.environ["GARMIN_EMAIL"]
        garmin_password = os.environ["GARMIN_PASSWORD"]

        g = Garmin(garmin_email, garmin_password)
        g.login()
        summary = g.get_stats_and_body(day)

        if summary.get("totalSteps") is None or summary.get("totalDistanceMeters") is None:
            print(f"No Garmin steps/distance found for {day}. Skipping.")
            return

        steps = int(summary.get("totalSteps"))
        distance_m = int(summary.get("totalDistanceMeters"))
        source = "garmin"

    start_date_local = f"{day}T12:00:00"

    speed_mps = override_speed_mps or 1.3
    elapsed_time_s = max(60, int(distance_m / speed_mps))

    name = "Daily walking distance"
    description = f"Date: {day}. Distance: {distance_m} meters. Steps: {steps}. Source: {source}."

    if dry_run:
        print("DRY RUN: would create Strava activity with:")
        print({"name": name, "start_date_local": start_date_local, "distance_m": distance_m, "elapsed_time_s": elapsed_time_s, "description": description})
        return

    access_token = strava_refresh_token(
        os.environ["STRAVA_CLIENT_ID"],
        os.environ["STRAVA_CLIENT_SECRET"],
        os.environ["STRAVA_REFRESH_TOKEN"],
    )

    created = strava_create_walk(
        access_token=access_token,
        name=name,
        start_date_local=start_date_local,
        distance_m=distance_m,
        elapsed_time_s=elapsed_time_s,
        description=description,
    )
    print(f"Created Strava activity id={created.get('id')} for {day} ({steps} steps)")

if __name__ == "__main__":
    main()