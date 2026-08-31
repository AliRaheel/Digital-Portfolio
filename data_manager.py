import csv
from datetime import datetime
import os

# Define the local database file path
LOG_FILE = "contact_messages.csv"


def log_contact_message(name, email, message):
    """Safely records visitor message submissions into a structured CSV file."""
    try:
        # Check if the file already exists to decide if we need to write column headers
        file_exists = os.path.isfile(LOG_FILE)

        # Capture the precise timestamp of when the recruiter sent the form
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Open file in append ('a') mode with safe UTF-8 encoding configuration
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as csv_file:
            fieldnames = ["Timestamp", "Name", "Email", "Message"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # If the CSV is completely brand new, insert the headers first
            if not file_exists:
                writer.writeheader()

            # Write the structured user dictionary row data safely
            writer.writerow({
                "Timestamp": current_time,
                "Name": name,
                "Email": email,
                "Message": message
            })
        print(f"📊 Successfully recorded message log row from: {name}")
        return True
    except Exception as e:
        print(f"❌ Critical Error logging message to local storage: {e}")
        return False
