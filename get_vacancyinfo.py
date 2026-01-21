
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

print(mockup_english)
print(mockup_german)



vacancy_rules="""
You are a going to recieve a text and you should be able to determine the following information from it: language (either english or german), place_of_internship (could be just city and postal code, this should be in the determined language. It means if the vacancy is in english, the name in english, if is in german, in german), company_name (if possible or convenient try to get the full company name, eg. Audi AG), person_in_charge (if you dont know the name just Recruiting-Team), internship_title (put in this format (if english:Application for Internship - x. if is in german: Bewerbung als Praktikant - x)), role_activities, requirements. Be descriptive in the role activities and the requirements, such as a programming language, a specific framework or anything. You should respond only with a json object with the following structure: {\n    "application": {\n        "language": "...",\n        "place_of_internship": ["...", "..."],\n        "company_name": "...",\n        "person_in_charge": "...",\n        "internship_title": "...",\n        "role_activities": "..." \n "requirements_for_the_internship": "..." \n    }\n}. If any of the fields is not present in the text, you should fill it with an empty string or an array with two empty strings for place_of_internship. Do not add any extra information or explanation.
"""

def process_vacancy(vacancy):
  response_vacancy = client.chat.completions.create(
      model="deepseek-chat",
      messages=[
          {"role": "system", "content": vacancy_rules},
          {"role": "user", "content": vacancy},
      ],
      stream=False
  )
  vacancy_info = response_vacancy.choices[0].message.content
  print("Vacancy info: "+vacancy_info)
  # Mejora en process_vacancy para manejar respuestas que a veces no traen markdown
  try:
  # Intenta buscar el bloque de código
    match = re.search(r'```json\s+(.*?)\s+```', vacancy_info, re.DOTALL)
    json_str = match.group(1) if match else vacancy_info

    json_vacancy = json.loads(json_str)
    if match:
        # Convierte el texto extraído en un diccionario y lo guarda en el archivo
        json_vacancy = json.loads(match.group(1))
        with open("vacancy_info.json", "w", encoding="utf-8") as f:
            json.dump(json_vacancy, f, indent=4, ensure_ascii=False)
        print("Archivo JSON generado exitosamente.")
    else:
        print("No se encontró un bloque JSON válido en la respuesta.")
        #update a csv with the vacancy info
    update_csv_from_json_vacancies("vacancy_info.json", "vacancies.csv")
  except json.JSONDecodeError:
    print("Error crítico: La IA no devolvió un JSON válido.")

  return vacancy_info

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
  instructions_coverletter="""
      Based on this CV:"""+cv+"""
     
  and based on this vacancy: """+vacancy_info+"""
  write a cover letter in the language from the vacancy based on this sketchups use this structure as reference: """+mockups+"""  . Make sure to include role activities and requirements from the vacancy in the letter. The letter should be formal and convincing, highlighting relevant skills and experiences from the CV that match the internship requirements. The letter should be around 350-400 words. dont add the tittle of the letter, just start with the greeting. dont add any special characters or markdown, just plain text. dont add the farewell to the letter. Dont lie about the CV information, only use what is in there. eg dont say you know a programming language if is not in the CV or say I can speak a language if is not in the CV. Language  German and English B2 are important. Include them if you do not find a required ability don't include it.

  """
  response_coverletter = client.chat.completions.create(
      model="deepseek-chat",
      messages=[
          {"role": "system", "content": system_identity},
          {"role": "user", "content": instructions_coverletter},
      ],
      stream=False
      
  )
  coverletter = response_coverletter.choices[0].message.content
  print("Generated Cover Letter: "+coverletter)
  return coverletter, json_vacancy

def save_application_data():
    coverletter, json_vacancy = generate_coverletter()
    data = {
                "language": json_vacancy["application"].get("language", ""),
                "place_of_internship": json_vacancy["application"].get("place_of_internship", ["", ""]),
                "company_name": json_vacancy["application"].get("company_name", ""),
                "person_in_charge": json_vacancy["application"].get("person_in_charge", ""),
                "internship_title": json_vacancy["application"].get("internship_title", ""),
                "cover_letter_text": coverletter,
            }
    print(data)

    with open("internship_application.json", "r", encoding="utf-8") as f:
        existing = json.load(f)
    existing["application"] = data
    with open("internship_application.json", "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=4)
    


