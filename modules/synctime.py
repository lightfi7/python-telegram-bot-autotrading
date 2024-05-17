from datetime import datetime

import win32api
import requests

def sync_utc_time():
    try:
        response = requests.get('http://worldtimeapi.org/api/timezone/UTC')
        response.raise_for_status()  # Raise an error for bad HTTP status codes
        time_data = response.json()

        # Parse the datetime string
        dt = datetime.strptime(time_data['datetime'], "%Y-%m-%dT%H:%M:%S.%f%z")

        # Set the system time
        win32api.SetSystemTime(
            dt.year, dt.month, 0, dt.day,
            dt.hour, dt.minute, dt.second, dt.microsecond // 1000
        )
        print("System time successfully synchronized with UTC.")
        return True
    except requests.RequestException as e:
        print(f"Error occurred while fetching the time: {e}")
        return False
    except (ValueError, KeyError) as e:
        print(f"Error occurred while parsing the time data: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
