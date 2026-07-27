import { useEffect, useMemo, useState } from "react";
import {
  exportTripCalendar,
  getTripEvents,
  getUserTrips,
  type CalendarEvent,
  type Trip,
} from "../api/trips";
import CalendarGrid from "./CalendarGrid";
import "../styles/CalendarDisplay.css";

type CalendarDisplayProps = {
  trips?: Trip[];
  selectedTripId?: number | null;
  events?: CalendarEvent[];
  loading?: boolean;
  error?: string;
  embedded?: boolean;
  selectedDate?: string | null;
  onTripSelect?: (tripId: number) => void;
  onDateSelect?: (date: string) => void;
};

export default function CalendarDisplay({
  trips: suppliedTrips,
  selectedTripId: suppliedSelectedTripId,
  events: suppliedEvents,
  loading: suppliedLoading,
  error: suppliedError,
  embedded = false,
  selectedDate,
  onTripSelect,
  onDateSelect,
}: CalendarDisplayProps) {
  const [loadedTrips, setLoadedTrips] = useState<Trip[]>([]);
  const [internalSelectedTripId, setInternalSelectedTripId] = useState<
    number | null
  >(null);
  const [loadedEvents, setLoadedEvents] = useState<CalendarEvent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [exportError, setExportError] = useState("");

  const isControlled = suppliedTrips !== undefined;
  const trips = suppliedTrips ?? loadedTrips;
  const selectedTripId =
    suppliedSelectedTripId !== undefined
      ? suppliedSelectedTripId
      : internalSelectedTripId;
  const events = suppliedEvents ?? loadedEvents;
  const loading = suppliedLoading ?? isLoading;
  const error = suppliedError ?? loadError;

  const selectedTrip = useMemo(
    () => trips.find((trip) => trip.id === selectedTripId) ?? null,
    [trips, selectedTripId]
  );

  useEffect(() => {
    if (isControlled) {
      return;
    }

    let requestCancelled = false;

    async function loadTrips() {
      try {
        setIsLoading(true);
        setLoadError("");
        const data = await getUserTrips();

        if (!requestCancelled) {
          setLoadedTrips(data);
          setInternalSelectedTripId(data[0]?.id ?? null);
        }
      } catch (error) {
        if (!requestCancelled) {
          setLoadError(
            error instanceof Error ? error.message : "Failed to load trips"
          );
        }
      } finally {
        if (!requestCancelled) {
          setIsLoading(false);
        }
      }
    }

    loadTrips();

    return () => {
      requestCancelled = true;
    };
  }, [isControlled]);

  useEffect(() => {
    if (isControlled || !selectedTrip) {
      if (!isControlled) {
        setLoadedEvents([]);
      }
      return;
    }

    const trip = selectedTrip;
    let requestCancelled = false;

    async function loadEvents() {
      try {
        setIsLoading(true);
        setLoadError("");
        const data = await getTripEvents(trip);

        if (!requestCancelled) {
          setLoadedEvents(data);
        }
      } catch (error) {
        if (!requestCancelled) {
          setLoadedEvents([]);
          setLoadError(
            error instanceof Error
              ? error.message
              : "Failed to load trip events"
          );
        }
      } finally {
        if (!requestCancelled) {
          setIsLoading(false);
        }
      }
    }

    loadEvents();

    return () => {
      requestCancelled = true;
    };
  }, [isControlled, selectedTrip]);

  function handleTripSelect(value: string) {
    const tripId = Number(value);

    if (onTripSelect) {
      onTripSelect(tripId);
    } else {
      setInternalSelectedTripId(tripId);
    }
  }

  async function handleExport() {
    if (!selectedTrip) {
      return;
    }

    try {
      setIsExporting(true);
      setExportError("");
      const { blob, filename } = await exportTripCalendar(selectedTrip);
      const downloadUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      setExportError(
        error instanceof Error ? error.message : "Failed to export calendar"
      );
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <section className={`calendar-page${embedded ? " calendar-embedded" : ""}`}>
      {!embedded && <h1>Trip calendar</h1>}

      {!embedded && trips.length > 0 && (
        <label className="calendar-trip-picker">
          Select trip
          <select
            value={selectedTripId ?? ""}
            onChange={(event) => handleTripSelect(event.target.value)}
          >
            {trips.map((trip) => (
              <option key={trip.id} value={trip.id}>
                {trip.name}
              </option>
            ))}
          </select>
        </label>
      )}

      {loading && <p className="loading-state">Loading calendar...</p>}
      {error && <p className="error-state">{error}</p>}

      {!loading && !error && trips.length === 0 && (
        <p className="empty-state">Create a trip to view its calendar.</p>
      )}

      {!loading && selectedTrip && (
        <>
          <CalendarGrid
            events={events}
            initialDate={selectedTrip.startDate}
            selectedDate={selectedDate}
            minDate={selectedTrip.startDate}
            maxDate={selectedTrip.endDate}
            onDateSelect={onDateSelect}
          />

          <div className="calendar-export">
            <button
              type="button"
              className="calendar-export-button"
              disabled={isExporting}
              onClick={handleExport}
            >
              {isExporting ? "Exporting..." : "Export calendar (.ics)"}
            </button>
            {exportError && <p className="error-state">{exportError}</p>}
          </div>
        </>
      )}
    </section>
  );
}
