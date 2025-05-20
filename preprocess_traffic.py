from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pickle, json, os
import tensorflow as tf
import uvicorn
import pandas as pd
import socket

# Configuration Logstash
LOGSTASH_HOST = '127.0.0.1'
LOGSTASH_PORT = 5000  # Assure-toi que Logstash écoute sur ce port

app = FastAPI()
DEPLOY = 'deployment'
SEQ_LEN = 10

# Chargement du modèle et des outils
model = tf.keras.models.load_model(os.path.join(DEPLOY, 'gru_model.keras'))
with open(os.path.join(DEPLOY, 'scaler.pkl'), 'rb') as f: scaler = pickle.load(f)
with open(os.path.join(DEPLOY, 'protocol_encoder.pkl'), 'rb') as f: proto_le = pickle.load(f)
with open(os.path.join(DEPLOY, 'features.json')) as f: feat_info = json.load(f)
FEATURES = feat_info['feature_columns']

class SequenceInput(BaseModel):
    sequence: list

def send_to_logstash(message: dict):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
        sock.connect((LOGSTASH_HOST, LOGSTASH_PORT))
        json_message = json.dumps(message) + '\n'
        sock.sendall(json_message.encode('utf-8'))
        sock.close()
    except Exception as e:
        print(f"Erreur d'envoi à Logstash : {e}")

@app.post("/preprocess_and_predict")
async def preprocess_and_predict(payload: SequenceInput):
    try:
        df = pd.DataFrame(payload.sequence)
        X = df[FEATURES]
        X_scaled = scaler.transform(X)
        X_seq = np.expand_dims(X_scaled, axis=0)

        prob = float(model.predict(X_seq)[0])
        pred = int(prob > 0.5)
        label = "Anomalie" if pred else "Normal"

        log_data = {
            "prediction": label,
            "probability": round(prob, 4),
            "input": payload.sequence
        }

        send_to_logstash(log_data)
        return log_data
    except Exception as e:
        error_message = {"error": str(e)}
        send_to_logstash(error_message)
        return error_message

if __name__ == "__main__":
    uvicorn.run("preprocess_traffic:app", host="127.0.0.1", port=8000)
