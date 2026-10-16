# //////////////////////////////////////////////////////
#                    PIPELINE SERVER
#   Put this file in teach_be/teach_pipe/ (next to flowmain.py)
#   Run it from teach_be:   python3 teach_pipe/server.py
# //////////////////////////////////////////////////////

import json
import os
import threading

import requests
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from flow.pipe_base import parse_config
from flow.pipe_flow import PipelineFlow

app = Flask(__name__)
CORS(app)  # lets the React page (port 5173) call this server (port 5001)

CASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "config", "case.yaml"
)

CASE_HEADER = """# # //////////////////////////////////////////////////////
#                     CASE INPUT 
# ////////////////////////////////////////////////////////

"""

# case.yaml is one shared file: only one request may use it at a time
case_lock = threading.Lock()


# The tables that exist in the database right now, asked to the API
def available_tables():
    api_url = parse_config().api_url.rstrip("/")
    try:
        response = requests.get(f"{api_url}/tables", timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        raise RuntimeError(f"Cannot get the list of tables from the API: {err}")
    return response.json()


@app.get("/tables")
def list_tables():
    try:
        return jsonify(available_tables())
    except RuntimeError as err:
        return jsonify({"error": str(err)}), 502


@app.post("/run")
def run_pipeline():
    data = request.get_json() or {}
    table = data.get("dbtable")

    # 1. validate the input against the real list of tables:
    #    only a name that exists in the database can be written into case.yaml
    try:
        tables = available_tables()
    except RuntimeError as err:
        return jsonify({"error": str(err)}), 502
    if table not in tables:
        return jsonify({"error": f"Table '{table}' does not exist"}), 400

    with case_lock:
        # 2. write the selection into the case file
        #    (json.dumps writes a safe quoted string, even for unusual table names)
        with open(CASE_PATH, "w") as f:
            f.write(CASE_HEADER + f"dbtable: {json.dumps(table)}\n")

        # 3. run the pipeline (a new PipelineFlow reads the config again, so it sees the new case)
        try:
            result = PipelineFlow().run()
        except RuntimeError as err:
            return jsonify({"error": str(err)}), 502

    # 4. send the table back as JSON (missing values become null)
    return Response(result.to_json(orient="records", date_format="iso"), mimetype="application/json")


if __name__ == "__main__":
    app.run(port=5001, debug=True)