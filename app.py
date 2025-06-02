
from flask import Flask, render_template, request, redirect
from azure.identity import DefaultAzureCredential
from pymongo import MongoClient
import os

app = Flask(__name__)
app.config["DEBUG"] = True

def get_collection():
    try:
        MONGO_HOST = os.getenv("COSMOS_HOST")
        if not MONGO_HOST:
            raise ValueError("COSMOS_HOST not set")
        
        print("[INFO] Obteniendo token de Azure...")
        credential = DefaultAzureCredential()
        token = credential.get_token("https://cosmos.azure.com/.default")
        print("[INFO] Token obtenido. Conectando a MongoClient...")

        client = MongoClient(
            f"mongodb://{MONGO_HOST}:10255/?ssl=true&replicaSet=globaldb",
            username="",
            password=token.token,
            authMechanism="MONGODB-AWS",
            authSource="$external"
        )

        db = client["clientesdb"]
        print("[INFO] Conexión exitosa a MongoClient.")
        return db["clientes"]
    
    except Exception as e:
        print(f"[ERROR] Fallo al conectar con Cosmos DB: {str(e)}")
        return None

@app.route('/', methods=["GET", "POST"])
def index():
    try:
        print("[INFO] Entrando a ruta /")
        collection = get_collection()
        if not collection:
            print("[ERROR] Colección no disponible.")
            return "Error conectando a la base de datos.", 500

        if request.method == "POST":
            print("[INFO] Recibida solicitud POST con data:", request.form.to_dict())
            cliente = {
                "id": request.form.get("id", "N/A"),
                "nombre": request.form.get("nombre", "N/A"),
                "correo": request.form.get("correo", "N/A"),
                "matricula": request.form.get("matricula", "N/A")
            }
            collection.insert_one(cliente)
            print("[INFO] Cliente insertado correctamente.")
            return redirect('/')

        clientes = list(collection.find({}, {"_id": 0}))
        print(f"[INFO] Renderizando index.html con {len(clientes)} clientes.")
        return render_template("index.html", clientes=clientes)
    
    except Exception as e:
        print(f"[ERROR] Fallo general en index(): {str(e)}")
        return f"Error inesperado: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO] Ejecutando en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
