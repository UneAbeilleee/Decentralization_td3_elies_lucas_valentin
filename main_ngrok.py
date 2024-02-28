import pandas as pd
import seaborn as sns
from flask import Flask, request, jsonify
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# Load Titanic dataset
df = sns.load_dataset('titanic')

# Drop unnecessary columns
columns_to_drop = ['sibsp', 'parch', 'fare', 'who', 'adult_male', 'deck', 'embark_town', 'alive', 'alone']
df.drop(columns=columns_to_drop, inplace=True)
df = df.dropna(thresh=6)

# Encode categorical features
le_sex = LabelEncoder()
le_embarked = LabelEncoder()
le_class = LabelEncoder()

df['sex'] = le_sex.fit_transform(df['sex'])
df['embarked'] = le_embarked.fit_transform(df['embarked'].astype(str))
df['class'] = le_class.fit_transform(df['class'])

# Define target column and features
target_column = 'survived'
X = df.drop(target_column, axis=1)
y = df[target_column]

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a logistic regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'Model Accuracy: {accuracy}')

# Initialize Flask app
app = Flask(__name__)

# Define home route
@app.route('/27c4-89-30-29-68/')  # Update this with your actual subdomain
def home():
    return jsonify({'message': 'Welcome to the Flask API!'})

# Define predict route
@app.route('/predict', methods=['GET'])  # Update this with your actual subdomain
def predict():
    try:
        input_data = request.args.to_dict()
        # Ensure the correct order and names of features
        input_features = [input_data['sex'], float(input_data['age']), int(input_data['pclass']), input_data['embarked'], input_data['class']]
        # Transform categorical features
        input_features[0] = le_sex.transform([input_features[0]])[0]
        input_features[3] = le_embarked.transform([input_features[3]])[0]
        input_features[4] = le_class.transform([input_features[4]])[0]

        # Make predictions using the model
        predictions = model.predict([input_features])

        # Create a response with predictions and model accuracy
        response = {
            'predictions': predictions.tolist(),
            'accuracy': accuracy
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)})

# Run the app if this script is executed
if __name__ == '__main__':
    app.run(debug=True)
