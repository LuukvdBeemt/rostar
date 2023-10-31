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
        '__VIEWSTATE': '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MzcxBDUzNzYENTM3NQQ1Mzc0BDUzNzMENTQwMwQ1NDA0BDU0MDIENTM5NwQ1Mzk4BDUzOTQENTY2MgQ1NDAxBDUzOTkENTM5NQQ1Mzk2BDUzOTMENTM5MgQ1NTIxBDU1MjIENTgxMQQ1NjIxBDU2MjIENTYyMAQ1NjE5BDU2MTgENTQ3MAQ1NjI1BDU2MjQENTYyMwQ1NDAwBDU2MTEENTQ2OAQ1NjE1BDU2MDkENTYxMAQ1NjE0BDU2MTcENTYxNgQ1NjEyBDU2MTMENTYwOAQ1NjA3BDU1MjYENTY2NAQ1NzI3BDU3MjgENTc4OAQ1Nzg3BDU3OTIENTc5MQQ1NzkwBDU3ODkENTUyNQQ1NjY1BDU3OTcENTc5OAQ1NzkzBDU3OTYENTc5NQQ1Nzk0BDU2NjMENTUyMwQ1NTI0BDU3ODEENTc4MgQ1Nzc3BDU3NzgENTc4MAQ1Nzg2BDU3ODUENTc4NAQ1NzgzBDU3NzkENTc3NgQ1Nzc1BDU3NjAENTgwNgQ1ODQ4BDU3NjEENTgwNwQ1ODQ5BDU3NTcENTgwNQQ1NzU0BDU4MTgENTc1NQQ1ODU5BDU4NTcENTg1NgQ1ODU1BDU0ODkENTY3MAQ1ODMzBDUyNDQENTU1MgQ1NzM1BDU4NzUENTQ5MAQ1NjY5BDU4MzQENTI0NQQ1NTUzBDU3MzYENTg3NgQ1NDkxBDU2NzEENTgzNQQ1MjQ2BDU1NTQENTczNwQ1ODc3BDUyNDcENTU1NgQ1NzM4BDU4NzgENTQ5MgQ1NjY2BDU4MzYENTI0OAQ1NTU3BDU3MzkENTg3OQQ1NDkzBDU2NjcENTgzNwQ1NDk0BDU2NjgENTgzOAQ1ODAwBDUyMzcENTU0NQQ1NTQ2BDUyMzgENTU0MwQ1NTQ0BDU3MjIENTcyMwQ1NzI0BDU3MjUENTg2MQQ1ODYyBDU4NjMENTg2NAQ1MzMzBDUzMzQENTMzNQQ1MzM2BDU1OTgENTU5NQQ1MzM3BDUzMzgENTMzOQQ1MzQwBDU1OTkENTU5NgQ1MzQxBDUzNDIENTM0MwQ1MzQ0BDU2MDAENTU5NwQ1MTY5BDU1NzgENTc0MAQ1NTc5BDU1ODAENTU4MQQ1NTgyBDU3NDEENTU4MwQ1NzQzBDU3NDQENTU4NAQ1NTg1BDU3NDIENTc0NQQ1NzQ2BDU3NDcENTU1NQQ1Njk2BDU2OTcENTcwOAQ1NzA5BDU3MTAENTgxMAQ1NzE3BDU1NzUENTcxOQQ1NTc2BDU3MTgENTU3NwQ0NzE1BDU3MjAEMTMwNQQ1NzYzBDE0MzIENDA0OQQ0MDA0BDU1ODkEMzk0MwQxNDM1BDQzODgENTE2NwQ0MTYzBDU4NTAENTE3NQQ1MTY1BDUxNjYENDcwNwQ0Mjc4BDE0NTUENTE5NQQ1MDMxBDM4OTEENTI3MgQ1Mzc3BDU3OTkENTQxOQQ1NDg4BDU0ODcENDk3NQQ1ODY1BDQ5NzQENTQ4MwQzODkwBDQxNDUENDA1MgQzNDEzBDE0NjcEMTUzNgQxNDY4BDE1MzUEMTU0NAQxNDY5BDE0NTQENDk4MQQ1NzczBDQ2MDAENDU5OQQzOTE5BDM5MDMENTEwNgQ0NjI1BDQ1MTMEMzQxNAQ0NTMyBDQ3OTgENDUxNAQ1MTY4BDU3MDUENTg2MAQ1MjI3BDU1MzYENTcxMQQ1MjI4BDU1MzcENTcxMgQ1MjI5BDU1MzgENTcxMwQ1MjMwBDU1MzkENTcxNAQ1MjMxBDU1NDAENTcxNQQ1MjMyBDU1NDEENTcxNgQ1MzMyBDUzMzEENTMzMAQ1NTMyBDU1NDIENTY5MgQ1NjQ3BDU4MDgENTU5NAQ1NTkxBDU1OTIENTU5MwQ1NzIxBDU3NzQENTQ0MgQ1NDQzBDU0NDQENTQ0NQQ1NDMwBDU0MzEENTQzMgQ1NDMzBDU0MzQENTQzNQQ1NjI2BDU2MjcENTYyOAQ1NjI5BDU2MzAENTQzNgQ1NDM3BDU0MzgENTQzOQQ1NDQwBDU0NDEENTQ3MwQ1NTA4BDU2MzEENTUxMgQ1NTEzBDU1MTcENTUxOAQ1NTE1BDU1MTkENTUxNgQ0NjYyBDQ5MTcENTE0NAQ1NDU4BDU0NTkENTY1NgQ1NjU3BDU3NTYENTg2OAQ1ODY5BDUxOTgENTUxMAQ1MTk5BDU1MTEENTQ5NQQ1ODQxBDU0OTYENTY3MgQ1NDgwBDU2ODkENTQ3OQQ1NDgxBDU4NDMENTg0MgQ1NDk3BDU2ODIENTg0MAQ1ODM5BDU0OTgENTY3MwQ1NjkxBDU2NzQENTQ4MgQ1NDk5BDU2NzUENTUwMAQ1Njc2BDU1MDEENTY5MAQ0MzkwBDQ2ODQENTEwOAQ1NDYyBDU0NjEENTQ2MwQ1NjYwBDU2NTkENTU5MAQ1ODE3BDU4MTYENTg4MAQ1NjM2BDU2MzUENTgwNAQ1ODI3BDU4MjgENTgyOQQ1ODMwBDU4MzEENTU2MAQ1NTYxBDU1NjIENTU3MgQ1NTY0BDU1NjUENTU2MwQ1NTczBDU1NjYENTU2NwQ1NTY4BDU1NzQENTU2OQQ1NTcwBDU1NzEENTUyOQQ1NzAxBDU3MDYENTcwNwQ1MzUyBDU1NTkENTYwMQQ1NzQ4BDUzNTMENTc0OQQ1MzU0BDU1NTgENTc1MAQ1NDE2BDU3NTEENTc1MgQ1NzUzBDU0MTcENTY5MwQ1NjMyBDU2OTQENTYzMwQ1NjM0BDU0MTgENTcwMgQ1NzAzBDU3MDQENTM2OQQ1NDIwBDU0MjEENTUyMAQ1NDA4BDU3MjYENTY0MQQ1NjQyBDU2NDMENTY0MAQ1NjQ1BDU2NDQENTYzOQQ1NjM3BDU2MzgENDM5MQQ0NjYxBDQ5MTUENTE0MwQ1NDU3BDU0NjAENTY1NQQ1NjU4BDU4NjYENTg2NwQ1NjQ4BDU2NDkENTYwMgQ0ODg4BDU2MDMENTc2NwQ1NzY4BDU3NzAENTc3MQQ1NzcyBDU4NDQENTY3OAQ1NDg1BDU4NDUENTQ4NgQ1Njc5BDU1MDYENTY4MAQ1ODQ2BDU1MDcENTY4MQQ1ODQ3BDQzODkENDM5MwQ0NjU2BDQ2NTcENDkwOQQ0OTEwBDUxMzMENTEzNAQ1MTM1BDUxMzYENTIwNAQ1NTMxBDU0NTIENTQ1MwQ1NDU0BDU0NTUENTQ1NgQ1NjYxBDU2NTAENTY1MQQ1NjUyBDU2NTQENTY1MwQ1ODEyBDU4MTMENTgxNAQ1ODE1BDU4NzQUKwPCBGdnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnFgFmZAIFD2QWBAIBD2QWAmYPZBYCZg9kFgJmD2QWAmYPPCsABQEEFCsBAGQCAw88KwAKAgQUKwACPCsACQEBFCsAAmRkZAUUKwACZGQWBGYPZBYEZg9kFgJmD2QWAmYPZBYCZg9kFgICAQ9kFgJmD2QWAmYPZBYCZg9kFgICAQ88KwAJAQAPFgIeDl8hVXNlVmlld1N0YXRlZ2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYCAgEPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmDzwrAAUBBBQrAQBkAgQPZBYCZg9kFgYCAw9kFgJmD2QWAmYPPCsACQIADxYCHwJnZAYPZBAWBmYCAQICAgMCBAIFFgY8KwAMAQAWBh8BBQRPcGVuHgROYW1lBQ9PcGVuQXBwb2ludG1lbnQeDlJ1bnRpbWVDcmVhdGVkZzwrAAwBABYIHwEFC0VkaXQgU2VyaWVzHwMFCkVkaXRTZXJpZXMfBGceCkJlZ2luR3JvdXBnPCsADAEAFggfAQUVUmVzdG9yZSBEZWZhdWx0IFN0YXRlHwMFEVJlc3RvcmVPY2N1cnJlbmNlHwRnHwVnPCsADAIAFgwfAQUMU2hvdyBUaW1lIEFzHwMFDVN0YXR1c1N1Yk1lbnUeC05hdmlnYXRlVXJsZR4GVGFyZ2V0ZR8FZx8EZwEPFgIeCklzU2F2ZWRBbGxnDxQrAAUUKwAMFhAfAwUPU3RhdHVz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LkFTUHhTY2hlZHVsZXIuQVNQeFNjaGVkdWxlck1lbnVJdGVtLCBEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLnYxOS4xLCBWZXJzaW9uPTE5LjEuNS4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI4OGQxNzU0ZDcwMGU0OWE8KwAMAgAWCB8BBQZEZWxldGUfAwURRGVsZXRlQXBwb2ludG1lbnQfBGcfBWcCFCsAAmQUKwABFgIeCENzc0NsYXNzBSFkeFNjaGVkdWxlcl9NZW51X0RlbGV0ZV9PZmZpY2UzNjUPFgYCAQIBAgFmZgIBFgEFmgFEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLkFTUHhTY2hlZHVsZXJNZW51SXRlbSwgRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci52MTkuMSwgVmVyc2lvbj0xOS4xLjUuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iODhkMTc1NGQ3MDBlNDlhZAIED2QWAmYPZBYCZg88KwAJAgAPFgIfAmdkBg9kEBYJZgIBAgICAwIEAgUCBgIHAggWCTwrAAwBABYIHwEFC0dvIHRvIFRvZGF5HwMFCUdvdG9Ub2RheR8EZx8FZzwrAAwCABYGHwEFDUdvIHRvIERhdGUuLi4fAwUIR290b0RhdGUfBGcCFCsAAmQUKwABFgIfFwUjZHhTY2hlZHVsZXJfTWVudV9Hb1RvRGF0ZV9PZmZpY2UzNjU8KwAMAgAWDB8BBQ5DaGFuZ2UgVmlldyBUbx8DBQ5Td2l0Y2hWaWV3TWVudR8GZR8HZR8FZx8EZwEPFgIfCGcPFCsAAxQrAAwWEB8DBQ9Td2l0Y2hUb0RheVZpZXcfBmUfCWgfB2UfAQUIRGFnIFZpZXcfCmUfCwUCVlcfBGcPFgIfCGdkZGRkZGRkZDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhw8KwAOAQAWFh8MCysEAB8NHB8OHB8PZR8QHB8RCysFAB8SCysGAh8THB8UHB8VAv////8PHxYcZBQrAAwWEB8DBRRTd2l0Y2hUb1dvcmtXZWVrVmlldx8GZR8JaB8HZR8BBQ5XZXJrIFdl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IGRlIGFjdGllIHRlIGFubnVsZXJlbh8YZ2RkAgIPPCsABwEGDxYCHwhnDxQrAAIUKwACFgYeCkFjdGlvbk5hbWUFEWNyZWF0ZUFwcG9pbnRtZW50HwEFD05pZXV3ZSBhZnNwcmFhax4LQ29udGV4dE5hbWUFDENlbGxTZWxlY3RlZGQUKwAEFgIfIAUTQXBwb2ludG1lbnRTZWxlY3RlZA9kEBYCZgIBFgIUKwACFgYfHwUPZWRpdEFwcG9pbnRtZW50HwEFCEJld2Vya2VuHwRnZBQrAAIWBh8fBRFkZWxldGVBcHBvaW50bWVudB8BBQtWZXJ3aWpkZXJlbh8EZ2QPFgICAQICFgIFoQFEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLkZBQkVkaXRBcHBvaW50bWVudEFjdGlvbkl0ZW0sIERldkV4cHJlc3MuV2ViLkFTUHhTY2hlZHVsZXIudjE5LjEsIFZlcnNpb249MTkuMS41LjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjg4ZDE3NTRkNzAwZTQ5YQWjAURldkV4cHJlc3MuV2ViLkFTUHhTY2hlZHVsZXIuRkFCRGVsZXRlQXBwb2ludG1lbnRBY3Rpb25JdGVtLCBEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLnYxOS4xLCBWZXJzaW9uPTE5LjEuNS4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI4OGQxNzU0ZDcwMGU0OWFkZA8UKwECAgECAhYCBZ8BRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci5GQUJDcmVhdGVBcHBvaW50bWVudEFjdGlvbiwgRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci52MTkuMSwgVmVyc2lvbj0xOS4xLjUuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iODhkMTc1NGQ3MDBlNDlhBaIBRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci5GQUJFZGl0QXBwb2ludG1lbnRBY3Rpb25Hcm91cCwgRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci52MTkuMSwgVmVyc2lvbj0xOS4xLjUuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iODhkMTc1NGQ3MDBlNDlhZAIGD2QWAgIBDzwrAAkBAA8WAh8CZ2RkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYSBTZjdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUFW2N0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSR2aWV3VmlzaWJsZUludGVydmFsQmxvY2skY3RsMDAkcG9wdXAFVGN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSR2aWV3U2VsZWN0b3JCbG9jayRjdGwwMCRjdGwwNAVUY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJHZpZXdTZWxlY3RvckJsb2NrJGN0bDAwJGN0bDA1BVRjdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUkdmlld1NlbGVjdG9yQmxvY2skY3RsMDAkY3RsMDYFXWN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSRjb250YWluZXJCbG9jayRNb3JlQnV0dG9ucyRUb3BCdXR0b25fMAVgY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJGNvbnRhaW5lckJsb2NrJE1vcmVCdXR0b25zJEJvdHRvbUJ1dHRvbl8wBUljdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUkYXB0TWVudUJsb2NrJFNNQVBUBUtjdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUkdmlld01lbnVCbG9jayRTTVZJRVcFTGN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSRuYXZCdXR0b25zQmxvY2skY3RsMDEFTGN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSRuYXZCdXR0b25zQmxvY2skY3RsMDMFVmN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSRtZXNzYWdlQm94QmxvY2skbWVzc2FnZUJveFBvcHVwBXJjdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUkbWVzc2FnZUJveEJsb2NrJG1lc3NhZ2VCb3hQb3B1cCRjdGwxOCRtZXNzYWdlQm94UG9wdXAkYnRuT2sFdmN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSRtZXNzYWdlQm94QmxvY2skbWVzc2FnZUJveFBvcHVwJGN0bDE4JG1lc3NhZ2VCb3hQb3B1cCRidG5DYW5jZWwFbGN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSR0b29sVGlwQmxvY2skYXBwb2ludG1lbnRUb29sVGlwRGl2JHRjJGNvbnRlbnQkYnRuRWRpdAVuY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJHRvb2xUaXBCbG9jayRhcHBvaW50bWVudFRvb2xUaXBEaXYkdGMkY29udGVudCRidG5EZWxldGUFOmN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSREUFAFQmN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXJQb3B1cCRBU1B4UG9wdXBDb250cm9sMU5AKhtR8JOJiJjFaTV03bdixMyrOpqEVuaQucD3sq5t',
        '__CALLBACKID': 'ctl00$ctl00$ContentBody$ContentBody$Rooster$mySchedule', # Request only appts and not whole pa

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
