# steps-on-strava

This is a tiny utility to help upload all your days steps from a garmin device to Strava as a single Strava activity. I made this because I didn't want to record walks and hikes because my garmin battery wouldn't last that long. Plus I have some walking goals I wanted to track. 

All of the data moving logic lives in `main.py` and `.github/workflows/nightly.yml` contains the orchestration logic. 

## Data movement logic

* Gets your total step count and distance covered for Garmin for the previous day. 
* Calculates the time elapsed (a required strava field) using a speed assumption that can be changed. 
* Uploads it as a single 'walk' activity. 

## Orchestration logic

* A github action triggers the job once a day for the previous day. 
* If no data is found, it just skips the upload. 
* There's an option to manually enter data for a specific day as a custom workflow_dispatch


## Using this repository (locally)

* Fork the repo and clone it. 
* Install dependencies: `uv sync`
* Create a .env file with your credentials. You'd need 5 credential. See the section on credentials below. 
```
GARMIN_EMAIL=you@example.com
GARMIN_PASSWORD=your-garmin-password

STRAVA_CLIENT_ID=12345
STRAVA_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxx
STRAVA_REFRESH_TOKEN=xxxxxxxxxxxxxxxxxxxx
```
* Run locally: uv run `main.py`


## Setting up as a github action

* Once you've got it working locally, all you need to do is to push any changes you've made to your forked version. 
* Go to Actions under your repository and look for the 'Nightly Garmin -> Strava' sync job. Click Run Workflow to test. 


## Credentials

`GARMIN_EMAIL` and `GARMIN_PASSWORD` are fairly straighforward. 

To generate strava credentials there's a few steps.

* Log into your Strava account. 
* Go to https://www.strava.com/settings/api
* Generate a API application. Use whatever name you want. For `Authorization Callback Domain` use `localhost`. For website use `http://localhost`.
* You'll get a `CLIENT_ID` and `CLIENT_SECRET`.
* Now in your browser, open this link. YOu'll need to replace YOUR_CLIENT_ID
```
https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:write
```
* You'll be redirected to something like: `http://localhost/?code=XYZ123`. And the page will not load. That's okay. What we need is the `code`. So copy the code. 
* Exchange the code for a token
```
curl -X POST https://www.strava.com/oauth/token \
  -d client_id=YOUR_CLIENT_ID \
  -d client_secret=YOUR_CLIENT_SECRET \
  -d code=THE_CODE_YOU_COPIED \
  -d grant_type=authorization_code
```
* Copy the refresh token and use that as the `STRAVA_REFRESH_TOKEN`. 




