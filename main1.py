import pandas as pd
import seaborn as sns
from flask import Flask, request, jsonify
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

df = sns.load_dataset('titanic')

columns_to_drop = ['sibsp', 'parch', 'fare', 'who', 'adult_male', 'deck', 'embark_town', 'alive', 'alone']
df.drop(columns=columns_to_drop, inplace=True)
df = df.dropna(thresh=6)

le_sex = LabelEncoder()
le_embarked = LabelEncoder()
le_class = LabelEncoder()

df['sex'] = le_sex.fit_transform(df['sex'])
df['embarked'] = le_embarked.fit_transform(df['embarked'].astype(str))
df['class'] = le_class.fit_transform(df['class'])

target_column = 'survived'
X = df.drop(target_column, axis=1)
y = df[target_column]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = KNeighborsClassifier(n_neighbors=5)  # Utilisation du modèle KNN avec 5 voisins
model.fit(X_train, y_train)

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Flask API!'})

@app.route('/predict', methods=['GET'])
def predict():
    try:
        input_data = request.args.to_dict()
        # Ensure the correct order and names of features
        input_features = [int(le_sex.transform([input_data['sex']])[0]), float(input_data['age']), int(input_data['pclass']), input_data['embarked'], input_data['class']]
        # Transform categorical features
        input_features[3] = le_embarked.transform([input_features[3]])[0]
        input_features[4] = le_class.transform([input_features[4]])[0]

        predictions = model.predict([input_features])
        accuracy = accuracy_score(y_test, model.predict(X_test))
        response = {
            'predictions': predictions.tolist(),
            'accuracy': accuracy
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
