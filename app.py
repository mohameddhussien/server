import sys
from flask import Flask, jsonify, request
import jwt
from flask_cors import CORS, cross_origin
import requests
import validators as valid
import db


# instantiate the app
app = Flask(__name__)
CORS(app, support_credentials=True)
app.config.from_object(__name__)
SECRET_KEY = "!mF8u88y7Q1w_20a3Z4x5c6V7b8n9m0"
app.secret_key = SECRET_KEY


def get_country_calling_codes():
    url = "https://restcountries.com/v3.1/all?fields=name,idd"
    result = {"countries": []}

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            result["countries"] = [
                {
                    "c_name": country.get("name", {}).get("common", "N/A"),
                    "c_code": country.get("idd", {}).get("root", "N/A"),
                }
                for country in data
            ]
        else:
            result["error"] = f"Error: {response.status_code}"

    except Exception as e:
        result["error"] = f"An error occurred: {e}"

    return result


@app.route("/country-calling-codes", methods=["GET"])
@cross_origin(supports_credentials=True)
def country_calling_codes():
    data = get_country_calling_codes()
    return jsonify(data)


@app.route("/events/<string:event_uuid>", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_event(event_uuid):
    event = db.getEvent(event_uuid)
    return jsonify(event)


@app.route("/getallevents", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_all_events():
    events = db.getAllEvents()
    return jsonify(events)


@app.route("/login", methods=["POST"])
@cross_origin(supports_credentials=True)
def login():
    credentials = request.get_json(force=True)
    username = credentials["username"]
    password = credentials["password"]
    if username == "" or password == "":
        return jsonify({"error": "Missing data.. please check all inputs."})
    user = db.GetUser(username, password)
    if "error" in user:
        return jsonify({"error": user["error"]})
    print(user)
    token = jwt.encode(
        {"user": {"id": user[0], "name": user[8]}}, SECRET_KEY, algorithm="HS256"
    )
    return jsonify(
        {
            "token": token,
            "user": user,
            "success": "Congratulations, you have successfully logged in.",
        }
    )


@app.route("/register", methods=["POST"])
@cross_origin(supports_credentials=True)
def register():
    data = request.get_json(force=True)
    keys = [
        "username",
        "first_name",
        "last_name",
        "email",
        "password",
        "confirmpass",
    ]
    if all(data.get(field, "") != "" for field in keys):
        print("All required fields are filled.")
    else:
        return jsonify({"error": "Missing inputs.. please check all inputs."})
    if set(keys).issubset(set(dict.keys(data))):
        error = valid.validate_signup_inputs(data)
        if error is not None:
            print("error:", error)
            return jsonify({"error": error})
        data = tuple(data.values())[:-1]
        insert = db.InsertUser(data)
        if "error" in insert:
            print("insert error")
            return jsonify({"error": f"Error with database: {insert['error']}"})
        print("success")
        return jsonify({"success": "Signed up successfully!"})


if __name__ == "__main__":
    db.CreateUserTable()
    db.CreateOrganizersTable()
    app.run(debug=True, host="192.168.1.23", port=1532)
