from torch import nn
from transformers import AutoTokenizer, AutoModel

class PolitcalModel(nn.Module):
    def __init__(self, model_name, num_classes):
        """
        Initialize transformer backbone, dropout, 
        and two heads: topic classification and stance regression.
        """
        super().__init__()
        self.model = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.2)
        self.topic_head = nn.Linear(self.model.config.hidden_size, num_classes)
        self.stance_head = nn.Linear(self.model.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask):
        """
        Forward pass: mean-pool transformer outputs, apply dropout,
        then pass to classification and regression heads.
        """
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        x = outputs.last_hidden_state.mean(dim=1)  # mean pooling
        x = self.dropout(x)
        return self.topic_head(x), self.stance_head(x)
