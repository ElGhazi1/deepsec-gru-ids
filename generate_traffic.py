# generate_traffic.py
import pandas as pd
import random
import time
import json
import requests

FEATURES = [
    "Flow_Duration", "Tot_Fwd_Pkts", "Tot_Bwd_Pkts", "TotLen_Fwd_Pkts",
    "TotLen_Bwd_Pkts", "Fwd_Pkt_Len_Max", "Fwd_Pkt_Len_Std", "Bwd_Pkt_Len_Max",
    "Bwd_Pkt_Len_Std", "Flow_Byts/s", "Flow_Pkts/s", "Flow_IAT_Mean",
    "Flow_IAT_Std", "Fwd_IAT_Tot", "Fwd_IAT_Mean", "Fwd_IAT_Std", "Fwd_IAT_Min",
    "Bwd_IAT_Std", "Bwd_PSH_Flags", "Bwd_URG_Flags", "Bwd_Pkts/s",
    "Pkt_Len_Std", "FIN_Flag_Cnt", "SYN_Flag_Cnt", "RST_Flag_Cnt",
    "ACK_Flag_Cnt", "CWE_Flag_Count", "ECE_Flag_Cnt", "Down/Up_Ratio",
    "Init_Bwd_Win_Byts", "Active_Mean", "Active_Std", "Protocol_enc"
]

API_URL = "http://127.0.0.1:8000/preprocess_and_predict"

def generate_packet(label=0):
    packet = [random.uniform(0, 1) * (10 + label * random.uniform(1, 20)) for _ in range(len(FEATURES)-1)]
    packet.append(random.choice([0, 1, 2]))  # Protocol_enc
    return dict(zip(FEATURES, packet))

def stream_packets():
    buffer = []
    while True:
        packet = generate_packet(random.choice([0, 1]))
        buffer.append(packet)

        if len(buffer) >= 10:  # séquence complète
            try:
                response = requests.post(API_URL, json={'sequence': buffer})
                print("📡 Prédiction reçue :", response.json())
            except Exception as e:
                print("Erreur:", e)
            buffer.pop(0)  # glissement de fenêtre

        time.sleep(1)  # 1 seconde entre chaque paquet

if __name__ == "__main__":
    stream_packets()
