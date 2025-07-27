'''from flask import Flask, request, jsonify
import os
from services.schema_parser import reconstruct_schema, extract_relevant_schema
from services.cohere_api import call_cohere  # ✅ Changed
from utils.helpers import format_prompt, clean_sql

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB_PATH = os.path.join(UPLOAD_FOLDER, "db.sqlite")

@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to NL2SQL Cohere API!",
        "routes": ["/upload_db (POST)", "/schema (GET)", "/generate_sql (POST)"]
    })

@app.route('/upload_db', methods=['POST'])
def upload_db():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    if not file.filename.endswith(".sqlite"):
        return jsonify({"error": "Only .sqlite files are supported"}), 400

    file.save(DB_PATH)
    return jsonify({"message": "Database uploaded successfully!"})

@app.route('/schema', methods=['GET'])
def get_schema():
    if not os.path.exists(DB_PATH):
        return jsonify({"error": "Upload a DB first."}), 400
    try:
        schema = reconstruct_schema(DB_PATH)
        return jsonify({"schema": schema})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_sql', methods=['POST'])
def generate_sql():
    data = request.json
    question = data.get("question")
    tables = data.get("tables")

    if not question or not tables:
        return jsonify({"error": "Provide both 'question' and 'tables'."}), 400

    try:
        full_schema = reconstruct_schema(DB_PATH)
        relevant_schema = extract_relevant_schema(full_schema, tables)
        prompt = format_prompt(question, relevant_schema)
        sql = call_cohere(prompt)  # ✅ Changed
        return jsonify({
            "question": question,
            "raw_sql": clean_sql(sql)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True) '''
from flask import Flask, request, render_template
import os, sqlite3
from werkzeug.utils import secure_filename
import re

from services.schema_parser import reconstruct_schema, extract_relevant_schema
from services.gemini_api import call_gemini
from services.cohere_api import call_cohere
from utils.helpers import clean_sql, format_prompt

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    db_file = request.files.get("db_file")
    question = request.form.get("question")
    model = request.form.get("llm")

    if not db_file or not question:
        return render_template("index.html", result="❌ Upload DB and enter a question.")

    filename = secure_filename(db_file.filename)
    db_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    db_file.save(db_path)

    try:
        full_schema = reconstruct_schema(db_path)
        tables = [row for row in extract_table_names(full_schema)]
        relevant_schema = extract_relevant_schema(full_schema, tables)
        prompt = format_prompt(question, relevant_schema)

        # Call the appropriate LLM
        if model == "gemini":
            raw_sql = call_gemini(prompt)
        else:
            raw_sql = call_cohere(prompt)

        sql = clean_sql(raw_sql)

        # Execute SQL
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        result = "\n".join(str(row) for row in rows) if rows else "✅ No rows returned."
        conn.close()

    except Exception as e:
        result = f"❌ Error: {str(e)}"
        sql = ""

    return render_template("index.html", sql=sql, result=result)

# Optional: You can implement auto-table name extractor
def extract_table_names(schema_text):
    return re.findall(r'CREATE TABLE (\w+)', schema_text)

if __name__ == "__main__":
    app.run(debug=True)
