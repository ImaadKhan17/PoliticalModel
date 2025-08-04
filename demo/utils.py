import streamlit as st
import torch
from model import PolitcalModel
from transformers import AutoTokenizer
import pickle
import json
import gdown
import os


BASE_DIR = os.path.dirname(__file__)

model_path = os.path.join(BASE_DIR, 'model.pth')
if not os.path.exists(model_path):
    url = "https://drive.google.com/uc?id=1k0RxLq33219ElJvv8D63Ee3kUwbzRzpt"
    gdown.download(url, model_path, quiet=False)

model_name = "allenai/longformer-base-4096"
num_classes = 187
tokenizer = AutoTokenizer.from_pretrained(model_name)
max_length = 1028
device = "cpu"

mappings_path = os.path.join(BASE_DIR, "mappings.json")
with open(mappings_path, "r") as file:
    mappings = json.load(file)

label_encoder_path = os.path.join(BASE_DIR, "label_encoder.pkl")
with open(label_encoder_path, 'rb') as f:
    le = pickle.load(f)

@st.cache_resource
def load_model():
    model = PolitcalModel(model_name, num_classes).to(device)
    model.load_state_dict(
        torch.load(model_path, map_location="cpu", weights_only=False)
    )
    model.eval()
    return model

model = load_model()

def map_preds(preds):
    label, stance = str(preds[0]), preds[1]
    major, minor, leaning = None, None, None

    for i in mappings:
        sub_keys = mappings[i]
        if label in sub_keys['Subtopics']:
            major = sub_keys['Major']
            minor = sub_keys['Subtopics'][label]
            break

    if -0.167 <= stance <= 0.025:
        leaning = "Centrist"
    elif stance < -0.167:
        leaning = "Liberal"
    else:
        leaning = "Conservative"

    return major, minor, leaning, stance

def predict(text):
    encoded = tokenizer(text, padding="max_length", truncation=True, max_length=max_length, return_tensors='pt')
    input_ids = encoded['input_ids'].to(device)
    attention_mask = encoded['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    _, pred = torch.max(outputs[0], dim=1)
    stance = outputs[1].item()
    label, stance = le.inverse_transform([pred.item()]), (stance * 2) - 1

    return map_preds((label[0], stance))
