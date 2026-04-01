# apaleo Guest Check-in Demo (Flask)

Kleine Demo-App, mit der ihr Gäste über eine Reservierungs-ID via apaleo einchecken könnt.

## Voraussetzungen

- Python 3.11+
- apaleo API Client Credentials mit passenden Scopes

## Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export $(grep -v '^#' .env | xargs)
python app.py
```

App läuft dann auf `http://localhost:5000`.

## Wichtige Hinweise

- Das ist ein **MVP/Starter**, noch ohne Multi-Property-Auswahl, Rollenmodell, Rate-Limit-Handling und Audit-Logging.
- Für Produktion: Secret-Management, robustes Error-Handling, Retries, Monitoring und Datenschutz-Prozesse ergänzen.
