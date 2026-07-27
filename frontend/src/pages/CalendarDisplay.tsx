import { useEffect, useState } from "react";
import CalendarGrid from "../pages/CalendarGrid.tsx"
import "../styles/CalendarDisplay.css";

interface Trip {
  id: number;
  name: string;
}

interface TripEvent {
  id: number;
  title: string;
  description?: string;
  startDateTime: string;
}

export default function CalendarPage() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [selectedTrip, setSelectedTrip] = useState("");
  const [events, setEvents] = useState<TripEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadTrips();
  }, []);

  async function loadTrips() {
    try {
      setLoading(true);

      const response = await fetch("/api/trips");
      const data = await response.json();

      setTrips(data);
    } catch {
      setError("Failed to load trips.");
    } finally {
      setLoading(false);
    }
  }

  async function handleTripSelect(tripId: string) {
    setSelectedTrip(tripId);

    try {
      setLoading(true);

      const response = await fetch(`/api/trips/${tripId}/events`);
      const data = await response.json();

      data.sort(
        (a: TripEvent, b: TripEvent) =>
          new Date(a.startDateTime).getTime() -
          new Date(b.startDateTime).getTime()
      );

      setEvents(data);
    } catch {
      setError("Failed to load events.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="calendar-page">
      <h1>ItineFairy Trip Planner</h1>

      <select
        value={selectedTrip}
        onChange={(e) => handleTripSelect(e.target.value)}
      >
        <option value="">Select a trip</option>

        {trips.map((trip) => (
          <option key={trip.id} value={trip.id}>
            {trip.name}
          </option>
        ))}
      </select>

      {loading && <p>Loading...</p>}

      {error && <p>{error}</p>}

      {!loading && (
        <CalendarGrid events={events} />
      )}
    </div>
  );
}