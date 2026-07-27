from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pytz
from dateutil.rrule import rrulestr
from icalendar import Calendar, Event as ICalEvent
from app.db import get_db


def expand_trip_events_raw(events, start_date, end_date):
    all_occurrences = []
    for event in events:
        occurrences = expand_recurring_event_raw(event, start_date, end_date)
        all_occurrences.extend(occurrences)
    all_occurrences.sort(key=lambda e: e['start_time'])
    return all_occurrences


def expand_recurring_event_raw(event, start_date, end_date):
    if not event.get('rrule'):
        if start_date <= datetime.fromisoformat(event['start_time']) <= end_date:
            return [event]
        else:
            return []
    
    try:
        rule = rrulestr(event['rrule'], dtstart=datetime.fromisoformat(event['start_time']))
    except Exception as e:
        print(f"Error parsing RRULE for event {event['id']}: {e}")
        return []
    
    occurrences = rule.between(start_date, end_date)
    result = []
    
    for occ_time in occurrences:
        start = datetime.fromisoformat(event['start_time'])
        end = datetime.fromisoformat(event['end_time'])
        duration = end - start
        
        result.append({
            'id': event['id'],
            'trip_id': event['trip_id'],
            'title': event['title'],
            'description': event['description'],
            'start_time': occ_time.isoformat(),
            'end_time': (occ_time + duration).isoformat(),
            'timezone': event['timezone']
        })
    
    return result


def parse_ics_file(file_path: str) -> Optional[Calendar]:
    try:
        with open(file_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())
        return cal
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error parsing .ics file: {e}")
        return None


def import_ics_to_trip(trip_id: int, file_path: str) -> Tuple[int, List[str]]:
    cal = parse_ics_file(file_path)
    if cal is None:
        return 0, ["Failed to parse .ics file"]

    imported_count = 0
    errors = []

    for component in cal.walk('VEVENT'):
        try:
            event_data = _extract_event_data_from_ical(component)
            
            create_event_from_ical(trip_id, event_data)
            imported_count += 1

        except Exception as e:
            errors.append(f"Error importing event: {str(e)}")
            continue

    return imported_count, errors


def _extract_event_data_from_ical(component: ICalEvent) -> Dict:
    title = component.get('SUMMARY', 'Untitled Event')
    description = component.get('DESCRIPTION')

    dtstart = component.get('DTSTART')
    dtend = component.get('DTEND')

    if dtstart is None:
        raise ValueError("Event has no DTSTART")

    start_time = dtstart.dt
    end_time = dtend.dt if dtend else start_time + timedelta(hours=1)

    timezone = 'UTC'
    if 'TZID' in str(dtstart.params):
        tzid_str = dtstart.params.get('TZID', 'UTC')
        timezone = tzid_str

    if isinstance(start_time, datetime) and start_time.tzinfo is not None:
        start_time = start_time.astimezone(pytz.UTC).replace(tzinfo=None)
    
    if isinstance(end_time, datetime) and end_time.tzinfo is not None:
        end_time = end_time.astimezone(pytz.UTC).replace(tzinfo=None)

    rrule = None
    if component.get('RRULE'):
        rrule_obj = component.get('RRULE')
        rrule = rrule_obj.to_ical().decode('utf-8') if isinstance(rrule_obj.to_ical(), bytes) else str(rrule_obj.to_ical())

    return {
        'title': str(title),
        'description': str(description) if description else None,
        'start_time': start_time,
        'end_time': end_time,
        'timezone': timezone,
        'rrule': rrule,
    }


def create_event_from_ical(trip_id: int, event_data: Dict):
    from app.models.trip import create_event
    create_event(trip_id, event_data['title'], event_data.get('description'), 
                 event_data['start_time'], event_data['end_time'], 
                 event_data['timezone'], event_data.get('rrule'))


def convert_time_to_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    try:
        from_zone = pytz.timezone(from_tz)
        to_zone = pytz.timezone(to_tz)

        if dt.tzinfo is None:
            dt = from_zone.localize(dt)
        else:
            dt = dt.astimezone(from_zone)

        return dt.astimezone(to_zone)

    except Exception as e:
        print(f"Error converting timezone: {e}")
        return dt


def validate_rrule(rrule_string: str) -> Tuple[bool, Optional[str]]:
    try:
        rrulestr(rrule_string, ignoretz=True)
        return True, None
    except Exception as e:
        return False, str(e)


def get_next_occurrence(event: Dict, after_date: datetime) -> Optional[datetime]:
    if not event.get('rrule'):
        start = datetime.fromisoformat(event['start_time'])
        return start if start > after_date else None

    try:
        rule = rrulestr(event['rrule'], dtstart=datetime.fromisoformat(event['start_time']))
        occurrences = rule.after(after_date, inc=False, count=1)
        return occurrences[0] if occurrences else None
    except Exception as e:
        print(f"Error getting next occurrence: {e}")
        return None
    
def generate_ics_from_events(trip, events):
    from icalendar import Calendar, Event as ICalEvent
    
    cal = Calendar()
    cal.add('prodid', '-//Vienna Group Project//Calendar//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    
    for event in events:
        vevent = ICalEvent()
        vevent.add('summary', event['title'])
        vevent.add('description', event.get('description', ''))
        vevent.add('dtstart', datetime.fromisoformat(event['start_time']))
        vevent.add('dtend', datetime.fromisoformat(event['end_time']))
        
        if event.get('rrule'):
            vevent.add('rrule', event['rrule'])
        
        vevent.add('location', '')
        vevent.add('uid', f"{event['id']}@vienna-group-project.com")
        
        cal.add_component(vevent)
    
    return cal.to_ical()