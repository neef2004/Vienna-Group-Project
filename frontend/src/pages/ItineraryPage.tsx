import { useState } from "react";

/*
  This type describes a trip option in the dropdown.

  We only have one fake trip right now, but using an array still makes sense
  because the backend will probably return a list of trips later.
*/
type TripOption = {
  id: number;
  name: string;
};

/*
  This type describes one itinerary item.

  Each itinerary item has a tripId so that later, when there are multiple
  trips from the backend, we can show only the items for the selected trip.
*/
type ItineraryItem = {
  id: number;
  tripId: number;
  dayNumber: number;
  time: string;
  title: string;
  category: string;
  location: string;
  durationMinutes: number;
  notes: string;
};

/*
  Fake trip dropdown data.

  Later this could be replaced with a backend call such as:
  GET /api/trips
*/
const fakeTripOptions: TripOption[] = [
  {
    id: 1,
    name: "Vienna Trip",
  },
];

/*
  Fake itinerary items.

  Later this could be replaced with a backend call such as:
  GET /api/trips/:tripId/itinerary
*/
const fakeItineraryItems: ItineraryItem[] = [
  {
    id: 1,
    tripId: 1,
    dayNumber: 1,
    time: "09:00",
    title: "Breakfast near Stephansplatz",
    category: "Food",
    location: "Stephansplatz, Vienna",
    durationMinutes: 60,
    notes: "Start the day with coffee and pastries.",
  },
  {
    id: 2,
    tripId: 1,
    dayNumber: 1,
    time: "10:30",
    title: "Visit St. Stephen's Cathedral",
    category: "Sightseeing",
    location: "Stephansplatz 3, Vienna",
    durationMinutes: 90,
    notes: "Walk around the cathedral and nearby streets.",
  },
  {
    id: 3,
    tripId: 1,
    dayNumber: 2,
    time: "11:00",
    title: "Schonbrunn Palace",
    category: "Activity",
    location: "Schonbrunner Schlosstrasse 47, Vienna",
    durationMinutes: 180,
    notes: "Leave extra time for the gardens.",
  },
];

function ItineraryPage() {
  /*
    selectedTripId stores which trip is selected in the dropdown.

    fakeTripOptions[0].id means:
    "Use the id of the first fake trip as the starting value."
  */
  const [selectedTripId, setSelectedTripId] = useState(fakeTripOptions[0].id);

  /*
    selectedDay stores which itinerary day the user is viewing.

    This is separate from selectedTripId because choosing a trip and choosing
    a day are two different pieces of page state.
  */
  const [selectedDay, setSelectedDay] = useState(1);

  /*
    We only have one fake trip right now, but find() keeps the code shaped
    like it will be when the backend gives us multiple trips.

    find() returns the first trip where trip.id matches selectedTripId.
  */
  const selectedTrip = fakeTripOptions.find(
    (trip) => trip.id === selectedTripId
  );

  /*
    This is a temporary hardcoded number of days.

    Later, the backend may provide trip dates or a totalDays field.
    Then we can calculate or load this instead of hardcoding 5.
  */
  const totalTripDays = 5;

  /*
    Array.from creates a new array.

    { length: totalTripDays } tells it how many items to make.

    The second argument is a function that decides what each item should be.
    index starts at 0, so index + 1 gives us:
    [1, 2, 3, 4, 5]
  */
  const tripDays = Array.from(
    { length: totalTripDays },
    (_, index) => index + 1
  );

  /*
    If selectedTrip is missing, show a simple fallback.

    This should not happen with our fake data, but TypeScript knows that
    find() can return undefined, so this keeps the component safe.
  */
  if (!selectedTrip) {
    return (
      <main className="itinerary-page">
        <h1>Itinerary</h1>
        <p>Trip not found.</p>
      </main>
    );
  }

  /*
    This filters itinerary items to show only items for:
    - the currently selected trip
    - the currently selected day
  */
  const itemsForSelectedTripAndDay = fakeItineraryItems.filter(
    (item) =>
      item.tripId === selectedTripId && item.dayNumber === selectedDay
  );

  /*
    This sorts the selected items by time.

    We copy the array first with [...itemsForSelectedTripAndDay] because
    sort() changes the array it is called on.

    localeCompare compares strings. Since our times are formatted like
    "09:00" and "14:30", string sorting works correctly.
  */
  const sortedItems = [...itemsForSelectedTripAndDay].sort((a, b) =>
    a.time.localeCompare(b.time)
  );

  /*
    This function runs when the user chooses a trip from the dropdown.

    React.ChangeEvent<HTMLSelectElement> tells TypeScript:
    "This event came from a select dropdown."
  */
  function handleTripChange(event: React.ChangeEvent<HTMLSelectElement>) {
    /*
      event.target.value comes from the selected <option>.

      Browser form values are strings, even if the value looks like a number.
      Number(...) converts it into a number so it matches our trip id type.
    */
    const tripIdFromDropdown = Number(event.target.value);

    setSelectedTripId(tripIdFromDropdown);

    /*
      Reset to Day 1 whenever the selected trip changes.

      This will matter more later when different trips may have different
      numbers of days.
    */
    setSelectedDay(1);
  }

  return (
    <main className="itinerary-page">
      <section className="itinerary-header">
        <div>
          <h1>Itinerary</h1>
          <p>Plan your trip day by day.</p>
        </div>

        <div className="trip-picker">
          <label htmlFor="trip-select">Select trip</label>

          <select
            id="trip-select"
            value={selectedTripId}
            onChange={handleTripChange}
          >
            {fakeTripOptions.map((trip) => (
              <option key={trip.id} value={trip.id}>
                {trip.name}
              </option>
            ))}
          </select>
        </div>

        <button className="primary-action" type="button">Add item</button>
      </section>

      <section className="selected-trip-summary">
        <h2>{selectedTrip.name}</h2>
      </section>

      <section className="day-selector">
        {tripDays.map((day) => (
          <button
            className={day === selectedDay ? "day-button active" : "day-button"}
            key={day}
            type="button"
            onClick={() => setSelectedDay(day)}
          >
            Day {day}
          </button>
        ))}
      </section>

      <section className="itinerary-list">
        <h2>Day {selectedDay}</h2>

        {sortedItems.length === 0 ? (
          <p className="empty-state">No plans yet for this day.</p>
        ) : (
          sortedItems.map((item) => (
            <article className="itinerary-card" key={item.id}>
              <div className="item-time">{item.time}</div>

              <div className="item-details">
                <div className="item-title-row">
                  <h3>{item.title}</h3>
                  <span>{item.category}</span>
                </div>

                <p>{item.location}</p>
                <p>{item.durationMinutes} minutes</p>
                <p>{item.notes}</p>
              </div>

              <div className="item-actions">
                <button type="button">Edit</button>
                <button type="button">Delete</button>
              </div>
            </article>
          ))
        )}
      </section>
    </main>
  );
}

export default ItineraryPage;
