import { useEffect, useMemo, useState } from "react";
import {
  createTripEvent,
  createTrip,
  getTripEvents,
  getUserTrips,
  type CalendarEvent,
  type Trip,
} from "../api/trips";
import CalendarDisplay from "./CalendarDisplay";

/*
    These are date formatting helper function
*/
function parseDateOnly(date: string): Date {
    const [year, month, day] = date.slice(0, 10).split("-").map(Number);
  
    return new Date(Date.UTC(year, month - 1, day));
  }
  
  function formatDateOnly(date: Date): string {
    return date.toISOString().slice(0, 10);
  }
  
  //gets the trip days based on the trip start and end time
  function getTripDays(startDate: string, endDate: string): string[] {
    const days: string[] = [];
    const current = parseDateOnly(startDate);
    const end = parseDateOnly(endDate);
  
    while (current <= end) {
      days.push(formatDateOnly(current));
      current.setUTCDate(current.getUTCDate() + 1);
    }
  
    return days;
  }

  //more date and time formatting
  function formatDayLabel(date: string, index: number): string {
    const formattedDate = parseDateOnly(date).toLocaleDateString(undefined, {
      timeZone: "UTC",
      weekday: "short",
      month: "short",
      day: "numeric",
    });
  
    return `Day ${index + 1} — ${formattedDate}`;
  }
  
  function formatTime(dateTime: string): string {
    const time = dateTime.match(/T(\d{2}):(\d{2})/);
  
    return time ? `${time[1]}:${time[2]}` : dateTime;
  }

function ItineraryPage() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [selectedTripId, setSelectedTripId] = useState<number | null>(null);
  const [view, setView] = useState<"itinerary" | "calendar">("itinerary");

  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  const [isLoadingTrips, setIsLoadingTrips] = useState(true);
  const [isLoadingEvents, setIsLoadingEvents] = useState(false);
  const [isCreatingTrip, setIsCreatingTrip] = useState(false);
  const [isCreatingEvent, setIsCreatingEvent] = useState(false);
  const [showTripForm, setShowTripForm] = useState(false);
  const [showEventForm, setShowEventForm] = useState(false);
  const [tripName, setTripName] = useState("");
  const [tripDescription, setTripDescription] = useState("");
  const [tripStartDate, setTripStartDate] = useState("");
  const [tripEndDate, setTripEndDate] = useState("");
  const [eventTitle, setEventTitle] = useState("");
  const [eventDescription, setEventDescription] = useState("");
  const [eventStartTime, setEventStartTime] = useState("");
  const [eventEndTime, setEventEndTime] = useState("");
  const [eventTimezone, setEventTimezone] = useState("Europe/Vienna");
  const [error, setError] = useState("");

  const selectedTrip = useMemo(
    () => trips.find((trip) => trip.id === selectedTripId) ?? null,
    [trips, selectedTripId]
  );

  const tripDays = useMemo(() => {
    if (!selectedTrip) {
      return [];
    }

    return getTripDays(selectedTrip.startDate, selectedTrip.endDate);
  }, [selectedTrip]);

  const eventsForSelectedDay = useMemo(() => {
    if (!selectedDate) {
      return [];
    }

    return events
      .filter((event) => event.startTime.slice(0, 10) === selectedDate)
      .sort(
        (firstEvent, secondEvent) =>
          new Date(firstEvent.startTime).getTime() -
          new Date(secondEvent.startTime).getTime()
      );
  }, [events, selectedDate]);

  useEffect(() => {
    async function loadTrips() {
      try {
        setIsLoadingTrips(true);
        setError("");

        const loadedTrips = await getUserTrips();

        setTrips(loadedTrips);
        setSelectedTripId(
          loadedTrips.length > 0 ? loadedTrips[0].id : null
        );
      } catch (error) {
        setError(
          error instanceof Error ? error.message : "Failed to load trips"
        );
      } finally {
        setIsLoadingTrips(false);
      }
    }

    loadTrips();
  }, []);

  useEffect(() => {
    if (!selectedTrip) {
      setEvents([]);
      setSelectedDate(null);
      return;
    }

    const trip = selectedTrip;
    let requestCancelled = false;

    async function loadEvents() {
      try {
        setIsLoadingEvents(true);
        setError("");

        const loadedEvents = await getTripEvents(trip);

        if (!requestCancelled) {
          setEvents(loadedEvents);
          setSelectedDate(trip.startDate.slice(0, 10));
        }
      } catch (error) {
        if (!requestCancelled) {
          setEvents([]);
          setError(
            error instanceof Error
              ? error.message
              : "Failed to load trip events"
          );
        }
      } finally {
        if (!requestCancelled) {
          setIsLoadingEvents(false);
        }
      }
    }

    loadEvents();

    return () => {
      requestCancelled = true;
    };
  }, [selectedTrip]);

  function handleTripChange(event: React.ChangeEvent<HTMLSelectElement>) {
    setSelectedTripId(Number(event.target.value));
  }

  async function handleCreateTrip(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (tripStartDate >= tripEndDate) {
      setError("The end date must be after the start date");
      return;
    }

    try {
      setIsCreatingTrip(true);

      const newTrip = await createTrip({
        name: tripName.trim(),
        description: tripDescription.trim(),
        startDate: tripStartDate,
        endDate: tripEndDate,
      });

      setTrips((currentTrips) => [...currentTrips, newTrip]);
      setSelectedTripId(newTrip.id);
      setTripName("");
      setTripDescription("");
      setTripStartDate("");
      setTripEndDate("");
      setShowTripForm(false);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Failed to create trip"
      );
    } finally {
      setIsCreatingTrip(false);
    }
  }

  async function handleCreateEvent(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (selectedTripId === null || selectedDate === null) {
      setError("Select a trip and day before adding an event");
      return;
    }

    if (eventStartTime >= eventEndTime) {
      setError("The event end time must be after its start time");
      return;
    }

    try {
      setIsCreatingEvent(true);

      const newEvent = await createTripEvent(selectedTripId, {
        title: eventTitle.trim(),
        description: eventDescription.trim(),
        startTime: `${selectedDate}T${eventStartTime}:00`,
        endTime: `${selectedDate}T${eventEndTime}:00`,
        timezone: eventTimezone,
      });

      setEvents((currentEvents) => [...currentEvents, newEvent]);
      setEventTitle("");
      setEventDescription("");
      setEventStartTime("");
      setEventEndTime("");
      setEventTimezone("Europe/Vienna");
      setShowEventForm(false);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Failed to create event"
      );
    } finally {
      setIsCreatingEvent(false);
    }
  }

  if (isLoadingTrips) {
    return (
      <main className="itinerary-page">
        <p>Loading trips...</p>
      </main>
    );
  }

  return (
    <main className="itinerary-page">
      <section className="itinerary-header">
        <div>
          <h1>Itinerary</h1>
          <p>Plan your trip day by day.</p>
        </div>

        {trips.length > 0 && (
          <div className="trip-picker">
            <label htmlFor="trip-select">Select trip</label>

            <select
              id="trip-select"
              value={selectedTripId ?? ""}
              onChange={handleTripChange}
            >
              {trips.map((trip) => (
                <option key={trip.id} value={trip.id}>
                  {trip.name}
                </option>
              ))}
            </select>
          </div>
        )}

        <button
          className="primary-action"
          type="button"
          onClick={() => {
            setError("");
            setShowTripForm((isOpen) => !isOpen);
          }}
        >
          {showTripForm ? "Cancel" : "New trip"}
        </button>
      </section>

      {showTripForm && (
        <section className="new-trip-panel">
          <h2>Create a new trip</h2>

          <form className="new-trip-form" onSubmit={handleCreateTrip}>
            <label>
              Trip name
              <input
                type="text"
                value={tripName}
                onChange={(event) => setTripName(event.target.value)}
                required
              />
            </label>

            <label>
              Description
              <textarea
                value={tripDescription}
                onChange={(event) => setTripDescription(event.target.value)}
                rows={3}
              />
            </label>

            <div className="trip-date-fields">
              <label>
                Start date
                <input
                  type="date"
                  value={tripStartDate}
                  onChange={(event) => setTripStartDate(event.target.value)}
                  required
                />
              </label>

              <label>
                End date
                <input
                  type="date"
                  value={tripEndDate}
                  min={tripStartDate || undefined}
                  onChange={(event) => setTripEndDate(event.target.value)}
                  required
                />
              </label>
            </div>

            <button
              className="primary-action"
              type="submit"
              disabled={isCreatingTrip}
            >
              {isCreatingTrip ? "Creating..." : "Create trip"}
            </button>
          </form>
        </section>
      )}

      {trips.length === 0 && !showTripForm && (
        <section className="empty-state trips-empty-state">
          <h2>No trips yet</h2>
          <p>Create your first trip to start planning.</p>
        </section>
      )}

      {selectedTrip && (
        <section className="selected-trip-summary">
          <div>
            <h2>{selectedTrip.name}</h2>

            {selectedTrip.description && (
              <p>{selectedTrip.description}</p>
            )}
          </div>

          <button
            className="primary-action"
            type="button"
            onClick={() => {
              setError("");
              setShowEventForm((isOpen) => !isOpen);
            }}
          >
            {showEventForm ? "Cancel" : "Add event"}
          </button>
        </section>
      )}

      {selectedTrip && (
        <div className="view-toggle" role="group" aria-label="Choose trip view">
          <button
            type="button"
            className={view === "itinerary" ? "active" : ""}
            aria-pressed={view === "itinerary"}
            onClick={() => setView("itinerary")}
          >
            Itinerary
          </button>
          <button
            type="button"
            className={view === "calendar" ? "active" : ""}
            aria-pressed={view === "calendar"}
            onClick={() => setView("calendar")}
          >
            Calendar
          </button>
        </div>
      )}

      {selectedTrip && view === "itinerary" && <section className="day-selector">
        <label htmlFor="day-select">Select day</label>

        <select
          id="day-select"
          value={selectedDate ?? ""}
          onChange={(event) => setSelectedDate(event.target.value)}
        >
          {tripDays.map((date, index) => (
            <option key={date} value={date}>
              {formatDayLabel(date, index)}
            </option>
          ))}
        </select>
      </section>}

      {showEventForm && selectedTrip && selectedDate && (
        <section className="new-event-panel">
          <h2>Add an event</h2>
          <p>{formatDayLabel(selectedDate, tripDays.indexOf(selectedDate))}</p>

          <form className="new-event-form" onSubmit={handleCreateEvent}>
            <label>
              Event title
              <input
                type="text"
                value={eventTitle}
                onChange={(event) => setEventTitle(event.target.value)}
                required
              />
            </label>

            <label>
              Description
              <textarea
                value={eventDescription}
                onChange={(event) => setEventDescription(event.target.value)}
                rows={3}
              />
            </label>

            <div className="event-time-fields">
              <label>
                Start time
                <input
                  type="time"
                  value={eventStartTime}
                  onChange={(event) => setEventStartTime(event.target.value)}
                  required
                />
              </label>

              <label>
                End time
                <input
                  type="time"
                  value={eventEndTime}
                  onChange={(event) => setEventEndTime(event.target.value)}
                  required
                />
              </label>

              <label>
                Timezone
                <input
                  type="text"
                  value={eventTimezone}
                  onChange={(event) => setEventTimezone(event.target.value)}
                  required
                />
              </label>
            </div>

            <button
              className="primary-action"
              type="submit"
              disabled={isCreatingEvent}
            >
              {isCreatingEvent ? "Adding..." : "Add event"}
            </button>
          </form>
        </section>
      )}

      {error && <p className="error-message">{error}</p>}

      {selectedTrip && view === "calendar" && (
        <CalendarDisplay
          embedded
          trips={trips}
          selectedTripId={selectedTripId}
          events={events}
          loading={isLoadingEvents}
          selectedDate={selectedDate}
          onTripSelect={setSelectedTripId}
          onDateSelect={setSelectedDate}
        />
      )}

      {selectedTrip && view === "itinerary" && <section className="itinerary-list">
        <h2>
          {selectedDate
            ? formatDayLabel(
                selectedDate,
                tripDays.indexOf(selectedDate)
              )
            : "Select a day"}
        </h2>

        {isLoadingEvents ? (
          <p>Loading events...</p>
        ) : eventsForSelectedDay.length === 0 ? (
          <p className="empty-state">No events planned for this day.</p>
        ) : (
          eventsForSelectedDay.map((event) => (
            <article className="itinerary-card" key={event.id}>
              <div className="item-time">
                {formatTime(event.startTime)}
              </div>

              <div className="item-details">
                <h3>{event.title}</h3>

                {event.description && <p>{event.description}</p>}

                <p>
                  {formatTime(event.startTime)}–{formatTime(event.endTime)}
                </p>

                <p>{event.timezone}</p>
              </div>

              <div className="item-actions">
                <button type="button">Edit</button>
                <button type="button">Delete</button>
              </div>
            </article>
          ))
        )}
      </section>}
    </main>
  );
}

export default ItineraryPage;
