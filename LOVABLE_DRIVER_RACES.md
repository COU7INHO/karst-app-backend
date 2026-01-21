# Add Driver Race History to Driver Detail Page

## Feature Request

On the Driver detail page (when clicking a driver), add a new section below the existing stats (Total Races, Total Laps, View Evolution, Compare) that shows **all races where this driver participated**.

## Backend API

The backend now supports filtering races by driver:

**Endpoint:** `GET /api/races/?driver={driver_id}`

**Example:** `GET /api/races/?driver=1`

**Response:**
```json
[
  {
    "id": 1,
    "date": "2024-01-15",
    "circuit": {
      "id": 1,
      "name": "Circuit Name"
    },
    "total_participants": 8
  },
  {
    "id": 2,
    "date": "2024-01-10",
    "circuit": {
      "id": 1,
      "name": "Circuit Name"
    },
    "total_participants": 6
  }
]
```

## Frontend Implementation

1. **Add a new section** in the Driver detail page below the existing buttons
2. **Section title:** "Race History" or "Races Participated"
3. **Fetch data** using the endpoint `/api/races/?driver={driver_id}` when the page loads
4. **Display the races** in a table or card list with:
   - Race Date (formatted nicely)
   - Circuit Name
   - Total Participants
   - A "View Details" link/button that navigates to the race detail page
5. **Sort by date** (most recent first - already comes sorted from backend)
6. **Show loading state** while fetching
7. **Show empty state** if driver has no races ("No races found for this driver")
8. **Error handling** if the API call fails

## UI Suggestions

- Use a Card or Table component (whatever fits the existing design)
- Make it clickable - clicking a race should navigate to that race's detail page
- Include a small icon or badge showing the number of races
- Consider pagination or "show more" if there are many races (optional for now)

## Example Layout

```
[Driver Name Header]

Total Races: X | Total Laps: Y
[View Evolution] [Compare]

--- New Section Below ---

Race History (X races)
┌─────────────────────────────────────────┐
│ 15 Jan 2024 | Circuit ABC | 8 drivers  │→
│ 10 Jan 2024 | Circuit XYZ | 6 drivers  │→
│ 05 Jan 2024 | Circuit ABC | 7 drivers  │→
└─────────────────────────────────────────┘
```

Please implement this feature maintaining the current design style and UX patterns.

Thanks!
