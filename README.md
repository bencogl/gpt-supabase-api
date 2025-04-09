
# GPT Supabase API

Questa è una semplice API Flask che legge documenti PDF da Supabase e li restituisce in formato testo per essere interrogati da GPT.

## Rotta disponibile

```
GET /get_bilancio?azienda=Enel&nome=Bilancio%202024
```

## Deployment su Render

1. Forka il repo
2. Vai su [https://render.com](https://render.com)
3. Collega il tuo GitHub
4. "New Web Service" → Seleziona il repo
5. Verifica che usi:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python main.py`
6. Aggiungi le environment variables se le sposti dal file
