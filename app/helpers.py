from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

import requests
import datetime
import re
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calender_service():
    """Gets Google Calender service
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('/data/token.json'):
        creds = Credentials.from_authorized_user_file('/data/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/data/credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080, bind_addr='0.0.0.0')
        # Save the credentials for the next run
        with open('/data/token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def login(username, password):
    url = 'https://web.eduflexcloud.nl/NLDA/Webmodules/Pages/Login.aspx'
    payload = {
        '__VIEWSTATE': '/wEPDwUKLTM2OTc0NjYzNw9kFgJmD2QWAmYPZBYCAgIPZBYCAgEPZBYCAgEPFgIeC18hSXRlbUNvdW50AgEWAmYPZBYCZg8VAwBCaHR0cHM6Ly93ZWIuZWR1ZmxleGNsb3VkLm5sOjQ0My9OTERBL1dlYm1vZHVsZXMvUGFnZXMvRGVmYXVsdC5hc3B4BEhvbWVkZBNCY0kusbjunVXVb+Ivn6pYqnS4R8oCu4ikuGaHcbes',
        'ctl00$ctl00$ContentBody$ContentBody$txtUser': username,
        'ctl00$ctl00$ContentBody$ContentBody$txtPass': password,
        'ctl00$ctl00$ContentBody$ContentBody$Button1': 'Log+in'
    }
    x = requests.post(url, data=payload, allow_redirects=False)

    return x.cookies


def getAppointments(sessionCookies, classId, start):
    appointmentFinder = re.compile(r"""dxo.AddAppointment\("([0-9]+)", new Date\(([0-9]+,[0-9]+,[0-9]+,[0-9]+,?[0-9]*)\), ([0-9]+), (.*?), "()", "(11111111)", "(Normal)", (0), (0), (0),\({\\'cpDocent\\':\\'(.*?)\\',\\'cpKlas\\':\\'(.*?)\\',\\'cpVak\\':\\'(.*?)\\',\\'cpAttribuut\\':\\'(.*?)\\',\\'cpTekst\\':\\'(.*?)\\',\\'cpKleur\\':\\'(.*?)\\',\\'cpLokaal\\':\\'(.*?)\\',\\'cpKlasType\\':\\'(.*?)\\',\\'cpLinkCode\\':\\'(.*?)\\',\\'cpExtraInfo\\':\\'(.*?)\\'}\)\);\\n""")

    url = 'https://web.eduflexcloud.nl/NLDA/Webmodules/Pages/KlasRooster.aspx'
    payload = {
        '__VIEWSTATE': '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FgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWBgIDDzwrAAQBAA8WAh4PRGF0YVNvdXJjZUJvdW5kZ2RkAgUPPCsABAEADxYCHyFnZGQCBw88KwAEAQAPFgIfIWdkZAIBD2QWAmYPZBYCZg9kFgICAQ9kFgICAQ9kFgJmD2QWAmYPZBYCZg9kFgQCAQ88KwAEAQAPFgIfIWdkZAIDDzwrAAQBAA8WBB8hZx4FVmFsdWUFJERydWsgb3AgRVNDIG9tIGRlIGFjdGllIHRlIGFubnVsZXJlbmRkAgIPPCsABwEGDxYCHxFnDxQrAAIUKwACFgYeCkFjdGlvbk5hbWUFEWNyZWF0ZUFwcG9pbnRtZW50HwEFD05pZXV3ZSBhZnNwcmFhax4LQ29udGV4dE5hbWUFDENlbGxTZWxlY3RlZGQUKwAEFgIfJAUTQXBwb2ludG1lbnRTZWxlY3RlZA9kEBYCZgIBFgIUKwACFgYfIwUPZWRpdEFwcG9pbnRtZW50HwEFCEJld2Vya2VuHw1nZBQrAAIWBh8jBRFkZWxldGVBcHBvaW50bWVudB8BBQtWZXJ3aWpkZXJlbh8NZ2QPFgICAQICFgIFoQFEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLkZBQkVkaXRBcHBvaW50bWVudEFjdGlvbkl0ZW0sIERldkV4cHJlc3MuV2ViLkFTUHhTY2hlZHVsZXIudjE5LjEsIFZlcnNpb249MTkuMS41LjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjg4ZDE3NTRkNzAwZTQ5YQWjAURldkV4cHJlc3MuV2ViLkFTUHhTY2hlZHVsZXIuRkFCRGVsZXRlQXBwb2ludG1lbnRBY3Rpb25JdGVtLCBEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLnYxOS4xLCBWZXJzaW9uPTE5LjEuNS4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI4OGQxNzU0ZDcwMGU0OWFkZA8UKwECAgECAhYCBZ8BRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci5GQUJDcmVhdGVBcHBvaW50bWVudEFjdGlvbiwgRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci52MTkuMSwgVmVyc2lvbj0xOS4xLjUuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iODhkMTc1NGQ3MDBlNDlhBaIBRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci5GQUJFZGl0QXBwb2ludG1lbnRBY3Rpb25Hcm91cCwgRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci52MTkuMSwgVmVyc2lvbj0xOS4xLjUuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iODhkMTc1NGQ3MDBlNDlhZAIGD2QWAgIBDzwrAAkCAA8WAh8FZ2QGPCsAEwEAFgwfB2gfCWYfCGYfBmgfCmgfC2hkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYQBTZjdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUFW2N0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSR2aWV3VmlzaWJsZUludGVydmFsQmxvY2skY3RsMDAkcG9wdXAFVGN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSR2aWV3U2VsZWN0b3JCbG9jayRjdGwwMCRjdGwwNAVUY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJHZpZXdTZWxlY3RvckJsb2NrJGN0bDAwJGN0bDA1BVRjdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUkdmlld1NlbGVjdG9yQmxvY2skY3RsMDAkY3RsMDYFXWN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSRjb250YWluZXJCbG9jayRNb3JlQnV0dG9ucyRUb3BCdXR0b25fMAVgY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJGNvbnRhaW5lckJsb2NrJE1vcmVCdXR0b25zJEJvdHRvbUJ1dHRvbl8wBUljdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUkYXB0TWVudUJsb2NrJFNNQVBUBUtjdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUkdmlld01lbnVCbG9jayRTTVZJRVcFTGN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSRuYXZCdXR0b25zQmxvY2skY3RsMDEFTGN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSRuYXZCdXR0b25zQmxvY2skY3RsMDMFVmN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSRtZXNzYWdlQm94QmxvY2skbWVzc2FnZUJveFBvcHVwBXJjdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUkbWVzc2FnZUJveEJsb2NrJG1lc3NhZ2VCb3hQb3B1cCRjdGwxOCRtZXNzYWdlQm94UG9wdXAkYnRuT2sFdmN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSRtZXNzYWdlQm94QmxvY2skbWVzc2FnZUJveFBvcHVwJGN0bDE4JG1lc3NhZ2VCb3hQb3B1cCRidG5DYW5jZWwFOmN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSREUFAFQmN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXJQb3B1cCRBU1B4UG9wdXBDb250cm9sMRYLMjkKudWXrnugCAbOAR35kgUuqAQLIxMt2IfBTGjn',
        '__CALLBACKID': 'ctl00$ctl00$ContentBody$ContentBody$Rooster$mySchedule',

        'ctl00$ctl00$ContentBody$ContentBody$DropDownList1': classId,
        }

    # Get date of each day in current week.
    dates = [start + datetime.timedelta(days=d) for d in range(7)]

    # Format dates and add to payload
    dates = ','.join(date.strftime("%m/%d/%Y") for date in dates)
    payload['__CALLBACKPARAM'] = f'c0:SETVISDAYS|{dates}'

    # Fetch and find appointments
    x = requests.post(url, cookies=sessionCookies, data = payload)
    appointments = appointmentFinder.findall(x.text)

    return appointments


def formatEvent(appointment):
    summary = appointment[12] if appointment[12] != "" else appointment[14]
    if not summary:
        summary = appointment[13]

    date = appointment[1].split(",")
    try:
        start = datetime.datetime(int(date[0]), int(date[1])+1, int(date[2]), int(date[3]), int(date[4]), tzinfo=ZoneInfo('Europe/Amsterdam'))
    except IndexError:
        start = datetime.datetime(int(date[0]), int(date[1])+1, int(date[2]), int(date[3]), tzinfo=ZoneInfo('Europe/Amsterdam'))
    end = start + datetime.timedelta(milliseconds=int(appointment[2]))

    # Create Google Calender compliant Event JSON
    newEvent = {
        'summary': summary,
        'location': appointment[16],
        'description': f"{appointment[19]}\nDocent: {appointment[10]}\nLokaal: {appointment[16]}\nBeschrijving: {appointment[14]}",
        'start': {
            'dateTime': start.isoformat(),
            'timeZone': 'Europe/Amsterdam',
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': 'Europe/Amsterdam',
        },
    }

    return newEvent

def fetch_klas_mapping(sessionCookies):
   
    url = 'https://web.eduflexcloud.nl/NLDA/Webmodules/Pages/KlasRooster.aspx'
    response = requests.get(url, cookies=sessionCookies)
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the select element by its name
    select_element = soup.find('select', {'name': 'ctl00$ctl00$ContentBody$ContentBody$DropDownList1'})
    
    if not select_element:
        print("Could not find the select element")
        return {}
    
    # Create the mapping
    klas_mapping = {}
    for option in select_element.find_all('option'):
        klas_id = option['value']
        friendly_name = option.get_text()
        klas_mapping[friendly_name] = klas_id
    
    return klas_mapping


def get_or_create_calendar(service, klas_id, friendly_name):
    calendar_list = service.calendarList().list().execute()
    for calendar_list_entry in calendar_list['items']:
        if 'description' in calendar_list_entry and calendar_list_entry['description'] == klas_id:
            return calendar_list_entry['id']
    
    # Create new calendar if not found
    calendar = {
        'summary': friendly_name,
        'timeZone': 'Europe/Amsterdam',
        'description': klas_id
    }

    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar['id']
