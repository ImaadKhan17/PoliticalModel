import torch
import torch.nn as nn
from transformers import AutoModel

class PolitcalModel(nn.Module):
    def __init__(self, model_name, num_classes):
   
        super(PolitcalModel, self).__init__()
        self.model = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(p=0.2)
        self.topic_head = nn.Linear(self.model.config.hidden_size, num_classes )
        self.stance_head = nn.Linear(self.model.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask):
 
        outputs = self.model(input_ids = input_ids, attention_mask = attention_mask)
        
        last_hidden_state = outputs.last_hidden_state
        mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
        masked_embeddings = last_hidden_state * mask
        x = masked_embeddings.sum(dim=1) / mask.sum(dim=1)

        x = self.dropout(x)
 
        topic_logits = self.topic_head(x)

        stance_pred = torch.sigmoid(self.stance_head(x))

        return topic_logits, stance_pred