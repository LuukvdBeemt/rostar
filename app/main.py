from helpers import *
import os


WEEKS = 10

    
def main():
    # Get eduflex cookies and google calender service api
    print("Getting eduflex cookies and calender service api...")
    sessionCookies = login(os.environ['ROSTAR_USER'], os.environ['ROSTAR_PASS'])
    service = get_calender_service()

    # Get start day of current week
    today = datetime.datetime.today().replace(tzinfo=ZoneInfo('Europe/Amsterdam'), hour=0, minute=0, second=0, microsecond=0)
    start = today - datetime.timedelta(days=today.isoweekday() - 1)
    
    for week in range(WEEKS):
        print(f"Week {week}:")

        # The start and end of the current week
        timeMin = start + datetime.timedelta(weeks=week)
        timeMax = timeMin + datetime.timedelta(weeks=1)

        print("Fetching upcoming google calender events...")
        # Query all google calender items with a start time later than current time
        events = service.events().list(calendarId='8f1fb85f4584ad953c5845069af48336ac78fb9eaa0013a1a4fa2004a2d11196@group.calendar.google.com', 
                maxResults=2500, 
                timeMin=timeMin.isoformat(), 
                timeMax=timeMax.isoformat()
            ).execute().get('items', [])

        # Get Paralax appointments
        print("Fetching upcoming eduflex appointments...")
        appointments = getAppointments(sessionCookies, 5143, timeMin)

        print("Checking for new events...")
        newEvents = []
        for appointment in appointments:
            newEvent = formatEvent(appointment)
            newEvents.append(newEvent)

            if not findEvent(newEvent, events):
                event = service.events().insert(calendarId='8f1fb85f4584ad953c5845069af48336ac78fb9eaa0013a1a4fa2004a2d11196@group.calendar.google.com', body=newEvent).execute()    
                print(f"Created calender item with id: {event['id']}")
                # print(f"Created calender item with id")

        print("Checking for deleted events...")
        for event in events:
            if not findEvent(event, newEvents):
                print(f"Deleting calender item with id: {event['id']}")
                event = service.events().delete(calendarId='8f1fb85f4584ad953c5845069af48336ac78fb9eaa0013a1a4fa2004a2d11196@group.calendar.google.com', eventId=event["id"]).execute()    


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


if __name__ == '__main__':
    main()
