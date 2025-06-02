from flask import Flask, render_template, request, redirect
from azure.identity import DefaultAzureCredential
from pymongo import MongoClient
import os

app = Flask(__name__)

# RBAC Auth
credential = DefaultAzureCredential()
token = credential.get_token("https://cosmos.azure.com/.default")
MONGO_HOST = os.getenv("COSMOS_HOST")  # ej. mcw-xxxx.mongo.cosmos.azure.com

client = MongoClient(
    f"mongodb://{MONGO_HOST}:10255/?ssl=true&replicaSet=globaldb",
    username="",  # no requerido
    password=token.token,
    authMechanism="MONGODB-AWS",
    authSource="$external"
)

db = client["clientesdb"]
collection = db["clientes"]

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        cliente = {
            "id": request.form["id"],
            "nombre": request.form["nombre"],
            "correo": request.form["correo"],
            "matricula": request.form["matricula"]
        }
        collection.insert_one(cliente)
        return redirect('/')
    clientes = list(collection.find({}, {"_id": 0}))
    return render_template("index.html", clientes=clientes)

if __name__ == "__main__":
    app.run()
