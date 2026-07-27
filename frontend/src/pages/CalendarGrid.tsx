import { useState } from "react";

interface Event {
  id: number;
  title: string;
  startDateTime: string;
}

interface Props {
  events: Event[];
}

export default function CalendarGrid({ events }: Props) {
  const [currentDate, setCurrentDate] = useState(new Date());

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);

  const daysInMonth = lastDay.getDate();
  const startWeekday = firstDay.getDay();

  const cells = [];

  // Empty cells before the first day of the month
  for (let i = 0; i < startWeekday; i++) {
    cells.push(
      <div
        key={`empty-${i}`}
        className="day-cell empty"
      />
    );
  }

  // Create day cells
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${year}-${String(month + 1).padStart(
      2,
      "0"
    )}-${String(day).padStart(2, "0")}`;

    const dayEvents = events
      .filter((event) =>
        event.startDateTime.startsWith(dateStr)
      )
      .sort(
        (a, b) =>
          new Date(a.startDateTime).getTime() -
          new Date(b.startDateTime).getTime()
      );

    cells.push(
      <div key={day} className="day-cell">
        <div className="day-number">{day}</div>

        {dayEvents.length > 0 ? (
          dayEvents.map((event) => (
            <div
              key={event.id}
              className="event-card"
            >
              <small>
                {new Date(
                  event.startDateTime
                ).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </small>

              <div>{event.title}</div>
            </div>
          ))
        ) : (
          <div className="empty-text">
            No events
          </div>
        )}
      </div>
    );
  }

  return (
    <>
      <div className="calendar-header">
        <button
          onClick={() =>
            setCurrentDate(
              new Date(year, month - 1, 1)
            )
          }
        >
          Previous
        </button>

        <h2>
          {currentDate.toLocaleString("default", {
            month: "long",
            year: "numeric",
          })}
        </h2>

        <button
          onClick={() =>
            setCurrentDate(
              new Date(year, month + 1, 1)
            )
          }
        >
          Next
        </button>
      </div>

      <div className="weekday-row">
        <div>Sun</div>
        <div>Mon</div>
        <div>Tue</div>
        <div>Wed</div>
        <div>Thu</div>
        <div>Fri</div>
        <div>Sat</div>
      </div>

      <div className="calendar-grid">
        {cells}
      </div>
    </>
      );
  }