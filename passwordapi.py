from flask import Flask, request, jsonify
import hashlib
import random
import string
import json


app = Flask(__name__)

generated_password = ""

def generate_password():
    generated_password = "".join(
        random.choices(string.ascii_letters + string.digits, k=random.randint(8, 16))
    )
    print("Generated Password: " + generated_password)
    return hashlib.md5(generated_password.encode()).hexdigest()


@app.route("/get_password", methods=["GET"])
def get_password():

    response = jsonify({"password": generated_password})
    with open("password.json", "w") as f:
        json.dump({"password": generated_password}, f)
    return response


@app.route("/check_password", methods=["POST"])
def check_password():
    data = request.get_json()
    password = data.get("password")
    password_hash = hashlib.md5(password.encode()).hexdigest()
    with open("password.json", "r") as f:
        stored_password = json.load(f).get("password")
    if password_hash == stored_password:
        return jsonify({"message": "Success"})
    else:
        return jsonify({"message": "Failed"})


if __name__ == "__main__":
    generate_password()
    app.run()