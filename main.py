from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from supabase import create_client
import fitz  # PyMuPDF
import tempfile
import traceback

SUPABASE_URL = "https://yamgofgwqbytmriukcnv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhbWdvZmd3cWJ5dG1yaXVrY252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQxODc1NDksImV4cCI6MjA1OTc2MzU0OX0._ppBZ2rBIE80NGeVR-MtG1HVBVHNzBdu0925-j52rxg"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
CORS(app)  #ABILITA CORS UNIVERSALE
BUCKET = "benchbila"
TABELLA = "tabella"

@app.route("/get_bilancio", methods=["GET"])
def get_bilancio():
    try:
        azienda = request.args.get("azienda")
        categoria = request.args.get("categoria", "Bilancio")

        print(f"[DEBUG] Parametri ricevuti: azienda={azienda}, categoria={categoria}")

        if not azienda:
            return jsonify({"errore": "Parametro 'azienda' mancante"}), 400

        query = supabase.table(TABELLA).select("*").ilike("Azienda", azienda).ilike("categoria", categoria).execute()
        print(f"[DEBUG] Risultato query: {query.data}")

        if not query.data:
            return jsonify({"errore": "Documento non trovato"}), 404

        file_info = query.data[0]
        original_path = file_info["path"]
        print(f"[DEBUG] path del file nel DB: {original_path}")

        # Rimuove il prefisso \"benchbila/\" se presente
        clean_path = original_path.replace("benchbila/", "")
        print(f"[DEBUG] path corretto usato per il download: {clean_path}")

        file_data = supabase.storage.from_(BUCKET).download(clean_path)




        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(file_data)
            temp_path = temp.name

        doc = fitz.open(temp_path)
        testo = "".join([page.get_text() for page in doc])
        doc.close()

        
        response = make_response(jsonify({
            "azienda": azienda,
            "categoria": categoria,
            "contenuto": testo[:4000]
        }), 200)
        response.headers["Content-Type"] = "application/json"
        return response

    except Exception as e:
        print("[ERROR]", traceback.format_exc())
        return jsonify({"errore": str(e)}), 500


@app.route("/dump", methods=["GET"])
def dump_tabella():
    query = supabase.table(TABELLA).select("*").execute()
    return jsonify(query.data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
