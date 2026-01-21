
import csv
import json
from pathlib import Path


def update_csv_from_json(json_file, csv_file):
    # Load data from JSON file
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    application = data.get("application", {})

    # Define CSV headers
    headers = [
        "language",
        "place_of_internship",
        "company_name",
        "person_in_charge",
        "internship_title",
        "cover_letter_text",
    ]




    # Prepare row data
    row = {
        "language": application.get("language", ""),
        "place_of_internship": application.get("place_of_internship",""),
        "company_name": application.get("company_name", ""),
        "person_in_charge": application.get("person_in_charge", ""),
        "internship_title": application.get("internship_title", ""),
        "cover_letter_text": application.get("cover_letter_text", ""),
    }

    csv_path = Path(csv_file)
    file_exists = csv_path.exists()
    file_empty = not file_exists or csv_path.stat().st_size == 0

    # Open in append mode to avoid overwriting
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)

        # Only write header once (when file is new/empty)
        if file_empty:
            writer.writeheader()

        writer.writerow(row)

    print(f"CSV file '{csv_file}' has been updated from JSON data.")

def update_csv_from_json_vacancies(json_file, csv_file):
    # Load data from JSON file
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    application = data.get("application", {})

    # Define CSV headers
    headers = [
        "language",
        "place_of_internship",
        "company_name",
        "person_in_charge",
        "role_activities",
        "requirements_for_the_internship",
    ]



    # Prepare row data
    row = {
        "language": application.get("language", ""),
        "place_of_internship": application.get("place_of_internship",""),
        "company_name": application.get("company_name", ""),
        "person_in_charge": application.get("person_in_charge", ""),
        "role_activities": application.get("role_activities", ""),
        "requirements_for_the_internship": application.get("requirements_for_the_internship", ""),
    }

    csv_path = Path(csv_file)
    file_exists = csv_path.exists()
    file_empty = not file_exists or csv_path.stat().st_size == 0

    # Open in append mode to avoid overwriting
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)

        # Only write header once (when file is new/empty)
        if file_empty:
            writer.writeheader()

        writer.writerow(row)

    print(f"CSV file '{csv_file}' has been updated from JSON data.")

