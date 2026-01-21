
from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import re
from update_csv import update_csv_from_json_vacancies
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEy")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
mockup_german="""
Bewerbung als Praktikant in der Forschung und Entwicklung – Testautoma-
tisierung
ich habe Ihre Ausschreibung für das Praktikum in der Testautomatisierung in Lübeck gelesen und finde den
Fokus auf „Technik für das Leben“ sehr motivierend. Als Student der Technischen Informatik und DAAD-
KOSPIE-Stipendiat an der Universität Göttingen suche ich für den Zeitraum von März bis August 2026 ein
sechsmonatiges Pflichtpraktikum, um meine Erfahrungen in der Automatisierung und Softwareentwicklung
praktisch einzubringen.
Während meiner Zeit als Werkstudent bei Ford habe ich bereits intensiv an CI/CD-Pipelines und der
Automatisierung von Testprozessen gearbeitet. Dabei ging es mir vor allem darum, Tools zu entwickeln,
die Fehler frühzeitig erkennen und Entwicklern direktes Feedback geben. Mir gefällt der Prozess, komplexe
Testframeworks stabiler und effizienter zu machen – genau das, was Sie mit der Weiterentwicklung Ihres
Frameworks in Python anstreben.
Neben der reinen Testautomatisierung bringe ich Erfahrung in der Webentwicklung (React/TypeScript)
und im Bereich Machine Learning (Python/OpenCV) mit. Projekte wie mein FPGA-Computer oder meine
Roboter-Steuerungen haben mir gezeigt, wie wichtig eine sorgfältige Dokumentation und präzise Testhilfs-
mittel sind, damit Hardware und Software am Ende reibungslos zusammenspielen. Ich arbeite mich gerne
eigenständig in neue Tech-Stacks ein und habe Spaß daran, Werkzeuge zu bauen, die anderen die Arbeit
erleichtern.
Ich spreche fließend Englisch und Deutsch (B2-Niveau) und freue mich darauf, Teil eines Teams zu werden,
das an Technologien arbeitet, die einen echten Unterschied machen. Ein Umzug nach Lübeck für die Dauer
des Praktikums ist für mich selbstverständlich.
Vielen Dank für Ihre Zeit. Ich freue mich auf die Gelegenheit, mich persönlich mit Ihnen auszutauschen.
"""
mockup_english="""
ApplicationforInternship—AgileProjectManagementforAutomatedDriving
Development
To the Recruiting Team,
I am a Computer Systems Engineering student currently participating in the DAAD-KOSPIE exchange
program and completing my academic exchange at the University of Göttingen. As part of this program, I
am required to complete a mandatory six-month professional internship, and I am seeking an opportunity
that combines my technical background with structured project coordination. For this reason, I am very
interested in joining your team as an intern.
My academic focus is on robotics and embedded systems, but my professional experience has shown me
that complex technologies depend just as much on clear processes and coordination as on strong technical
implementation. During my time as a Working Student at Ford Motor Company, I worked closely with
both development and process-oriented teams. While my responsibilities included CI/CD pipelines and
monitoring tools, a key part of my contribution was improving transparency and workflow efficiency for
example, by using the Jira API to create reports that supported planning and faster feedback cycles.
This experience reinforced the importance of clear documentation and alignment in fast-paced automotive
development.
Through my studies in Mexico and my academic exchange in Germany,  have learned to work independently
while collaborating effectively in multidisciplinary and international teams. I am comfortable using agile
tools such as Jira and communicate fluently in both German and English, enabling effective cross-functional
collaboration.
I am motivated to complete my mandatory six-month internship starting in March or April 2026 and would
be glad to contribute my analytical mindset and structured working style to your team. I am fully willing
to relocate and would welcome the opportunity to discuss how my background and interests align with your
projects.
Thank you very much for your time and consideration.


"""

def process_vacancy(vacancy):
  response_vacancy = client.chat.completions.create(
      model="deepseek-chat",
      messages=[
          {"role": "system", "content": "You are a going to recieve a text and you should be able to determine the following information from it: language (either english or german), place_of_internship (could be just city and postal code, this should be in the determined language. It means if the vacancy is in english, the name in english, if is in german, in german), company_name (if possible or convenient try to get the full company name, eg. Audi AG), person_in_charge (if you dont know the name just Recruiting-Team), internship_title (put in this format (if english:Application for Internship - x. if is in german: Bewerbung als Praktikant - x)), role_activities, requirements. Be descriptive in the role activities and the requirements, such as a programming language, a specific framework or anything. You should respond only with a json object with the following structure: {\n    \"application\": {\n        \"language\": \"...\",\n        \"place_of_internship\": [\"...\", \"...\"],\n        \"company_name\": \"...\",\n        \"person_in_charge\": \"...\",\n        \"internship_title\": \"...\",\n        \"role_activities\": \"...\"\n \"requirements_for_the_internship\": \"...\"\n    }\n}. If any of the fields is not present in the text, you should fill it with an empty string or an array with two empty strings for place_of_internship. Do not add any extra information or explanation."},
          {"role": "user", "content": vacancy},
      ],
      stream=False
  )
  vacancy_info = response_vacancy.choices[0].message.content
  print("Vacancy info: "+vacancy_info)
  # Extrae el contenido entre las marcas de código ```json y ```
  match = re.search(r'```json\s+(.*?)\s+```', vacancy_info, re.DOTALL)
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

  return vacancy_info

def generate_coverletter():
  with open("vacancy_info.json", "r", encoding="utf-8") as f:
      json_vacancy = json.load(f)

  vacancy_info = json.dumps(json_vacancy["application"])
  with open("cv.json", "r", encoding="utf-8") as f:
      cv_data = json.load(f)
  cv = json.dumps(cv_data)
  instructions_coverletter="""
      Based on this CV:"""+cv+"""
     
  and based on this vacancy: """+vacancy_info+"""
  write a cover letter in the language from the vacancy based on this sketchups if it is in german use this structure: """+mockup_german+"""  if is in english use """+mockup_english+""". Make sure to include role activities and requirements from the vacancy in the letter. The letter should be formal and convincing, highlighting relevant skills and experiences from the CV that match the internship requirements. The letter should be around 300-400 words.

  """
  response_coverletter = client.chat.completions.create(
      model="deepseek-chat",
      messages=[
          {"role": "system", "content": "You are a going to write a cover letter.In english or german based on the vacancy language. add just the text without the Tittle, and also without the closing regards."},
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
    


