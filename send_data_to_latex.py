import subprocess
import os
import json
from jinja2 import Environment, FileSystemLoader
import re
def escape_latex(text):
    if not isinstance(text, str):
        return text

    # Diccionario de mapeo
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }

    # Creamos una expresión regular que busca cualquiera de estos caracteres.
    # El orden en el re.escape es vital, y usar re.compile mejora el rendimiento.
    regex = re.compile('|'.join(re.escape(str(key)) for key in conv.keys()))
    
    # La magia: cada coincidencia se reemplaza solo una vez.
    return regex.sub(lambda mo: conv[mo.group()], text)
def sanitize_for_latex(obj):
    if isinstance(obj, dict):
        return {k: sanitize_for_latex(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_latex(v) for v in obj]
    elif isinstance(obj, str):
        return escape_latex(obj)
    return obj

def read_json(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        return sanitize_for_latex(data)
def get_jinja_env(template_file):
    return Environment(
        block_start_string='[%',
        block_end_string='%]',
        variable_start_string='((',
        variable_end_string='))',
        comment_start_string='[#',
        comment_end_string='#]',
        line_statement_prefix=None, 
        line_comment_prefix=None,
        trim_blocks=True,      # Elimina saltos de línea automáticos de Jinja
        lstrip_blocks=True,    # Elimina espacios a la izquierda de bloques
        loader=FileSystemLoader(searchpath=os.path.dirname(template_file))
    )
def fill_latex_main_template(json_file, template_file, output_file):
    data = read_json(json_file)["application"]
    env = get_jinja_env(template_file)
    template = env.get_template(os.path.basename(template_file))
    
    place_raw = data.get("place_of_internship", "")
    if place_raw[0] == "":
        place_str = place_raw[1]
    else:
        place_str = " -- ".join(place_raw) if isinstance(place_raw, list) else place_raw

    rendered_content = template.render(
        language=data.get("language", ""),
        company_name=data.get("company_name", ""),     
        person_in_charge=data.get("person_in_charge", ""), 
        place_of_internship=place_str
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered_content)

def fill_latex_letter_template(json_file, template_file, output_file):
    # read_json ya devuelve los datos escapados correctamente
    data = read_json(json_file)["application"]
    env = get_jinja_env(template_file)
    template = env.get_template(os.path.basename(template_file))

    # Obtenemos el texto que ya fue escapado en read_json
    cover_letter_escaped = data.get("cover_letter_text", "")
    cover_letter_processed = cover_letter_escaped.replace("\n", " \\\\ ")

    rendered_content = template.render(
        # Internship_title también viene ya escapado de read_json
        title=data.get("internship_title", ""),  
        coverletter=cover_letter_processed      
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered_content)

def generate_pdf(language):
    # Guardar el directorio actual para volver después
    original_dir = os.getcwd()
    print(original_dir)
    #remove old pdf if exists
    target_name = "Anschreiben.pdf" if language == "german" else "Cover_Letter.pdf"
    if os.path.exists(target_name):
        os.remove(target_name) 
        
    try:
        os.chdir("Job_Application_letter")
        # Ejecutamos pdflatex dos veces (estándar en LaTeX para referencias)
        subprocess.run(["pdflatex", "main.tex"], check=True)
        print("PDF generated successfully.")
        # delete old files if exist
        target_name = "Anschreiben.pdf" if language == "german" else "Cover_Letter.pdf"
        # Usamos os.path para evitar problemas de rutas
        subprocess.run(["cp", "main.pdf", os.path.join("..", target_name)], check=True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        os.chdir(original_dir)

def create_letter():
    os.makedirs("Job_Application_letter/Txt", exist_ok=True)
    data = read_json("internship_application.json")
    lang = data["application"]["language"]

    fill_latex_main_template("internship_application.json", 
                    "Job_Application_letter_template/main.tex", 
                    "Job_Application_letter/main.tex")

    fill_latex_letter_template("internship_application.json",
                    "Job_Application_letter_template/Txt/Application-letter.tex",
                    "Job_Application_letter/Txt/Application-letter.tex")

    generate_pdf(lang)
    # open the generated PDF
    target_name = "Anschreiben.pdf" if lang == "german" else "Cover_Letter.pdf"
    subprocess.run(["open", target_name])
    

if __name__ == "__main__":
    create_letter()