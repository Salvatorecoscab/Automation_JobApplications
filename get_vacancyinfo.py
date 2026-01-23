
from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import re
from update_csv import update_csv_from_json_vacancies
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEy")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
# open mockup texts in the mock_ups.json file
with open("mock_ups.json", "r", encoding="utf-8") as f:
    mockups = json.load(f)

# Extrae solo el texto de la lista de inglés
mockup_english = ", ".join(mockups["mockups_cover_letter"]["english"])

# Extrae solo el texto de la lista de alemán
mockup_german = ", ".join(mockups["mockups_cover_letter"]["german"])





vacancy_rules="""
You are going to receive a text and extract the following information.
Respond ONLY with a valid JSON object.

json object format:
{
  "application": {
    "language": "",
    "place_of_internship": "",
    "company_name": "",
    "person_in_charge": "",
    "internship_title": "",
    "role_activities": "",
    "requirements_for_the_internship": ""
  }
}

RULES:
- Language must be either "english" or "german"
- If a field is missing, use an empty string
- No explanations, no markdown, no comments
- Translate the name of the place to english or german depending on the language of the vacancy
 For the place if the internship use this format street, number - postal code city. if possible if not just postal code city or just the city. Remember to respond only with the json object and nothing else.
"""

def process_vacancy_json(vacancy):
    response_vacancy = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": vacancy_rules},
            {"role": "user", "content": vacancy},
        ],
        stream=False
    )
    
    content = response_vacancy.choices[0].message.content
    print("Respuesta de IA recibida.")

    try:
        # 1. Extraer solo el contenido dentro de los bloques de código JSON
        match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
        else:
            # Si no hay backticks, intentamos limpiar el texto para ver si es un JSON puro
            json_str = content.strip()

        # 2. Parsear el JSON
        json_vacancy = json.loads(json_str)

        # 3. Guardar el archivo correctamente
        with open("vacancy_info.json", "w", encoding="utf-8") as f:
            json.dump(json_vacancy, f, indent=4, ensure_ascii=False)
        
        print("Archivo vacancy_info.json generado exitosamente.")
        
        # 4. Actualizar CSV
        update_csv_from_json_vacancies("vacancy_info.json", "vacancies.csv")
        
        # IMPORTANTE: Devolvemos el diccionario parseado, no el texto bruto
        return json_vacancy

    except json.JSONDecodeError as e:
        print(f"Error crítico: La IA no devolvió un JSON válido. Detalle: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None
def generate_coverletter():
  system_identity = (
      "You are an expert career coach helping a Computer Systems Engineering student. "
      "Your goal is to write a cover letter that sounds EXACTLY like the student's provided mockups. "
      "Maintain a balance between technical confidence (from previous academic and working experience) and a "
      "proactive learning mindset for unknown technologies."
  )
  with open("vacancy_info.json", "r", encoding="utf-8") as f:
      json_vacancy = json.load(f)

  vacancy_info = json.dumps(json_vacancy["application"])
  with open("cv.json", "r", encoding="utf-8") as f:
      cv_data = json.load(f)
  cv = json.dumps(cv_data)
  vacancy_language = json_vacancy["application"].get("language")
  mockups=""
  if vacancy_language == "german":
      print("The vacancy is in german")
      mockups=mockup_german
  else:   
      print("The vacancy is in english")
      mockups=mockup_english
  # Define strict rules separately
  prompt_rules = (
    f"TASK: Write a cover letter in {vacancy_language}.\n"
    "CONSTRAINTS:\n"
    "- LENGTH: 350-400 words.\n"
    "- STYLE: Match the provided mockups.\n"
    "- NO HALLUCINATIONS: Do not mention skills not in the CV. If a skill is missing, say 'I am    willing to learn'.\n"
    "- FORMAT: Plain text only. No markdown, no title, no farewell.\n"
    f"- REFERENCE MOCKUPS: {mockups}"
  )

  messages = [
      {"role": "system", "content": system_identity},
      {"role": "user", "content": f"STRICT RULES:\n{prompt_rules}"},
      {"role": "user", "content": f"STUDENT CV (FACTS ONLY):\n{cv}"},
      {"role": "user", "content": f"TARGET VACANCY:\n{vacancy_info}"},
  ]
  response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.3 # Lower temperature reduces "creativity" (hallucinations)
)
  coverletter = response.choices[0].message.content
  print("Generated Cover Letter: "+coverletter)
  return coverletter, json_vacancy

def save_application_data():
    coverletter, json_vacancy = generate_coverletter()

    data = {
        "language": json_vacancy["application"].get("language", ""),
        "place_of_internship": json_vacancy["application"].get("place_of_internship", ""),
        "company_name": json_vacancy["application"].get("company_name", ""),
        "person_in_charge": json_vacancy["application"].get("person_in_charge", ""),
        "internship_title": json_vacancy["application"].get("internship_title", ""),
        "cover_letter_text": coverletter,
    }

    # ✔ SAFE LOAD
    try:
        with open("internship_application.json", "r", encoding="utf-8") as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = {}

    existing["application"] = data

    with open("internship_application.json", "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=4)
