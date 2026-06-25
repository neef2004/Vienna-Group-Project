# CALENDAR BACKEND
# GET /entries - Calendar Display Logic (query trips, expand multi-day, sort by date)
# POST /entries - Itinerary Integration (accept trip ID, pull dates/stops)
# GET /recurring-events - Recurrence Processing (generate occurrences from RRULE)
# PATCH /entries/:id - Editing Recurring Events (edit scope, exceptions)
# POST /entries/:id/reminders - Reminder Input Validation (offset, trigger time)
# GET /reminders/due - Reminder Scheduling (poll, deliver, mark sent)
