import pandas as pd
import seaborn as sns
from flask import Flask, request, jsonify
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# Chargement du jeu de données Titanic
df = sns.load_dataset('titanic')

# Suppression des colonnes inutiles
columns_to_drop = ['sibsp', 'parch', 'fare', 'who', 'adult_male', 'deck', 'embark_town', 'alive', 'alone']
df.drop(columns=columns_to_drop, inplace=True)
df = df.dropna(thresh=6)

# Encodage des caractéristiques catégorielles
le_sex = LabelEncoder()
le_embarked = LabelEncoder()
le_class = LabelEncoder()

df['sex'] = le_sex.fit_transform(df['sex'])
df['embarked'] = le_embarked.fit_transform(df['embarked'].astype(str))
df['class'] = le_class.fit_transform(df['class'])

# Définition de la colonne cible et des caractéristiques
target_column = 'survived'
X = df.drop(target_column, axis=1)
y = df[target_column]

# Division du jeu de données
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialisation du modèle KNN
model = KNeighborsClassifier(n_neighbors=5)  # Utilisation du modèle KNN avec 5 voisins
model.fit(X_train, y_train)

# Initialisation de l'application Flask
app = Flask(__name__)

# Définition de la route d'accueil
@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Flask API with KNN!'})

# Définition de la route de prédiction
@app.route('/predict', methods=['GET'])
def predict():
    try:
        input_data = request.args.to_dict()
        # Assurez-vous de l'ordre correct et des noms des caractéristiques
        input_features = [int(le_sex.transform([input_data['sex']])[0]), float(input_data['age']), int(input_data['pclass']), input_data['embarked'], input_data['class']]
        # Transformation des caractéristiques catégorielles
        input_features[3] = le_embarked.transform([input_features[3]])[0]
        input_features[4] = le_class.transform([input_features[4]])[0]

        # Prédictions à l'aide du modèle
        predictions = model.predict([input_features])
        accuracy = accuracy_score(y_test, model.predict(X_test))
        
        # Création d'une réponse avec les prédictions et la précision du modèle
        response = {
            'predictions': predictions.tolist(),
            'accuracy': accuracy
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)})

# Exécution de l'application si ce script est exécuté
if __name__ == '__main__':
    app.run(debug=True)
