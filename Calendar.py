from __future__ import print_function
from datetime import datetime, time, date
import os.path
import pytz
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'


def checkOverlap(s1, e1, s2, e2):
    """
    check if two time slots(in datetime format) overlap
    :return true if overlap
    """
    latterStart = max(s1, s2)
    earlierEnd = min(e1, e2)
    return latterStart > earlierEnd


def getCred():
    """
    Get credentials from user's calender
    :return valid service
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service


def getEvents(service, day=None, start=None, end=None):
    """
    Get upcoming events from google Calender
    if no input range, get upcoming ten events
    :return events
    """
    if day is None:
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        # Call the Calendar API
        events_result = service.events().list(calendarId='primary',
                                              timeMin=now,
                                              maxResults=10,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
    else:
        day = date.fromisoformat(day)
        if start and end:
            start = time.fromisoformat(start)
            end = time.fromisoformat(end)
            start =  datetime.combine(day, start).astimezone(pytz.utc)
            end =  datetime.combine(day, end).astimezone(pytz.utc)
        else:
            start =  datetime.combine(day, datetime.min.time()).astimezone(pytz.utc)
            end = datetime.combine(day, datetime.max.time()).astimezone(pytz.utc)


        # Call the Calendar API
        events_result = service.events().list(calendarId='primary',
                                              timeMin=start.isoformat(),
                                              timeMax=end.isoformat(),
                                              singleEvents=True,
                                              orderBy='startTime').execute()

    events = events_result.get('items', [])
    return events


def addEvent(service, day, start, end, eventName):
    """
    add event to the google Calender
    :return html link if successfully add the event
    :return empty string if fail
    """
    events = getEvents(service, day, start, end)

    day = date.fromisoformat(day)
    start = datetime.combine(day, time.fromisoformat(start)).astimezone(pytz.utc)
    end = datetime.combine(day, time.fromisoformat(end)).astimezone(pytz.utc)

    for event in events:
        eventStart = datetime.fromisoformat(event['start'].get('dateTime',
                                            event['start'].get('date')))
        eventEnd = datetime.fromisoformat(event['end'].get('dateTime',
                                          event['end'].get('date')))
        if checkOverlap(start, end, eventStart, eventEnd):
            return "Schedule Overlap!"

    event = {
        'summary': eventName,
        'start': {
            'dateTime': start.isoformat()
        },
        'end': {
            'dateTime': end.isoformat()
        }
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return f'Event created: {event.get("htmlLink")}'


if __name__ == '__main__':
    # test functionalities
    service = getCred()
    # mock event
    eventName = 'Study Numerical Programming'
    day = date.today().strftime("%Y-%m-%d")
    start = '14:00'
    end = '16:00'

    string = addEvent(service, day, start, end, eventName)
    events = getEvents(service, day, start, end)

    for event in events:
        print(f'Event name: {event["summary"]}')
