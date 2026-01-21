# tk kinter interface for GUI form to get data to fill up a latex template

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
from update_csv import update_csv_from_json
from send_data_to_latex import create_letter
from get_vacancyinfo import process_vacancy,save_application_data

# Output JSON file
OUTPUT_FILE = Path("internship_application.json")
OUTPUT_CSV = "applications.csv"
INPUT_JSON = "application_data.json"


class InternshipForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Internship Application Data")
        self.geometry("700x600")

        # -------- Vacancy text (TOP) --------
        tk.Label(self, text="Vacancy (copy-paste):").grid(
            row=0, column=0, sticky="nw", padx=10, pady=5
        )
        self.vacancy_text = tk.Text(self, height=8, wrap="word")
        self.vacancy_text.grid(
            row=0, column=1, sticky="nsew", padx=10, pady=5
        )

        tk.Button(
            self, text="Process Vacancy", command=self.process_vacancy
        ).grid(row=0, column=2, sticky="n", padx=5, pady=5)

        # -------- Form fields --------
        # Language
        tk.Label(self, text="Language of application:").grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )
        self.language_var = tk.StringVar(value="german")
        self.language_combo = ttk.Combobox(
            self,
            textvariable=self.language_var,
            values=["german", "english"],
            state="readonly",
        )
        self.language_combo.grid(
            row=1, column=1, sticky="ew", padx=10, pady=5
        )

        # Place
        tk.Label(self, text="Place of internship:").grid(
            row=2, column=0, sticky="w", padx=10, pady=5
        )
        self.place_entry1 = tk.Entry(self)
        self.place_entry1.grid(
            row=2, column=1, sticky="ew", padx=5, pady=5
        )
        self.place_entry2 = tk.Entry(self)
        self.place_entry2.grid(
            row=2, column=2, sticky="ew", padx=5, pady=5
        )

        # Company
        tk.Label(self, text="Company name:").grid(
            row=3, column=0, sticky="w", padx=10, pady=5
        )
        self.company_entry = tk.Entry(self)
        self.company_entry.grid(
            row=3, column=1, sticky="ew", padx=10, pady=5
        )

        # Person in charge
        tk.Label(self, text="Person in charge:").grid(
            row=4, column=0, sticky="w", padx=10, pady=5
        )
        self.person_entry = tk.Entry(self)
        self.person_entry.insert(0, "Recruiting-Team")
        self.person_entry.grid(
            row=4, column=1, sticky="ew", padx=10, pady=5
        )

        # Internship title
        tk.Label(self, text="Internship title:").grid(
            row=5, column=0, sticky="w", padx=10, pady=5
        )
        self.title_entry = tk.Entry(self)
        self.title_entry.grid(
            row=5, column=1, sticky="ew", padx=10, pady=5
        )

        # Cover letter
        tk.Label(self, text="Cover letter text:").grid(
            row=6, column=0, sticky="nw", padx=10, pady=5
        )
        self.cover_text = tk.Text(self, height=15, wrap="word")
        self.cover_text.grid(
            row=6, column=1, sticky="nsew", padx=10, pady=5
        )

        # Save button
        tk.Button(
            self, text="Save to JSON", command=self.save_to_json
        ).grid(row=7, column=0, columnspan=2, pady=10)

        # Grid behavior
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(6, weight=1)


    def process_vacancy(self):
        """Process pasted vacancy text and autofill fields."""
        vacancy = self.vacancy_text.get("1.0", "end").strip()

        if not vacancy:
            messagebox.showwarning("Empty Vacancy", "Please paste a vacancy first.")
            return

        try:
            # >>>>> CALL WILL BE ENABLED BY YOU LATER <<<<<
            vacancy_info = process_vacancy(vacancy)
            save_application_data()
            with open("internship_application.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            data = data.get("application", {})

            if "language" in data:
                self.language_var.set(data["language"])

            if "place_of_internship" in data:
                places = data["place_of_internship"]
                if len(places) > 0:
                    self.place_entry1.delete(0, tk.END)
                    self.place_entry1.insert(0, places[0])
                if len(places) > 1:
                    self.place_entry2.delete(0, tk.END)
                    self.place_entry2.insert(0, places[1])

            if "company_name" in data:
                self.company_entry.delete(0, tk.END)
                self.company_entry.insert(0, data["company_name"])

            if "person_in_charge" in data:
                self.person_entry.delete(0, tk.END)
                self.person_entry.insert(0, data["person_in_charge"])

            if "internship_title" in data:
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, data["internship_title"])

            if "cover_letter_text" in data:
                self.cover_text.delete("1.0", tk.END)
                self.cover_text.insert("1.0", data["cover_letter_text"])

            messagebox.showinfo("Vacancy", "Vacancy processed.")

        except Exception as e:
            messagebox.showerror("Error", f"Could not process vacancy:\n{e}")

    def collect_data(self):
        return {
            "language": self.language_var.get(),
            "place_of_internship": [self.place_entry1.get(), self.place_entry2.get()],
            "company_name": self.company_entry.get(),
            "person_in_charge": self.person_entry.get(),
            "internship_title": self.title_entry.get(),
            "cover_letter_text": self.cover_text.get("1.0", "end").strip(),
        }

    def save_to_json(self):
        data = self.collect_data()

        try:
            if OUTPUT_FILE.exists():
                with OUTPUT_FILE.open("r", encoding="utf-8") as f:
                    existing = json.load(f)
            else:
                existing = {}

            existing["application"] = data

            with OUTPUT_FILE.open("w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=4)

            messagebox.showinfo("Success", f"Data saved to {OUTPUT_FILE}")

            update_csv_from_json(OUTPUT_FILE, OUTPUT_CSV)
            create_letter()


        except Exception as e:
            messagebox.showerror("Error", f"Could not save data:\n{e}")


if __name__ == "__main__":
    app = InternshipForm()
    app.mainloop()
