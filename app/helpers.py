from zoneinfo import ZoneInfo

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
    if os.path.exists('/app/token.json'):
        creds = Credentials.from_authorized_user_file('/app/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/app/credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080, bind_addr='0.0.0.0')
        # Save the credentials for the next run
        with open('/app/token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def login(username, password):
    url = 'https://nlda.rostareduflex.com/Webmodules/Pages/Login.aspx'
    payload = {
        '__VIEWSTATE': '/wEPDwUKLTM2OTc0NjYzNw9kFgJmD2QWAmYPZBYCAgIPZBYCAgEPZBYCAgEPFgIeC18hSXRlbUNvdW50AgEWAmYPZBYCZg8VAwBAaHR0cHM6Ly9ubGRhLnJvc3RhcmVkdWZsZXguY29tOjQ0My9XZWJtb2R1bGVzL1BhZ2VzL0RlZmF1bHQuYXNweARIb21lZGQFJzW8w+VCSUclLoq94wHRtERh2kNWww//ZUmc0jVMiQ==',
        'ctl00$ctl00$ContentBody$ContentBody$txtUser': username,
        'ctl00$ctl00$ContentBody$ContentBody$txtPass': password,
        'ctl00$ctl00$ContentBody$ContentBody$Button1': 'Log+in'
    }
    x = requests.post(url, data=payload, allow_redirects=False)

    return x.cookies


def getAppointments(sessionCookies, classId, start):
    appointmentFinder = re.compile(r"""dxo.AddAppointment\("([0-9]+)", new Date\(([0-9]+,[0-9]+,[0-9]+,[0-9]+,?[0-9]*)\), ([0-9]+), (.*?), "()", "(11111111)", "(Normal)", (0), (0), (0),\({\\'cpDocent\\':\\'(.*?)\\',\\'cpKlas\\':\\'(.*?)\\',\\'cpVak\\':\\'(.*?)\\',\\'cpAttribuut\\':\\'(.*?)\\',\\'cpTekst\\':\\'(.*?)\\',\\'cpKleur\\':\\'(.*?)\\',\\'cpLokaal\\':\\'(.*?)\\',\\'cpKlasType\\':\\'(.*?)\\',\\'cpLinkCode\\':\\'(.*?)\\',\\'cpExtraInfo\\':\\'(.*?)\\'}\)\);\\n""")

    url = 'https://nlda.rostareduflex.com/Webmodules/Pages/KlasRooster.aspx'
    payload = {
        '__VIEWSTATE': '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BDUzOTgENTM5NAQ1NjYyBDU0MDEENTM5OQQ1Mzk1BDUzOTYENTM5MwQ1MzkyBDU1MjEENTUyMgQ1NjIxBDU2MjIENTYyMAQ1NjE5BDU2MTgENTQ3MAQ1NjI1BDU2MjQENTYyMwQ1NzU3BDU0MDAENTYxMQQ1NDY4BDU2MTUENTYwOQQ1NjEwBDU2MTQENTYxNwQ1NjE2BDU2MTIENTYxMwQ1NjA4BDU2MDcENTUyNgQ1NjY0BDU3MjcENTcyOAQ1Nzg4BDU3ODcENTc5MgQ1NzkxBDU3OTAENTc4OQQ1NTI1BDU2NjUENTc5NwQ1Nzk4BDU3OTMENTc5NgQ1Nzk1BDU3OTQENTY2MwQ1NTIzBDU1MjQENTc4MQQ1NzgyBDU3NzcENTc3OAQ1NzgwBDU3ODYENTc4NQQ1Nzg0BDU3ODMENTc3OQQ1Nzc2BDU3NzUENTc2MAQ1NzYxBDU3NTQENTc1NQQ1NDg5BDU2NzAENTI0NAQ1NTUyBDU3MzUENTQ5MAQ1NjY5BDUyNDUENTU1MwQ1NzM2BDU0OTEENTY3MQQ1MjQ2BDU1NTQENTczNwQ1MjQ3BDU1NTYENTczOAQ1NDkyBDU2NjYENTI0OAQ1NTU3BDU3MzkENTQ5MwQ1NjY3BDU0OTQENTY2OAQ1MjM3BDU1NDUENTU0NgQ1MjM4BDU1NDMENTU0NAQ1NzIyBDU3MjMENTcyNAQ1NzI1BDUzMzMENTMzNAQ1MzM1BDUzMzYENTU5OAQ1NTk1BDUzMzcENTMzOAQ1MzM5BDUzNDAENTU5OQQ1NTk2BDUzNDEENTM0MgQ1MzQzBDUzNDQENTYwMAQ1NTk3BDUxNjkENTU3OAQ1NzQwBDU1NzkENTU4MAQ1NTgxBDU1ODIENTc0MQQ1NTgzBDU3NDMENTc0NAQ1NTg0BDU1ODUENTc0MgQ1NzQ1BDU3NDYENTc0NwQ1NTU1BDU2OTYENTY5NwQ1NzA4BDU3MDkENTcxMAQ1NTc1BDU3MTcENTcxOQQ1NTc2BDU3MTgENTU3NwQ0NzE1BDU3MjAEMTMwNQQ1NzYzBDE0MzIENDA0OQQ0MDA0BDU1ODkEMzk0MwQxNDM1BDUxNjcENDE2MwQ1MTc1BDUxNjUENTE2NgQ0NzA3BDQyNzgEMTQ1NQQ1MDMxBDM4OTEENTI3MgQ1Mzc3BDU3OTkENTQxOQQ1NDg4BDU0ODcENDk3NQQ0OTc0BDUxOTUENTQ4MwQ1NzAxBDQzODgEMzg5MAQ0MTQ1BDQwNTIEMzQxMwQxNDY3BDE1MzYEMTQ2OAQxNTM1BDE1NDQEMTQ2OQQxNDU0BDQ5ODEENTc3MwQ0NjAwBDQ1OTkEMzkxOQQzOTAzBDUxMDYENDYyNQQ0NTEzBDM0MTQENDUzMgQ0Nzk4BDQ1MTQENTE2OAQ1NzA1BDUyMjcENTUzNgQ1NzExBDUyMjgENTUzNwQ1NzEyBDUyMjkENTUzOAQ1NzEzBDUyMzAENTUzOQQ1NzE0BDUyMzEENTU0MAQ1NzE1BDUyMzIENTU0MQQ1NzE2BDUzMzIENTMzMQQ1MzMwBDU1MzIENTU0MgQ1NjkyBDU2NDcENTU5NAQ1NTkxBDU1OTIENTU5MwQ1NzIxBDU3NzQENTQ0MgQ1NDQzBDU0NDQENTQ0NQQ1NDMwBDU0MzEENTQzMgQ1NDMzBDU0MzQENTQzNQQ1NjI2BDU2MjcENTYyOAQ1NjI5BDU2MzAENTQzNgQ1NDM3BDU0MzgENTQzOQQ1NDQwBDU0NDEENTQ3MwQ1NTA4BDU2MzEENTUxMgQ1NTEzBDU1MTcENTUxOAQ1NTE1BDU1MTkENTUxNgQ0NjYyBDQ5MTcENTE0NAQ1NDU4BDU0NTkENTY1NgQ1NjU3BDU3NTYENTE5OAQ1NTEwBDUxOTkENTUxMQQ1NDk1BDU0OTYENTY3MgQ1NDgwBDU2ODkENTQ3OQQ1NDgxBDU0OTcENTY4MgQ1NDk4BDU2NzMENTY5MQQ1Njc0BDU0ODIENTQ5OQQ1Njc1BDU1MDAENTY3NgQ1NTAxBDU2OTAENDM5MAQ0Njg0BDUxMDgENTQ2MgQ1NDYxBDU0NjMENTY2MAQ1NjU5BDU1OTAENTYzNgQ1NjM1BDU1NjAENTU2MQQ1NTYyBDU1NzIENTU2NAQ1NTY1BDU1NjMENTU3MwQ1NTY2BDU1NjcENTU2OAQ1NTc0BDU1NjkENTU3MAQ1NTcxBDU1MjkENTcwNgQ1NzA3BDUzNTIENTU1OQQ1NjAxBDU3NDgENTM1MwQ1NzQ5BDUzNTQENTU1OAQ1NzUwBDU0MTYENTc1MQQ1NzUyBDU3NTMENTQxNwQ1NjkzBDU2MzIENTY5NAQ1NjMzBDU2MzQENTQxOAQ1NzAyBDU3MDMENTcwNAQ1MzY5BDU0MjAENTQyMQQ1NTIwBDU0MDgENTcyNgQ1NjQxBDU2NDIENTY0MwQ1NjQwBDU2NDUENTY0NAQ1NjM5BDU2MzcENTYzOAQ0MzkxBDQ2NjEENDkxNQQ1MTQzBDU0NTcENTQ2MAQ1NjU1BDU2NTgENTY0OAQ1NjQ5BDU2MDIENDg4OAQ1NjAzBDU3NjcENTc2OAQ1NzcwBDU3NzEENTc3MgQ1Njc4BDU0ODUENTQ4NgQ1Njc5BDU1MDYENTY4MAQ1NTA3BDU2ODEENDM4OQQ0MzkzBDQ2NTYENDY1NwQ0OTA5BDQ5MTAENTEzMwQ1MTM0BDUxMzUENTEzNgQ1MjA0BDU1MzEENTQ1MgQ1NDUzBDU0NTQENTQ1NQQ1NDU2BDU2NjEENTY1MAQ1NjUxBDU2NTIENTY1MwQ1NjU0FCsD+wNnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2cWAWZkAgUPZBYEAgEPZBYCZg9kFgJmD2QWAmYPZBYCZg88KwAFAQQUKwEAZAIDDzwrAAoCBBQrAAI8KwAJAQEUKwACZGRkBRQrAAJkZBYEZg9kFgRmD2QWAmYPZBYCZg9kFgJmD2QWAgIBD2QWAmYPZBYCZg9kFgJmD2QWAgIBDzwrAAkBAA8WAh4OXyFVc2VWaWV3U3RhdGVnZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgICAQ9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPPCsABQEEFCsBAGQCBQ9kFgJmD2QWBgIDD2QWAmYPZBYCZg88KwAJAgAPFgIfAmdkBg9kEBYGZgIBAgICAwIEAgUWBjwrAAwBABYGHwEFBE9wZW4eBE5hbWUFD09wZW5BcHBvaW50bWVudB4OUnVudGltZUNyZWF0ZWRnPCsADAEAFggfAQULRWRpdCBTZXJpZXMfAwUKRWRpdFNlcmllcx8EZx4KQmVnaW5Hcm91cGc8KwAMAQAWCB8BBRVSZXN0b3JlIERlZmF1bHQgU3RhdGUfAwURUmVzdG9yZU9jY3VycmVuY2UfBGcfBWc8KwAMAgAWDB8BBQxTaG93IFRpbWUgQXMfAwUNU3RhdHVzU3ViTWVudR4LTmF2aWdhdGVVcmxlHgZUYXJnZXRlHwVnHwRnAQ8WAh4KSXNTYXZlZEFsbGcPFCsABRQrAAwWEB8DBQ9TdGF0dXNTdWJNZW51ITAfBmUeCFNlbGVjdGVkaB8HZR8BBQRGcmVlHgdUb29sVGlwZR4JR3JvdXBOYW1lBQNTVEEfBGcPFgIfCGdkZGRkZGRkZDwrAA4BABYWHg1WZXJ0aWNhbEFsaWduCyonU3lzdGVtLldlYi5VSS5XZWJDb250cm9scy5WZXJ0aWNhbEFsaWduAB4KTGluZUhlaWdodBweB1NwYWNpbmccHgZDdXJzb3JlHhxUb29sYmFyRHJvcERvd25CdXR0b25TcGFjaW5nHB4PSG9yaXpvbnRhbEFsaWduCyopU3lzdGVtLldlYi5VSS5XZWJDb250cm9scy5Ib3Jpem9udGFsQWxpZ24AHgRXcmFwCyl6RGV2RXhwcmVzcy5VdGlscy5EZWZhdWx0Qm9vbGVhbiwgRGV2RXhwcmVzcy5EYXRhLnYxOS4xLCBWZXJzaW9uPTE5LjEuNS4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI4OGQxNzU0ZDcwMGU0OWECHhlUb29sYmFyUG9wT3V0SW1hZ2VTcGFjaW5nHB4VRHJvcERvd25CdXR0b25TcGFjaW5nHB4HT3BhY2l0eQL/////Dx4MSW1hZ2VTcGFjaW5nHDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhxkFCsADBYQHwMFD1N0YXR1c1N1Yk1lbnUhMR8GZR8JaB8HZR8BBQlUZW50YXRpdmUfCmUfCwUDU1RBHwRnDxYCHwhnZGRkZGRkZGQ8KwAOAQAWFh8MCysEAB8NHB8OHB8PZR8QHB8RCysFAB8SCysGAh8THB8UHB8VAv////8PHxYcPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHGQUKwAMFhAfAwUPU3RhdHVzU3ViTWVudSEyHwZlHwloHwdlHwEFBEJ1c3kfCmUfCwUDU1RBHwRnDxYCHwhnZGRkZGRkZGQ8KwAOAQAWFh8MCysEAB8NHB8OHB8PZR8QHB8RCysFAB8SCysGAh8THB8UHB8VAv////8PHxYcPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHGQUKwAMFhAfAwUPU3RhdHVzU3ViTWVudSEzHwZlHwloHwdlHwEFDU91dCBPZiBPZmZpY2UfCmUfCwUDU1RBHwRnDxYCHwhnZGRkZGRkZGQ8KwAOAQAWFh8MCysEAB8NHB8OHB8PZR8QHB8RCysFAB8SCysGAh8THB8UHB8VAv////8PHxYcPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHGQUKwAMFhAfAwUPU3RhdHVzU3ViTWVudSE0HwZlHwloHwdlHwEFEVdvcmtpbmcgRWxzZXdoZXJlHwplHwsFA1NUQR8EZw8WAh8IZ2RkZGRkZGRkPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhxkDxQrAQUCAQIBAgECAQIBFgEFmgFEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLkFTUHhTY2hlZHVsZXJNZW51SXRlbSwgRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci52MTkuMSwgVmVyc2lvbj0xOS4xLjUuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iODhkMTc1NGQ3MDBlNDlhPCsADAIAFgwfAQUITGFiZWwgQXMfAwUMTGFiZWxTdWJNZW51HwZlHwdlHwVoHwRnAQ8WAh8IZw8UKwALFCsADBYQHwMFDkxhYmVsU3ViTWVudSEwHwZlHwloHwdlHwEFBE5vbmUfCmUfCwUDTEJMHwRnDxYCHwhnZGRkZGRkZGQ8KwAOAQAWFh8MCysEAB8NHB8OHB8PZR8QHB8RCysFAB8SCysGAh8THB8UHB8VAv////8PHxYcPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHGQUKwAMFhAfAwUOTGFiZWxTdWJNZW51ITEfBmUfCWgfB2UfAQUJSW1wb3J0YW50HwplHwsFA0xCTB8EZw8WAh8IZ2RkZGRkZGRkPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhxkFCsADBYQHwMFDkxhYmVsU3ViTWVudSEyHwZlHwloHwdlHwEFCEJ1c2luZXNzHwplHwsFA0xCTB8EZw8WAh8IZ2RkZGRkZGRkPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhxkFCsADBYQHwMFDkxhYmVsU3ViTWVudSEzHwZlHwloHwdlHwEFCFBlcnNvbmFsHwplHwsFA0xCTB8EZw8WAh8IZ2RkZGRkZGRkPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhxkFCsADBYQHwMFDkxhYmVsU3ViTWVudSE0HwZlHwloHwdlHwEFCFZhY2F0aW9uHwplHwsFA0xCTB8EZw8WAh8IZ2RkZGRkZGRkPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhxkFCsADBYQHwMFDkxhYmVsU3ViTWVudSE1HwZlHwloHwdlHwEFC011c3QgQXR0ZW5kHwplHwsFA0xCTB8EZw8WAh8IZ2RkZGRkZGRkPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhxkFCsADBYQHwMFDkxhYmVsU3ViTWVudSE2HwZlHwloHwdlHwEFD1RyYXZlbCBSZXF1aXJlZB8KZR8LBQNMQkwfBGcPFgIfCGdkZGRkZGRkZDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhw8KwAOAQAWFh8MCysEAB8NHB8OHB8PZR8QHB8RCysFAB8SCysGAh8THB8UHB8VAv////8PHxYcZBQrAAwWEB8DBQ5MYWJlbFN1Yk1lbnUhNx8GZR8JaB8HZR8BBRFOZWVkcyBQcmVwYXJhdGlvbh8KZR8LBQNMQkwfBGcPFgIfCGdkZGRkZGRkZDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhw8KwAOAQAWFh8MCysEAB8NHB8OHB8PZR8QHB8RCysFAB8SCysGAh8THB8UHB8VAv////8PHxYcZBQrAAwWEB8DBQ5MYWJlbFN1Yk1lbnUhOB8GZR8JaB8HZR8BBQhCaXJ0aGRheR8KZR8LBQNMQkwfBGcPFgIfCGdkZGRkZGRkZDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhw8KwAOAQAWFh8MCysEAB8NHB8OHB8PZR8QHB8RCysFAB8SCysGAh8THB8UHB8VAv////8PHxYcZBQrAAwWEB8DBQ5MYWJlbFN1Yk1lbnUhOR8GZR8JaB8HZR8BBQtBbm5pdmVyc2FyeR8KZR8LBQNMQkwfBGcPFgIfCGdkZGRkZGRkZDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhw8KwAOAQAWFh8MCysEAB8NHB8OHB8PZR8QHB8RCysFAB8SCysGAh8THB8UHB8VAv////8PHxYcZBQrAAwWEB8DBQ9MYWJlbFN1Yk1lbnUhMTAfBmUfCWgfB2UfAQUKUGhvbmUgQ2FsbB8KZR8LBQNMQkwfBGcPFgIfCGdkZGRkZGRkZDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhw8KwAOAQAWFh8MCysEAB8NHB8OHB8PZR8QHB8RCysFAB8SCysGAh8THB8UHB8VAv////8PHxYcZA8UKwELAgECAQIBAgECAQIBAgECAQIBAgECARYBBZoBRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci5BU1B4U2NoZWR1bGVyTWVudUl0ZW0sIERldkV4cHJlc3MuV2ViLkFTUHhTY2hlZHVsZXIudjE5LjEsIFZlcnNpb249MTkuMS41LjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjg4ZDE3NTRkNzAwZTQ5YTwrAAwCABYIHwEFBkRlbGV0ZR8DBRFEZWxldGVBcHBvaW50bWVudB8EZx8FZwIUKwACZBQrAAEWAh4IQ3NzQ2xhc3MFIWR4U2NoZWR1bGVyX01lbnVfRGVsZXRlX09mZmljZTM2NQ8WBgIBAgECAWZmAgEWAQWaAURldkV4cHJlc3MuV2ViLkFTUHhTY2hlZHVsZXIuQVNQeFNjaGVkdWxlck1lbnVJdGVtLCBEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLnYxOS4xLCBWZXJzaW9uPTE5LjEuNS4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI4OGQxNzU0ZDcwMGU0OWFkAgQPZBYCZg9kFgJmDzwrAAkCAA8WAh8CZ2QGD2QQFglmAgECAgIDAgQCBQIGAgcCCBYJPCsADAEAFggfAQULR28gdG8gVG9kYXkfAwUJR290b1RvZGF5HwRnHwVnPCsADAIAFgYfAQUNR28gdG8gRGF0ZS4uLh8DBQhHb3RvRGF0ZR8EZwIUKwACZBQrAAEWAh8XBSNkeFNjaGVkdWxlcl9NZW51X0dvVG9EYXRlX09mZmljZTM2NTwrAAwCABYMHwEFDkNoYW5nZSBWaWV3IFRvHwMFDlN3aXRjaFZpZXdNZW51HwZlHwdlHwVnHwRnAQ8WAh8IZw8UKwADFCsADBYQHwMFD1N3aXRjaFRvRGF5Vmlldx8GZR8JaB8HZR8BBQhEYWcgVmlldx8KZR8LBQJWVx8EZw8WAh8IZ2RkZGRkZGRkPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhxkFCsADBYQHwMFFFN3aXRjaFRvV29ya1dlZWtWaWV3HwZlHwloHwdlHwEFDldlcmsgV2VlayBWaWV3HwplHwsFAlZXHwRnDxYCHwhnZGRkZGRkZGQ8KwAOAQAWFh8MCysEAB8NHB8OHB8PZR8QHB8RCysFAB8SCysGAh8THB8UHB8VAv////8PHxYcPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHGQUKwAMFhAfAwURU3dpdGNoVG9Nb250aFZpZXcfBmUfCWgfB2UfAQUKTW9udGggVmlldx8KZR8LBQJWVx8EZw8WAh8IZ2RkZGRkZGRkPCsADgEAFhYfDAsrBAAfDRwfDhwfD2UfEBwfEQsrBQAfEgsrBgIfExwfFBwfFQL/////Dx8WHDwrAA4BABYWHwwLKwQAHw0cHw4cHw9lHxAcHxELKwUAHxILKwYCHxMcHxQcHxUC/////w8fFhxkDxQrAQMCAQIBAgEWAQWaAURldkV4cHJlc3MuV2ViLkFTUHhTY2hlZHVsZXIuQVNQeFNjaGVkdWxlck1lbnVJdGVtLCBEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLnYxOS4xLCBWZXJzaW9uPTE5LjEuNS4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI4OGQxNzU0ZDcwMGU0OWE8KwAMAQAWCh8BBQo2MCBNaW51dGVzHwMFGFN3aXRjaFRpbWVTY2FsZSEwMTowMDowMB8LBQNUU0wfBGcfBWc8KwAMAQAWCh8BBQozMCBNaW51dGVzHwMFGFN3aXRjaFRpbWVTY2FsZSEwMDozMDowMB8LBQNUU0wfBGcfBWg8KwAMAQAWCh8BBQoxNSBNaW51dGVzHwMFGFN3aXRjaFRpbWVTY2FsZSEwMDoxNTowMB8LBQNUU0wfBGcfBWg8KwAMAQAWCh8BBQoxMCBNaW51dGVzHwMFGFN3aXRjaFRpbWVTY2FsZSEwMDoxMDowMB8LBQNUU0wfBGcfBWg8KwAMAQAWCh8BBQk2IE1pbnV0ZXMfAwUYU3dpdGNoVGltZVNjYWxlITAwOjA2OjAwHwsFA1RTTB8EZx8FaDwrAAwBABYKHwEFCTUgTWludXRlcx8DBRhTd2l0Y2hUaW1lU2NhbGUhMDA6MDU6MDAfCwUDVFNMHwRnHwVoDxYJAgECAWYCAQIBAgECAQIBAgEWAQWaAURldkV4cHJlc3MuV2ViLkFTUHhTY2hlZHVsZXIuQVNQeFNjaGVkdWxlck1lbnVJdGVtLCBEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLnYxOS4xLCBWZXJzaW9uPTE5LjEuNS4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI4OGQxNzU0ZDcwMGU0OWFkAgoPZBYCZg9kFgRmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYKAgEPPCsABAEADxYCHg9EYXRhU291cmNlQm91bmRnZGQCAw88KwAEAQAPFgIfGGdkZAIFDzwrAAQBAA8WAh8YZ2RkAgcPFCsABg8WAh8BBQhCZXdlcmtlbmQUKwAMFggeBVdpZHRoGwAAAAAAAElABwAAAB4GSGVpZ2h0GwAAAAAAAEZAAQAAAB4LQm9yZGVyU3R5bGULKiVTeXN0ZW0uV2ViLlVJLldlYkNvbnRyb2xzLkJvcmRlclN0eWxlAR4EXyFTQgLAA2RkZBQrAAEWBB4FU3R5bGULKwcEHxkbAAAAAAAA8D8BAAAAZGRkZGQ8KwAMAQAWBB8XBRdkeHNjLWRhdC1jb2xvcmVkLWJ1dHRvbh8cAgI8KwAMAQAWBB8XBRdkeHNjLWRhdC1jb2xvcmVkLWJ1dHRvbh8cAgJkZDwrAAcBATwrAAwBABYEHxcFFWR4c2MtZGF0LWRpc2FibGVkLWJ0bh8cAgJkZAIJDxQrAAYPFgIfAQULVmVyd2lqZGVyZW5kFCsADBYIHxkbAAAAAAAASUAHAAAAHxobAAAAAAAARkABAAAAHxsLKwcBHxwCwANkZGQUKwABFgQfHQsrBwQfGRsAAAAAAADwPwEAAABkZGRkZDwrAAwBABYEHxcFF2R4c2MtZGF0LWNvbG9yZWQtYnV0dG9uHxwCAjwrAAwBABYEHxcFF2R4c2MtZGF0LWNvbG9yZWQtYnV0dG9uHxwCAmRkPCsABwEBPCsADAEAFgQfFwUVZHhzYy1kYXQtZGlzYWJsZWQtYnRuHxwCAmRkAgEPZBYCZg9kFgJmD2QWAgIBD2QWAgIBD2QWAmYPZBYCZg9kFgJmD2QWBAIBDzwrAAQBAA8WAh8YZ2RkAgMPPCsABAEADxYEHgVWYWx1ZQUkRHJ1ayBvcCBFU0Mgb20gZGUgYWN0aWUgdGUgYW5udWxlcmVuHxhnZGQCAg88KwAHAQYPFgIfCGcPFCsAAhQrAAIWBh4KQWN0aW9uTmFtZQURY3JlYXRlQXBwb2ludG1lbnQfAQUPTmlldXdlIGFmc3ByYWFrHgtDb250ZXh0TmFtZQUMQ2VsbFNlbGVjdGVkZBQrAAQWAh8gBRNBcHBvaW50bWVudFNlbGVjdGVkD2QQFgJmAgEWAhQrAAIWBh8fBQ9lZGl0QXBwb2ludG1lbnQfAQUIQmV3ZXJrZW4fBGdkFCsAAhYGHx8FEWRlbGV0ZUFwcG9pbnRtZW50HwEFC1ZlcndpamRlcmVuHwRnZA8WAgIBAgIWAgWhAURldkV4cHJlc3MuV2ViLkFTUHhTY2hlZHVsZXIuRkFCRWRpdEFwcG9pbnRtZW50QWN0aW9uSXRlbSwgRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci52MTkuMSwgVmVyc2lvbj0xOS4xLjUuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iODhkMTc1NGQ3MDBlNDlhBaMBRGV2RXhwcmVzcy5XZWIuQVNQeFNjaGVkdWxlci5GQUJEZWxldGVBcHBvaW50bWVudEFjdGlvbkl0ZW0sIERldkV4cHJlc3MuV2ViLkFTUHhTY2hlZHVsZXIudjE5LjEsIFZlcnNpb249MTkuMS41LjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjg4ZDE3NTRkNzAwZTQ5YWRkDxQrAQICAQICFgIFnwFEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLkZBQkNyZWF0ZUFwcG9pbnRtZW50QWN0aW9uLCBEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLnYxOS4xLCBWZXJzaW9uPTE5LjEuNS4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI4OGQxNzU0ZDcwMGU0OWEFogFEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLkZBQkVkaXRBcHBvaW50bWVudEFjdGlvbkdyb3VwLCBEZXZFeHByZXNzLldlYi5BU1B4U2NoZWR1bGVyLnYxOS4xLCBWZXJzaW9uPTE5LjEuNS4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI4OGQxNzU0ZDcwMGU0OWFkAgYPZBYCAgEPPCsACQEADxYCHwJnZGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFhIFNmN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZQVbY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJHZpZXdWaXNpYmxlSW50ZXJ2YWxCbG9jayRjdGwwMCRwb3B1cAVUY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJHZpZXdTZWxlY3RvckJsb2NrJGN0bDAwJGN0bDA0BVRjdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUkdmlld1NlbGVjdG9yQmxvY2skY3RsMDAkY3RsMDUFVGN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSR2aWV3U2VsZWN0b3JCbG9jayRjdGwwMCRjdGwwNgVdY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJGNvbnRhaW5lckJsb2NrJE1vcmVCdXR0b25zJFRvcEJ1dHRvbl8wBWBjdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUkY29udGFpbmVyQmxvY2skTW9yZUJ1dHRvbnMkQm90dG9tQnV0dG9uXzAFSWN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSRhcHRNZW51QmxvY2skU01BUFQFS2N0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSR2aWV3TWVudUJsb2NrJFNNVklFVwVMY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJG5hdkJ1dHRvbnNCbG9jayRjdGwwMQVMY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJG5hdkJ1dHRvbnNCbG9jayRjdGwwMwVWY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJG1lc3NhZ2VCb3hCbG9jayRtZXNzYWdlQm94UG9wdXAFcmN0bDAwJGN0bDAwJENvbnRlbnRCb2R5JENvbnRlbnRCb2R5JFJvb3N0ZXIkbXlTY2hlZHVsZSRtZXNzYWdlQm94QmxvY2skbWVzc2FnZUJveFBvcHVwJGN0bDE4JG1lc3NhZ2VCb3hQb3B1cCRidG5PawV2Y3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJG1lc3NhZ2VCb3hCbG9jayRtZXNzYWdlQm94UG9wdXAkY3RsMTgkbWVzc2FnZUJveFBvcHVwJGJ0bkNhbmNlbAVsY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJHRvb2xUaXBCbG9jayRhcHBvaW50bWVudFRvb2xUaXBEaXYkdGMkY29udGVudCRidG5FZGl0BW5jdGwwMCRjdGwwMCRDb250ZW50Qm9keSRDb250ZW50Qm9keSRSb29zdGVyJG15U2NoZWR1bGUkdG9vbFRpcEJsb2NrJGFwcG9pbnRtZW50VG9vbFRpcERpdiR0YyRjb250ZW50JGJ0bkRlbGV0ZQU6Y3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlciRteVNjaGVkdWxlJERQUAVCY3RsMDAkY3RsMDAkQ29udGVudEJvZHkkQ29udGVudEJvZHkkUm9vc3RlclBvcHVwJEFTUHhQb3B1cENvbnRyb2wxlNCkZ9fT0DYtvuYw74kWNkMdYL73BUWyh52aQppSJBw=',
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