import os
from datetime import date
from typing import Any, Dict

import requests
from flask import Flask, render_template, request

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

APALEO_ID_URL = os.getenv("APALEO_ID_URL", "https://identity.apaleo.com")
APALEO_API_URL = os.getenv("APALEO_API_URL", "https://api.apaleo.com")
APALEO_CLIENT_ID = os.getenv("APALEO_CLIENT_ID", "")
APALEO_CLIENT_SECRET = os.getenv("APALEO_CLIENT_SECRET", "")
APALEO_SCOPE = os.getenv("APALEO_SCOPE", "reservations.read checkin.manage")
REDIRECT_URI = os.getenv("APALEO_REDIRECT_URI", "http://localhost:5000/oauth/callback")


def _apaleo_token() -> str:
    """Exchange client credentials for a management token."""
    response = requests.post(
        f"{APALEO_ID_URL}/connect/token",
        data={
            "grant_type": "client_credentials",
            "scope": APALEO_SCOPE,
        },
        auth=(APALEO_CLIENT_ID, APALEO_CLIENT_SECRET),
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _api_get(path: str, token: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    response = requests.get(
        f"{APALEO_API_URL}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def _api_post(path: str, token: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any] | None:
    response = requests.post(
        f"{APALEO_API_URL}{path}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload or {},
        timeout=20,
    )
    response.raise_for_status()
    if response.text:
        return response.json()
    return None


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", result=None, error=None)


@app.route("/checkin", methods=["POST"])
def checkin():
    reservation_id = request.form.get("reservation_id", "").strip()
    if not reservation_id:
        return render_template("index.html", result=None, error="Bitte Reservierungs-ID eingeben.")

    try:
        token = _apaleo_token()

        reservation = _api_get(f"/booking/v1/reservations/{reservation_id}", token)
        checked_in_res = _api_post(f"/booking/v1/reservations/{reservation_id}/check-in", token)

        result = {
            "reservation": reservation,
            "checked_in": checked_in_res,
        }
        return render_template("index.html", result=result, error=None)
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unbekannt"
        details = exc.response.text if exc.response is not None else str(exc)
        return render_template(
            "index.html",
            result=None,
            error=f"Check-in fehlgeschlagen (HTTP {status}): {details}",
        )
    except Exception as exc:  # pylint: disable=broad-except
        return render_template("index.html", result=None, error=f"Fehler: {exc}")


@app.route("/health")
def health():
    return {"status": "ok", "date": date.today().isoformat()}


if __name__ == "__main__":
    app.run(debug=True)
