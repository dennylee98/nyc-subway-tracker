#!/usr/bin/env python3
"""NYC Subway Real-Time API Server - Python 3.12"""

from flask import Flask, jsonify, request, render_template
import os
from datetime import datetime
from dotenv import load_dotenv
from nyct_gtfs import NYCTFeed

load_dotenv()

app = Flask(__name__)

# NYC MTA API endpoint
MTA_API_KEY = os.getenv('MTA_API_KEY', '')

# Feed mapping for nyct-gtfs library
FEED_MAPPING = {
    '1': '1',
    '2': 'A',
    '11': 'B',
    '16': 'N',
    '21': 'G',
    '26': 'J',
    '31': 'L',
    '36': '7'
}

@app.route('/')
def home():
    return jsonify({
        'message': 'NYC Subway Real-Time API',
        'endpoints': {
            '/subway/feeds': 'Get available subway feeds',
            '/subway/feed/<feed_id>': 'Get real-time data for a specific feed',
            '/arrivals': 'View live arrivals page (auto-refreshing)'
        }
    })

@app.route('/arrivals')
def arrivals_page():
    return render_template('arrivals.html')

@app.route('/subway/feeds')
def get_feeds():
    """Return available MTA feed IDs"""
    feeds = {
        '1': 'Subway lines: 1, 2, 3, 4, 5, 6, S',
        '2': 'Subway lines: A, C, E',
        '11': 'Subway lines: B, D, F, M',
        '16': 'Subway lines: N, Q, R, W',
        '21': 'Subway lines: G',
        '26': 'Subway lines: J, Z',
        '31': 'Subway lines: L',
        '36': 'Subway lines: 7'
    }
    return jsonify(feeds)

@app.route('/subway/feed/<feed_id>')
def get_subway_feed(feed_id):
    """Get real-time subway data for a specific feed"""
    try:
        # Get optional filters from query parameters
        route_filter = request.args.get('route')
        direction_filter = request.args.get('direction')  # N for northbound, S for southbound
        stop_filter = request.args.get('stop')
        travel_time = request.args.get('travel_time', type=int)  # Minutes to reach the station

        # Check if feed_id is valid
        if feed_id not in FEED_MAPPING:
            return jsonify({'error': f'Invalid feed_id: {feed_id}'}), 400

        # Get the feed using nyct-gtfs
        feed = NYCTFeed(FEED_MAPPING[feed_id])

        # Convert to JSON-friendly format
        arrivals = [] if stop_filter else None
        arrivals_with_timestamp = [] if stop_filter else None
        trips = []

        for train in feed.trips:
            # Filter by route if specified
            if route_filter and train.route_id != route_filter:
                continue

            # Filter by direction if specified (N = North, S = South)
            if direction_filter and train.direction != direction_filter:
                continue

            trip_data = {
                'trip_id': train.trip_id,
                'route_id': train.route_id,
                'direction': train.direction,
                'start_date': train.start_date,
                'stop_time_updates': []
            }

            for stop_time in train.stop_time_updates:
                # Filter by stop if specified
                if stop_filter and stop_filter not in stop_time.stop_id:
                    continue

                stop_data = {
                    'stop_id': stop_time.stop_id,
                    'stop_name': stop_time.stop_name if hasattr(stop_time, 'stop_name') else None
                }

                # Add arrival information with time and datetime
                if stop_time.arrival:
                    stop_data['arrival'] = {
                        'time': int(stop_time.arrival.timestamp()),
                        'datetime': stop_time.arrival.isoformat()
                    }

                    # If filtering by stop, add to simplified arrivals list
                    if stop_filter:
                        # Format time as "3:45 PM"
                        arrival_formatted = stop_time.arrival.strftime('%-I:%M %p')
                        arrival_timestamp = int(stop_time.arrival.timestamp())

                        # Calculate when to leave if travel_time is provided
                        arrival_data = {
                            'route_id': train.route_id,
                            'direction': train.direction,
                            'stop_id': stop_time.stop_id,
                            'stop_name': stop_time.stop_name if hasattr(stop_time, 'stop_name') else None,
                            'arrival_time': arrival_formatted,
                            'timestamp': arrival_timestamp
                        }

                        if travel_time:
                            from datetime import datetime as dt
                            now = dt.now()
                            arrival_dt = stop_time.arrival
                            minutes_until_arrival = int((arrival_dt - now).total_seconds() / 60)
                            leave_in = minutes_until_arrival - travel_time

                            if leave_in > 0:
                                arrival_data['leave_in'] = f"Leave in {leave_in} minutes"
                            elif leave_in == 0:
                                arrival_data['leave_in'] = "Leave now!"
                            else:
                                arrival_data['leave_in'] = f"Too late (missed by {abs(leave_in)} min)"

                        arrivals_with_timestamp.append(arrival_data)

                # Add departure information with time and datetime
                if stop_time.departure:
                    stop_data['departure'] = {
                        'time': int(stop_time.departure.timestamp()),
                        'datetime': stop_time.departure.isoformat()
                    }

                trip_data['stop_time_updates'].append(stop_data)

            # Only include trips that have matching stops (if stop filter was applied)
            if not stop_filter or trip_data['stop_time_updates']:
                trips.append(trip_data)

        response = {
            'feed_id': feed_id,
            'timestamp': {
                'epoch': int(feed.last_generated.timestamp()),
                'datetime': feed.last_generated.isoformat()
            }
        }

        # If stop filter is applied, return simplified arrivals list
        if stop_filter:
            # Sort by timestamp
            arrivals_with_timestamp.sort(key=lambda x: x['timestamp'])
            # Remove timestamp from final output and limit to first 3
            arrivals = [{k: v for k, v in a.items() if k != 'timestamp'} for a in arrivals_with_timestamp[:3]]
            response['arrivals'] = arrivals
        else:
            response['trips'] = trips

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': f'Error processing feed: {str(e)}'}), 500

if __name__ == '__main__':
    # Using port 8000 instead of 5000 (which is used by macOS AirPlay Receiver)
    app.run(debug=True, host='0.0.0.0', port=8000)
