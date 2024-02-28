import requests
import numpy as np
import json

# Les URLs des modèles
model_urls = [
    "https://27c4-89-30-29-68.ngrok-free.app/predict",
    "https://63bc-89-30-29-68.ngrok-free.app/predict"
]

# Les données d'entrée
input_data = {
    "sex": "male",
    "age": 22,
    "pclass": 3,
    "embarked": "S",
    "class": "Third"
}

# Initialiser les soldes des modèles
model_balances = {url: 1000 for url in model_urls}

def query_models_predictions(input_data, model_urls):
    predictions = []
    for url in model_urls:
        response = requests.get(url, params=input_data)
        prediction = response.json()['predictions'][0]
        predictions.append(prediction)
    return predictions

def query_models_accuracy(input_data, model_urls):
    accuracies = []
    for url in model_urls:
        response = requests.get(url, params=input_data)
        accuracy = response.json()['accuracy']  # Pas besoin d'indexer ici
        accuracies.append(accuracy)
    return accuracies

def update_weights(accuracies, balances):
    performances = [accuracy * balances[url] for accuracy, url in zip(accuracies, model_urls)]
    total_performance = sum(performances)
    weights = [performance / total_performance for performance in performances]
    return weights

def apply_penalties(accuracies, balances, threshold=0.74, penalty=100):
    for accuracy, url in zip(accuracies, model_urls):
        if accuracy < threshold:
            balances[url] -= penalty

def weighted_prediction(predictions, weights):
    return np.dot(predictions, weights)

# Obtenir les prédictions et les précisions de chaque modèle
predictions = query_models_predictions(input_data, model_urls)
accuracies = query_models_accuracy(input_data, model_urls)

# Appliquer des pénalités si nécessaire
apply_penalties(accuracies, model_balances)

# Mettre à jour les poids en fonction des précisions et des soldes
weights = update_weights(accuracies, model_balances)

# Obtenir la prédiction pondérée de consensus
consensus_pred = weighted_prediction(predictions, weights)

print(f'Consensus Prediction: {consensus_pred}')
print(f'Weights: {weights}')
print(f'Model Balances: {model_balances}')

# Sauvegarder les soldes des modèles dans une base de données JSON
with open('model_balances.json', 'w') as f:
    json.dump(model_balances, f)
