import base64
import os
import json
import csv
import logging

def process_attachments(attachments: list[dict]) -> dict:
    """
    Processes the attachments by decoding them and saving them to a temporary directory.
    For image files, it returns the data URI directly.
    """
    processed_data = {}
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    for attachment in attachments:
        name = attachment["name"]
        url = attachment["url"]

        if name.endswith((".png", ".jpg", ".jpeg")):
            processed_data[name] = url
            continue

        try:
            header, encoded = url.split(",", 1)
            # Add padding if it's missing
            padding = len(encoded) % 4
            if padding != 0:
                encoded += "=" * (4 - padding)
            data = base64.b64decode(encoded)
        except (ValueError, TypeError) as e:
            logging.error(f"Error decoding attachment {name}: {e}")
            continue

        file_path = os.path.join(temp_dir, name)
        try:
            with open(file_path, "wb") as f:
                f.write(data)
        except IOError as e:
            logging.error(f"Error writing attachment {name} to file: {e}")
            continue

        if name.endswith(".csv"):
            try:
                with open(file_path, "r", encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    processed_data[name] = [row for row in reader]
            except (IOError, csv.Error) as e:
                logging.error(f"Error processing CSV {name}: {e}")
        elif name.endswith(".json"):
            try:
                with open(file_path, "r") as f:
                    processed_data[name] = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                logging.error(f"Error processing JSON {name}: {e}")
        elif name.endswith(".md"):
            try:
                with open(file_path, "r") as f:
                    processed_data[name] = f.read()
            except IOError as e:
                logging.error(f"Error reading Markdown file {name}: {e}")

    return processed_data