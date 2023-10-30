from helpers import *
from klas_helper import load_klas_data

WEEKS = 14
    
def main():
    # Get start day of current week
    today = datetime.datetime.today().replace(microsecond=0).replace(tzinfo=ZoneInfo('Europe/Amsterdam'), hour=0, minute=0, second=0, microsecond=0)
    start = today - datetime.timedelta(days=today.isoweekday() - 1)
    
    # Get eduflex cookies and google calender service api
    printDated("Getting eduflex cookies and calender service api...")
    sessionCookies = login(os.environ['ROSTAR_USER'], os.environ['ROSTAR_PASS'])
    service = get_calender_service()


    # Get list of klassen
    klas_data = load_klas_data()
    for friendly_name, klas_name_id in klas_data.items():
        printDated(f"Processing {friendly_name}:")
        klas_name, klas_id = klas_name_id
        calendar_id = get_or_create_calendar(service, klas_id, friendly_name)
        processKlas(sessionCookies, service, start, klas_id, calendar_id)
    
    
def processKlas(sessionCookies, service, start, id, calenderId):
    for week in range(WEEKS):
        printDated(f"\nWeek {week}:")

        # The start and end of the current week
        timeMin = start + datetime.timedelta(weeks=week)
        timeMax = timeMin + datetime.timedelta(weeks=1)

        printDated("Fetching upcoming google calender events...")
        # Query all google calender items with a start time later than current time
        events = service.events().list(calendarId=calenderId, 
                maxResults=2500, 
                timeMin=timeMin.isoformat(), 
                timeMax=timeMax.isoformat()
            ).execute().get('items', [])

        # Get Paralax appointments
        printDated("Fetching upcoming eduflex appointments...")
        appointments = getAppointments(sessionCookies, id, timeMin)

        printDated("Checking for new events...")
        newEvents = []
        for appointment in appointments:
            newEvent = formatEvent(appointment)
            newEvents.append(newEvent)

            if not findEvent(newEvent, events):
                event = service.events().insert(calendarId=calenderId, body=newEvent).execute()    
                printDated(f"Created calender item with id: {event['id']}")
                # printDated(f"Created calender item with id")

        printDated("Checking for deleted events...")
        for event in events:
            if not findEvent(event, newEvents):
                printDated(f"Deleting calender item with id: {event['id']}")
                event = service.events().delete(calendarId=calenderId, eventId=event["id"]).execute()    


def findEvent(newEvent, events):
    """Returns True if event was found in list."""
    for event in events:
        if newEvent['summary'] == event['summary'] and newEvent['description'] == event['description'] and newEvent['start'] == event['start'] and newEvent['end'] == event['end'] and locationsMatch(newEvent, event):
            return True
    return False

def locationsMatch(newEvent, event):
    if 'location' in newEvent.keys():
        if newEvent['location'] == '':
            if not 'location' in event.keys():
                return True # Both new and old event have missing location info, they are the same.
        else:
            if 'location' in event.keys():
                if newEvent['location'] == event['location']:
                    return True # Both new and old event have matching location info.
    else:
        if event['location'] == '':
            return True
            
    return False

def printDated(message):
    now = datetime.datetime.today().replace(microsecond=0)
    print(f"{now.isoformat()}: {message}")

if __name__ == '__main__':
    main()