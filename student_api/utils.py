import base64
import os
import json
import csv

def process_attachments(attachments: list[dict]) -> dict:
    """
    Decodes and processes the attachments.
    """
    processed_data = {}
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    for attachment in attachments:
        name = attachment["name"]
        url = attachment["url"]

        # Decode the base64-encoded data
        try:
            header, encoded = url.split(",", 1)
            data = base64.b64decode(encoded)
        except Exception as e:
            print(f"Error decoding attachment {name}: {e}")
            continue

        # Save the attachment to a temporary file
        file_path = os.path.join(temp_dir, name)
        with open(file_path, "wb") as f:
            f.write(data)

        # Process the attachment based on its file type
        if name.endswith(".csv"):
            with open(file_path, "r") as f:
                reader = csv.DictReader(f)
                processed_data[name] = [row for row in reader]
        elif name.endswith(".json"):
            with open(file_path, "r") as f:
                processed_data[name] = json.load(f)
        elif name.endswith(".md"):
            with open(file_path, "r") as f:
                processed_data[name] = f.read()

    return processed_data