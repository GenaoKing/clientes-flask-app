from flask import Flask, render_template, request, redirect
from azure.identity import DefaultAzureCredential
from pymongo import MongoClient
import os

app = Flask(__name__)

def get_collection():
    try:
        MONGO_HOST = os.getenv("COSMOS_HOST")
        if not MONGO_HOST:
            raise ValueError("COSMOS_HOST not set")
        
        credential = DefaultAzureCredential()
        token = credential.get_token("https://cosmos.azure.com/.default")

        client = MongoClient(
            f"mongodb://{MONGO_HOST}:10255/?ssl=true&replicaSet=globaldb",
            username="",
            password=token.token,
            authMechanism="MONGODB-AWS",
            authSource="$external"
        )

        db = client["clientesdb"]
        return db["clientes"]
    
    except Exception as e:
        print(f"[ERROR] Fallo al conectar con Cosmos DB: {str(e)}")
        return None

@app.route('/', methods=["GET", "POST"])
def index():
    collection = get_collection()
    if not collection:
        return "Error conectando a la base de datos.", 500

    if request.method == "POST":
        try:
            cliente = {
                "id": request.form["id"],
                "nombre": request.form["nombre"],
                "correo": request.form["correo"],
                "matricula": request.form["matricula"]
            }
            collection.insert_one(cliente)
            return redirect('/')
        except Exception as e:
            return f"Error al guardar cliente: {str(e)}", 500

    clientes = list(collection.find({}, {"_id": 0}))
    return render_template("index.html", clientes=clientes)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
