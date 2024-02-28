from flask import Flask, jsonify

# Initialisation de l'application Flask
app = Flask(__name__)

# Définition de la route /getServer pour les méthodes GET, POST, PUT, DELETE
@app.route('/getServer', methods=['GET', 'POST', 'PUT', 'DELETE'])
def get_server():
    hostname = 'localhost'  # Utiliser 'localhost' au lieu de socket.gethostname()
    port = 5000  # Changer le port si nécessaire
    server_url = f"{hostname}:{port}"
    response = {"code": 200, "server": server_url}
    return jsonify(response)

# Exécution de l'application si ce script est exécuté
if __name__ == '__main__':
    app.run(debug=True)
