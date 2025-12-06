# NYC Subway Real-Time API Server

A simple Python 3 Flask server that connects to the NYC MTA real-time subway API.

## Requirements

- Python 3.9 or higher
- pip (Python package manager)

## Setup

### 1. Install Dependencies

```bash
# Using pip3 to ensure Python 3
pip3 install -r requirements.txt

# Or use python3 -m pip
python3 -m pip install -r requirements.txt
```

### 2. (Optional) Configure API Key

The MTA API may work without an API key. If you encounter authentication errors, you can optionally set up an API key:

1. Visit the [MTA Developer Portal](https://api.mta.info/)
2. Sign up for a free account and create an API key
3. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` and add your API key:
   ```
   MTA_API_KEY=your_actual_api_key_here
   ```

### 3. Run the Server

```bash
# Using python3
python3 app.py

# Or make the file executable and run directly
chmod +x app.py
./app.py
```

The server will start on `http://localhost:8000`

**Note:** We use port 8000 instead of 5000 because macOS AirPlay Receiver uses port 5000 by default.

## API Endpoints

### GET `/`
Returns information about available endpoints.

### GET `/subway/feeds`
Returns a list of available MTA feed IDs and the subway lines they cover.

**Example Response:**
```json
{
  "1": "Subway lines: 1, 2, 3, 4, 5, 6, S",
  "2": "Subway lines: A, C, E",
  "11": "Subway lines: B, D, F, M"
}
```

### GET `/subway/feed/<feed_id>`
Get real-time subway data for a specific feed.

**Example:**
```bash
curl http://localhost:8000/subway/feed/1
```

**Example Response:**
```json
{
  "feed_id": "1",
  "timestamp": 1234567890,
  "trips": [
    {
      "trip_id": "123456_1..N",
      "route_id": "1",
      "start_date": "20250123",
      "stop_time_updates": [
        {
          "stop_id": "101N",
          "arrival_time": 1234567890,
          "departure_time": 1234567900
        }
      ]
    }
  ]
}
```

## Feed IDs

- **1**: Lines 1, 2, 3, 4, 5, 6, S
- **2**: Lines A, C, E
- **11**: Lines B, D, F, M
- **16**: Lines N, Q, R, W
- **21**: Line G
- **26**: Lines J, Z
- **31**: Line L
- **36**: Line 7

## Notes

- The MTA API returns data in GTFS-realtime format (Protocol Buffers)
- Times are returned as Unix timestamps
- The server automatically parses the binary format into JSON
# nyc-subway-tracker
# nyc-subway-tracker
# nyc-subway-tracker
# nyc-subway-tracker
# nyc-subway-tracker
