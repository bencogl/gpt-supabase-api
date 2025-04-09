
from flask import Flask, request, jsonify
from supabase import create_client
import fitz  # PyMuPDF
import tempfile

SUPABASE_URL = "https://yamgofgwqbytmriukcnv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhbWdvZmd3cWJ5dG1yaXVrY252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQxODc1NDksImV4cCI6MjA1OTc2MzU0OX0._ppBZ2rBIE80NGeVR-MtG1HVBVHNzBdu0925-j52rxg"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
BUCKET = "benchbila"
TABELLA = "tabella"

@app.route("/get_bilancio", methods=["GET"])
def get_bilancio():
    azienda = request.args.get("azienda")
    categoria = request.args.get("categoria", "bilancio")
    if not azienda:
        return jsonify({"errore": "Manca azienda"}), 400

    query = supabase.table(tabella).select("*").eq("Azienda", azienda).eq("categoria", categoria).execute()
    if not query.data:
        return jsonify({"errore": "Documento non trovato"}), 404

    file_info = query.data[0]
    file_path = file_info["path"]
    file_data = supabase.storage.from_(BUCKET).download(file_path)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(file_data)
        temp_path = temp.name

    doc = fitz.open(temp_path)
    testo = "".join([page.get_text() for page in doc])
    doc.close()

    return jsonify({
        "azienda": azienda,
        "categoria": categoria,
        "contenuto": testo[:4000]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
