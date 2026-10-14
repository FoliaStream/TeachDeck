from flask import Flask, jsonify
from flask_cors import CORS

from flow.pipe_flow import PipelineFlow

app = Flask(__name__)
CORS(app)                      # lets React on port 5173 call it
pipeline = PipelineFlow()      # config is loaded once, when the server starts

if __name__ == "__main__":
    app.run(port=5001, debug=True)