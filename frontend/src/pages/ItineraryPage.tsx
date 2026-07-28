import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  createTripEvent,
  createTrip,
  deleteTripEvent,
  getTripEvents,
  getUserTrips,
  updateTripEvent,
  type CalendarEvent,
  type Trip,
} from "../api/trips";
import { signOut } from "../api/auth";
import {
  acceptInvitation,
  getCollaborators,
  inviteCollaborator,
  removeCollaborator,
  updateCollaboratorPermission,
  type Collaborator,
  type CollaboratorPermission,
} from "../api/collaborate";
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

function getCurrentUserId(): number | null {
  try {
    const user = JSON.parse(localStorage.getItem("user") ?? "null") as {
      id?: number;
    } | null;
    return user?.id ?? null;
  } catch {
    return null;
  }
}

function ItineraryPage() {
  const navigate = useNavigate();
  const [trips, setTrips] = useState<Trip[]>([]);
  const [selectedTripId, setSelectedTripId] = useState<number | null>(null);
  const [view, setView] = useState<"itinerary" | "calendar">("itinerary");

  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  const [isLoadingTrips, setIsLoadingTrips] = useState(true);
  const [isLoadingEvents, setIsLoadingEvents] = useState(false);
  const [isCreatingTrip, setIsCreatingTrip] = useState(false);
  const [isCreatingEvent, setIsCreatingEvent] = useState(false);
  const [editingEventId, setEditingEventId] = useState<number | null>(null);
  const [deletingEventId, setDeletingEventId] = useState<number | null>(null);
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [showTripForm, setShowTripForm] = useState(false);
  const [showEventForm, setShowEventForm] = useState(false);
  const [showCollaboration, setShowCollaboration] = useState(false);
  const [collaborators, setCollaborators] = useState<Collaborator[]>([]);
  const [collaboratorEmail, setCollaboratorEmail] = useState("");
  const [collaboratorPermission, setCollaboratorPermission] =
    useState<CollaboratorPermission>("editor");
  const [isLoadingCollaborators, setIsLoadingCollaborators] = useState(false);
  const [isInvitingCollaborator, setIsInvitingCollaborator] = useState(false);
  const [collaborationMessage, setCollaborationMessage] = useState("");
  const [invitationLink, setInvitationLink] = useState("");
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
    const inviteValue = new URLSearchParams(window.location.search).get("invite");
    const inviteTripId = Number(inviteValue);

    if (!Number.isInteger(inviteTripId) || inviteTripId <= 0) {
      return;
    }

    if (!localStorage.getItem("token")) {
      const invitationPath = `/itinerary?invite=${encodeURIComponent(inviteValue ?? "")}`;
      sessionStorage.setItem("redirectAfterLogin", invitationPath);
      navigate(`/login?redirect=${encodeURIComponent(invitationPath)}`, {
        replace: true,
      });
      return;
    }

    async function acceptSharedTrip() {
      try {
        setError("");
        await acceptInvitation(inviteTripId);
        const loadedTrips = await getUserTrips();
        setTrips(loadedTrips);
        setSelectedTripId(inviteTripId);
        setCollaborationMessage("Trip invitation accepted.");
        window.history.replaceState({}, "", "/itinerary");
      } catch (error) {
        setError(
          error instanceof Error
            ? error.message
            : "Failed to accept trip invitation"
        );
      }
    }

    acceptSharedTrip();
  }, [navigate]);

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
    resetEventForm();
    setShowCollaboration(false);
    setCollaborationMessage("");
    setSelectedTripId(Number(event.target.value));
  }

  async function loadCollaborators(tripId: number) {
    try {
      setIsLoadingCollaborators(true);
      setError("");
      setCollaborators(await getCollaborators(tripId));
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to load collaborators"
      );
    } finally {
      setIsLoadingCollaborators(false);
    }
  }

  async function handleInviteCollaborator(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!selectedTrip) {
      return;
    }

    try {
      setIsInvitingCollaborator(true);
      setError("");
      setCollaborationMessage("");
      await inviteCollaborator(
        selectedTrip.id,
        collaboratorEmail,
        collaboratorPermission
      );
      const invitationUrl = new URL("/itinerary", window.location.origin);
      invitationUrl.searchParams.set("invite", String(selectedTrip.id));
      setCollaboratorEmail("");
      setInvitationLink(invitationUrl.toString());
      setCollaborationMessage(
        "Invitation created for that account. Send them the link below."
      );
      await loadCollaborators(selectedTrip.id);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to invite collaborator"
      );
    } finally {
      setIsInvitingCollaborator(false);
    }
  }

  async function handlePermissionChange(
    collaborator: Collaborator,
    permission: CollaboratorPermission
  ) {
    try {
      setError("");
      await updateCollaboratorPermission(
        collaborator.tripId,
        collaborator.userId,
        permission
      );
      setCollaborators((current) =>
        current.map((item) =>
          item.id === collaborator.id
            ? { ...item, permissionLevel: permission }
            : item
        )
      );
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Failed to update permission"
      );
    }
  }

  async function handleRemoveCollaborator(collaborator: Collaborator) {
    if (!window.confirm(`Remove ${collaborator.email} from this trip?`)) {
      return;
    }

    try {
      setError("");
      await removeCollaborator(collaborator.tripId, collaborator.userId);
      setCollaborators((current) =>
        current.filter((item) => item.id !== collaborator.id)
      );
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Failed to remove collaborator"
      );
    }
  }

  async function handleCopyInvitationLink() {
    if (!invitationLink) {
      return;
    }

    try {
      await navigator.clipboard.writeText(invitationLink);
      setCollaborationMessage("Invitation link copied.");
    } catch {
      setError("Unable to copy the invitation link.");
    }
  }

  function handleCalendarTripSelect(tripId: number) {
    resetEventForm();
    setSelectedTripId(tripId);
  }

  function resetEventForm() {
    setEventTitle("");
    setEventDescription("");
    setEventStartTime("");
    setEventEndTime("");
    setEventTimezone("Europe/Vienna");
    setEditingEventId(null);
    setShowEventForm(false);
  }

  function handleEditEvent(calendarEvent: CalendarEvent) {
    setError("");
    setEditingEventId(calendarEvent.id);
    setEventTitle(calendarEvent.title);
    setEventDescription(calendarEvent.description ?? "");
    setEventStartTime(formatTime(calendarEvent.startTime));
    setEventEndTime(formatTime(calendarEvent.endTime));
    setEventTimezone(calendarEvent.timezone);
    setSelectedDate(calendarEvent.startTime.slice(0, 10));
    setShowEventForm(true);
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

      const eventInput = {
        title: eventTitle.trim(),
        description: eventDescription.trim(),
        startTime: `${selectedDate}T${eventStartTime}:00`,
        endTime: `${selectedDate}T${eventEndTime}:00`,
        timezone: eventTimezone,
      };

      if (editingEventId === null) {
        const newEvent = await createTripEvent(selectedTripId, eventInput);
        setEvents((currentEvents) => [...currentEvents, newEvent]);
      } else {
        const updatedEvent = await updateTripEvent(
          selectedTripId,
          editingEventId,
          eventInput
        );
        setEvents((currentEvents) =>
          currentEvents.map((currentEvent) =>
            currentEvent.id === updatedEvent.id ? updatedEvent : currentEvent
          )
        );
      }

      resetEventForm();
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : editingEventId === null
            ? "Failed to create event"
            : "Failed to update event"
      );
    } finally {
      setIsCreatingEvent(false);
    }
  }

  async function handleDeleteEvent(calendarEvent: CalendarEvent) {
    if (
      !window.confirm(`Delete "${calendarEvent.title}"? This cannot be undone.`)
    ) {
      return;
    }

    try {
      setDeletingEventId(calendarEvent.id);
      setError("");
      await deleteTripEvent(calendarEvent.tripId, calendarEvent.id);
      setEvents((currentEvents) =>
        currentEvents.filter((event) => event.id !== calendarEvent.id)
      );

      if (editingEventId === calendarEvent.id) {
        resetEventForm();
      }
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Failed to delete event"
      );
    } finally {
      setDeletingEventId(null);
    }
  }

  async function handleSignOut() {
    try {
      setIsSigningOut(true);
      setError("");
      await signOut();
      navigate("/login", { replace: true });
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Failed to sign out"
      );
      setIsSigningOut(false);
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
      <nav className="itinerary-nav">
        <button
          className="brand"
          type="button"
          aria-label="Back to ItineFairy home"
          onClick={() => navigate("/")}
        >
          <span className="brand-mark" aria-hidden="true">✦</span>
          <span>itineFairy</span>
        </button>
        <div className="itinerary-nav-actions">
          <span className="itinerary-nav-note">Your travel workspace</span>
          <button
            className="sign-out-button"
            type="button"
            onClick={handleSignOut}
            disabled={isSigningOut}
          >
            {isSigningOut ? "Signing out..." : "Sign out"}
          </button>
        </div>
      </nav>

      <section className="itinerary-header">
        <div>
          <span className="section-kicker">✦ Trip planner</span>
          <h1>Your itinerary</h1>
          <p>Every detail, beautifully organized.</p>
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
                  {trip.userId === getCurrentUserId() || !trip.ownerEmail
                    ? trip.name
                    : `${trip.name} -- ${trip.ownerEmail}`}
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

          <div className="trip-summary-actions">
            <button
              className="secondary-action"
              type="button"
              aria-expanded={showCollaboration}
              onClick={() => {
                const willOpen = !showCollaboration;
                setError("");
                setCollaborationMessage("");
                setInvitationLink("");
                setShowCollaboration(willOpen);
                if (willOpen) {
                  loadCollaborators(selectedTrip.id);
                }
              }}
            >
              {showCollaboration ? "Close" : "Collaborate"}
            </button>
            <button
              className="primary-action"
              type="button"
              onClick={() => {
                setError("");
                if (showEventForm) {
                  resetEventForm();
                } else {
                  setEditingEventId(null);
                  setShowEventForm(true);
                }
              }}
            >
              {showEventForm ? "Cancel" : "Add event"}
            </button>
          </div>
        </section>
      )}

      {selectedTrip && showCollaboration && (
        <section className="collaboration-panel">
          <div>
            <h2>Collaborate on this trip</h2>
            <p>
              Invite an existing itineFairy account to the entire trip.
            </p>
          </div>

          <form
            className="collaboration-form"
            onSubmit={handleInviteCollaborator}
          >
            <label>
              Account email
              <input
                type="email"
                value={collaboratorEmail}
                onChange={(event) => setCollaboratorEmail(event.target.value)}
                placeholder="traveller@example.com"
                required
              />
            </label>
            <label>
              Permission
              <select
                value={collaboratorPermission}
                onChange={(event) =>
                  setCollaboratorPermission(
                    event.target.value as CollaboratorPermission
                  )
                }
              >
                <option value="editor">Can edit</option>
                <option value="viewer">View only</option>
              </select>
            </label>
            <button
              className="primary-action"
              type="submit"
              disabled={isInvitingCollaborator}
            >
              {isInvitingCollaborator ? "Inviting..." : "Invite"}
            </button>
          </form>

          {collaborationMessage && (
            <p className="collaboration-message">{collaborationMessage}</p>
          )}
          {invitationLink && (
            <div className="invitation-link">
              <input
                aria-label="Invitation link"
                type="text"
                value={invitationLink}
                readOnly
                onFocus={(event) => event.target.select()}
              />
              <button
                className="copy-invitation-button"
                type="button"
                onClick={handleCopyInvitationLink}
              >
                Copy link
              </button>
            </div>
          )}

          <div className="collaborator-list">
            <h3>Invited collaborators</h3>
            {isLoadingCollaborators && <p>Loading collaborators...</p>}
            {!isLoadingCollaborators && collaborators.length === 0 && (
              <p>No collaborators have been invited yet.</p>
            )}
            {collaborators.map((collaborator) => (
              <div className="collaborator-row" key={collaborator.id}>
                <div>
                  <strong>{collaborator.email}</strong>
                  <span>
                    {collaborator.accepted ? "Accepted" : "Pending"}
                  </span>
                </div>
                <select
                  aria-label={`Permission for ${collaborator.email}`}
                  value={collaborator.permissionLevel}
                  onChange={(event) =>
                    handlePermissionChange(
                      collaborator,
                      event.target.value as CollaboratorPermission
                    )
                  }
                >
                  <option value="editor">Can edit</option>
                  <option value="viewer">View only</option>
                </select>
                <button
                  className="remove-collaborator-button"
                  type="button"
                  onClick={() => handleRemoveCollaborator(collaborator)}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
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
          <h2>{editingEventId === null ? "Add an event" : "Edit event"}</h2>
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
              {isCreatingEvent
                ? editingEventId === null
                  ? "Adding..."
                  : "Saving..."
                : editingEventId === null
                  ? "Add event"
                  : "Save changes"}
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
          onTripSelect={handleCalendarTripSelect}
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
                <button
                  type="button"
                  onClick={() => handleEditEvent(event)}
                  disabled={deletingEventId === event.id}
                >
                  Edit
                </button>
                <button
                  className="delete-event-button"
                  type="button"
                  onClick={() => handleDeleteEvent(event)}
                  disabled={deletingEventId === event.id}
                >
                  {deletingEventId === event.id ? "Deleting..." : "Delete"}
                </button>
              </div>
            </article>
          ))
        )}
      </section>}
    </main>
  );
}

export default ItineraryPage;
