
from flask import Flask, jsonify, render_template, request
from database import initialize_database, add_deployment, get_deployments

app = Flask(__name__)

# Initialize the database when the application starts
initialize_database()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    return jsonify({
        "message": "CloudDeploy API",
        "status": "running",
        "database": "connected"
    })


@app.route("/api/deployments", methods=["GET"])
def list_deployments():
    try:
        limit = request.args.get("limit", default=20, type=int)

        if limit is None or limit < 1:
            return jsonify({
                "error": "Limit must be a positive integer"
            }), 400

        deployments = get_deployments(limit)

        return jsonify({
            "count": len(deployments),
            "deployments": deployments
        })
    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid limit"
        }), 400


@app.route("/api/deployments", methods=["POST"])
def create_deployment():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    version = data.get("version")
    environment = data.get("environment", "local")
    details = data.get("details", "")

    if not isinstance(version, str) or not version.strip():
        return jsonify({
            "error": "A non-empty version is required"
        }), 400

    if environment not in ("local", "staging", "production"):
        return jsonify({
            "error": "Environment must be local, staging, or production"
        }), 400

    if not isinstance(details, str):
        return jsonify({
            "error": "Details must be text"
        }), 400

    deployment_id = add_deployment(
        version=version.strip(),
        environment=environment,
        status="success",
        details=details.strip()
    )

    return jsonify({
        "message": "Deployment record created",
        "id": deployment_id
    }), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)