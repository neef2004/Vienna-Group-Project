//backend trips and calendar events look different from frontend
type BackendTrip = {
    id: number;
    user_id: number;
    name: string;
    description: string | null;
    start_date: string;
    end_date: string;
    created_at: string;
    updated_at: string;
    owner_email?: string;
  };
  
  type BackendCalendarEvent = {
    id: number;
    trip_id: number;
    title: string;
    description: string | null;
    start_time: string;
    end_time: string;
    timezone: string;
    rrule?: string | null;
  };
  
  export type Trip = {
    id: number;
    userId: number;
    name: string;
    description: string | null;
    startDate: string;
    endDate: string;
    createdAt: string;
    updatedAt: string;
    ownerEmail: string | null;
  };
  
  export type CalendarEvent = {
    id: number;
    tripId: number;
    title: string;
    description: string | null;
    startTime: string;
    endTime: string;
    timezone: string;
    rrule: string | null;
  };

  export type CreateTripInput = {
    name: string;
    description: string;
    startDate: string;
    endDate: string;
  };

  export type CreateEventInput = {
    title: string;
    description: string;
    startTime: string;
    endTime: string;
    timezone: string;
  };

  export type UpdateEventInput = CreateEventInput;

  //reusable auth function
  function getAuthToken(): string {
    const token = localStorage.getItem("token");

    if(!token) {
        throw new Error("You must be logged in");
    }
    return token;
  }

  async function authenticatedFetch(
    input: RequestInfo | URL,
    init: RequestInit = {}
  ): Promise<Response> {
    const headers = new Headers(init.headers);
    headers.set("Authorization", `Bearer ${getAuthToken()}`);

    const response = await fetch(input, { ...init, headers });

    if (response.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      sessionStorage.setItem(
        "authMessage",
        "Your session expired. Please log in again."
      );
      window.location.replace("/login");
      throw new Error("Your session expired. Please log in again.");
    }

    return response;
  }

  //maps backend trip response to frontend trip type
  function mapTrip(trip: BackendTrip): Trip {
    return {
        id: trip.id,
        userId: trip.user_id,
        name: trip.name,
        description: trip.description,
        startDate: trip.start_date,
        endDate: trip.end_date,
        createdAt: trip.created_at,
        updatedAt: trip.updated_at,
        ownerEmail: trip.owner_email ?? null,
    };
  }
  //same thing for calendar events
  function mapCalendarEvent(event: BackendCalendarEvent): CalendarEvent {
    return {
      id: event.id,
      tripId: event.trip_id,
      title: event.title,
      description: event.description,
      startTime: event.start_time,
      endTime: event.end_time,
      timezone: event.timezone,
      rrule: event.rrule ?? null,
    };
  }
  //helper function that adds one day to the passed date
  function addOneDay(date: string): string {
    const [year, month, day] = date
      .slice(0, 10)
      .split("-")
      .map(Number);
  
    const result = new Date(Date.UTC(year, month - 1, day));
    result.setUTCDate(result.getUTCDate() + 1);
  
    return result.toISOString().slice(0, 10);
  }

  //makes the api call to get the user's planned trips
  export async function getUserTrips() : Promise<Trip[]> {
    const response = await authenticatedFetch("/api/trips");

    if (!response.ok) {
        throw new Error("failed to load trips");
    }

    const data: BackendTrip[] = await response.json();

    return data.map(mapTrip);
  }

  export async function createTrip(input: CreateTripInput): Promise<Trip> {
    const response = await authenticatedFetch("/api/trips", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: input.name,
        description: input.description || null,
        start_date: `${input.startDate}T00:00:00`,
        end_date: `${input.endDate}T00:00:00`
      })
    });

    if (!response.ok) {
      const data = await response.json().catch(() => null);
      throw new Error(data?.error ?? "Failed to create trip");
    }

    const data: BackendTrip = await response.json();
    return mapTrip(data);
  }

  //gets the trip events for the selected trip
  export async function getTripEvents(
    trip: Trip
  ): Promise<CalendarEvent[]> {
    const startDate = trip.startDate.slice(0, 10);
    const endDate = addOneDay(trip.endDate);
    //to prevent from pulling recurring events outside the trip
    //date range we limit events to the range of the trip
    const query = new URLSearchParams({
        start: `${startDate}T00:00:00`,
        end: `${endDate}T00:00:00`
    });
    const response = await authenticatedFetch(
        `/api/trips/${trip.id}/events?${query.toString()}`,
        {}
    );

    if(!response.ok) {
        throw new Error("failed to load trip events")
    }

    const data: BackendCalendarEvent[] = await response.json();

    return data.map(mapCalendarEvent);
  }

  export async function createTripEvent(
    tripId: number,
    input: CreateEventInput
  ): Promise<CalendarEvent> {
    const response = await authenticatedFetch(`/api/trips/${tripId}/events`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        title: input.title,
        description: input.description || null,
        start_time: input.startTime,
        end_time: input.endTime,
        timezone: input.timezone
      })
    });

    if (!response.ok) {
      const data = await response.json().catch(() => null);
      throw new Error(data?.error ?? "Failed to create event");
    }

    const data: BackendCalendarEvent = await response.json();
    return mapCalendarEvent(data);
  }

  export async function updateTripEvent(
    tripId: number,
    eventId: number,
    input: UpdateEventInput
  ): Promise<CalendarEvent> {
    const response = await authenticatedFetch(
      `/api/trips/${tripId}/events/${eventId}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          title: input.title,
          description: input.description || null,
          start_time: input.startTime,
          end_time: input.endTime,
          timezone: input.timezone
        })
      }
    );

    if (!response.ok) {
      const data = await response.json().catch(() => null);
      throw new Error(data?.error ?? "Failed to update event");
    }

    const data: BackendCalendarEvent = await response.json();
    return mapCalendarEvent(data);
  }

  export async function deleteTripEvent(
    tripId: number,
    eventId: number
  ): Promise<void> {
    const response = await authenticatedFetch(
      `/api/trips/${tripId}/events/${eventId}`,
      { method: "DELETE" }
    );

    if (!response.ok) {
      const data = await response.json().catch(() => null);
      throw new Error(data?.error ?? "Failed to delete event");
    }
  }

  export async function exportTripCalendar(
    trip: Trip
  ): Promise<{ blob: Blob; filename: string }> {
    const response = await authenticatedFetch(
      `/api/trips/${trip.id}/calendar.ics`
    );

    if (!response.ok) {
      const data = await response.json().catch(() => null);
      throw new Error(data?.error ?? "Failed to export calendar");
    }

    const disposition = response.headers.get("Content-Disposition");
    const headerFilename = disposition?.match(/filename="?([^"]+)"?/i)?.[1];
    const fallbackName = `${trip.name.replace(/[^\w -]/g, "").trim() || "trip"}.ics`;

    return {
      blob: await response.blob(),
      filename: headerFilename ?? fallbackName,
    };
  }
