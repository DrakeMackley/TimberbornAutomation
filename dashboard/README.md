# Timberborn Colony Dashboard

Browser-based real-time colony status monitoring for Timberborn.

## Features

- ✅ Real-time adapter (sensor) monitoring
- ✅ Manual lever control from the dashboard
- ✅ Traffic-light indicators (green = good, red = alert)
- ✅ Filter/search adapters and levers
- ✅ Connection status indicator
- ✅ Pause/resume polling
- ✅ Dark theme with steampunk aesthetic
- ✅ Fully responsive (desktop + mobile)
- ✅ Zero dependencies — pure HTML/CSS/JS

## Usage

1. **Make sure Timberborn is running** with the HTTP API mod enabled

2. **Serve the dashboard:**
   
   Using Python (simplest):
   ```bash
   python3 -m http.server 8000
   ```
   
   Or using Node.js:
   ```bash
   npx serve .
   ```

3. **Open in browser:**
   ```
   http://localhost:8000
   ```

4. The dashboard will:
   - Auto-poll adapters and levers every 5 seconds
   - Show green/red indicators for adapter states
   - Let you toggle levers with a click
   - Filter/search using the text boxes

## Configuration

### API Endpoint
Edit the `API_BASE` constant in `index.html` if your game API is on a different port:

```javascript
const API_BASE = 'http://localhost:8080';
```

### Polling Interval
Adjust `POLL_INTERVAL` (in milliseconds) to poll more or less frequently:

```javascript
const POLL_INTERVAL = 5000; // 5 seconds
```

Lower = more responsive, higher = less API load.

## Features Detail

### Adapters Section
- Lists all HTTP Adapters from the game
- Shows current state (ON = alert/active, OFF = normal)
- Red border = adapter is ON (alerting)
- Green border = adapter is OFF (normal)
- Filter box to search by name

### Levers Section
- Lists all HTTP Levers from the game
- Shows current state with clickable toggle button
- Click to switch lever ON/OFF remotely
- Filter box to search by name

### Connection Status
- Green pulsing dot = connected to game
- Red dot = game not reachable
- Shows last successful update time

### Controls
- **Refresh Now** — manually trigger a poll
- **Pause/Resume** — stop/start auto-polling
- **Configure Categories** — info about filtering

## Tips

- **Filter by purpose:** Use the filter boxes to show only water-related adapters, production levers, etc.
- **Pause during config:** Pause polling while you adjust in-game settings to avoid conflicts
- **Mobile-friendly:** Works on phones/tablets for remote monitoring
- **Multiple tabs:** Open multiple instances filtered to different categories

## Troubleshooting

**"Disconnected" status**
- Verify Timberborn is running
- Check that the HTTP API mod is active
- Confirm the game API is on port 8080 (or update `API_BASE`)

**Levers not responding**
- Make sure the lever name matches exactly (case-sensitive)
- Check that the lever isn't locked by in-game automation

**Dashboard not loading**
- Check browser console for errors (F12)
- Verify you're serving from the dashboard directory
- Make sure you're not opening `index.html` as a file:// URL (use a server)

## Advanced: Remote Access

To access the dashboard from another device on your network:

1. Find your machine's local IP (e.g., `192.168.1.100`)
2. Serve on `0.0.0.0` instead of `localhost`:
   ```bash
   python3 -m http.server 8000 --bind 0.0.0.0
   ```
3. Update the dashboard's `API_BASE` to your machine's IP:
   ```javascript
   const API_BASE = 'http://192.168.1.100:8080';
   ```
4. Access from other device: `http://192.168.1.100:8000`

**Security note:** This exposes the dashboard to your local network. Don't expose to the internet without proper security.
