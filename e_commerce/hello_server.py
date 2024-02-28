from flask import Flask

# Initialisation de l'application Flask
app = Flask(__name__)

# Définition de la route d'accueil
@app.route('/')
def hello_world():
    return 'Hello, World!'

# Exécution de l'application si ce script est exécuté
if __name__ == '__main__':
    app.run(debug=True)
