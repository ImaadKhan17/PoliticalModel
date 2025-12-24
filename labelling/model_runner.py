from models.final_Longformer_model import PolitcalModel
from transformers import AutoTokenizer, AutoModel
from torch import nn
import torch
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import pickle
import os
from pathlib import Path



class BillLabeler:

    def __init__(self):

        BASE_DIR = Path(__file__).resolve().parent.parent
        MODEL_PATH = BASE_DIR / "best_model.pt"
        ENCODER_PATH = BASE_DIR / "label_encoder.pkl"
        
        with open(ENCODER_PATH, 'rb') as f:
            self.le = pickle.load(f)

        self.model_name = "allenai/longformer-base-4096"
        self.num_classes = 199
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_length = 1028

    
        self.model = PolitcalModel(self.model_name, self.num_classes).to(self.device)
        self.model.load_state_dict(torch.load(MODEL_PATH, map_location=self.device) )


    def predict(self,text):
        try:
            self.model.eval()
            encoded  = self.tokenizer(text, padding="max_length", truncation=True, max_length=self.max_length, return_tensors='pt' )
            input_ids = encoded['input_ids'].to(self.device)
            attention_mask = encoded['attention_mask'].to(self.device)

            with torch.no_grad():
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

            #turn output into 5 most occuring categories, weighted(remove one's less than 0.05)
            probs = torch.softmax(outputs[0], dim =1)
            topk_vals, topk_idx = torch.topk(probs, k=5, dim=1)
            issues = {
                self.le.inverse_transform([topk_idx[0][i].item()])[0]: topk_vals[0][i].item()
                for i in range(4)
    
            }
            #cleanup
            topk_idx = topk_idx.cpu()
            topk_vals = topk_vals.cpu()

            #change stance back from 0 <-> 1 to -1<->1
            stance = (outputs[1]*2)-1

            return_info = {
                "bill_text": text,
                "sub_topics": issues,
                "ideology_stance":stance
            }

            return return_info
        except Exception as e:
            print(f"Caught an error: {e}")