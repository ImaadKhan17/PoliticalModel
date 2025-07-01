import torch
from torch import nn
from transformers import AutoTokenizer, AutoModel
import pickle
from sklearn.preprocessing import LabelEncoder

# Constants
MODEL_NAME = "allenai/longformer-base-4096"
NUM_CLASSES = 199
MAX_LENGTH = 1028
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load label encoder
with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# Define the model
class PoliticalModel(nn.Module):
    def __init__(self, model_name, num_classes):
        super(PoliticalModel, self).__init__()
        self.model = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(p=0.2)
        self.topic_head = nn.Linear(self.model.config.hidden_size, num_classes)
        self.stance_head = nn.Linear(self.model.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask):
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden_state = outputs.last_hidden_state
        mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
        masked_embeddings = last_hidden_state * mask
        x = masked_embeddings.sum(dim=1) / mask.sum(dim=1)
        x = self.dropout(x)
        topic_logits = self.topic_head(x)
        stance_pred = self.stance_head(x)
        return topic_logits, stance_pred

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = PoliticalModel(MODEL_NAME, NUM_CLASSES).to(DEVICE)
model.load_state_dict(torch.load("best_model.pt", map_location=DEVICE))
model.eval()

# Prediction function
def predict(text):
    encoded = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors='pt'
    )
    input_ids = encoded["input_ids"].to(DEVICE)
    attention_mask = encoded["attention_mask"].to(DEVICE)

    with torch.no_grad():
        topic_logits, stance_output = model(input_ids=input_ids, attention_mask=attention_mask)

    # Topic prediction
    topic_class = torch.argmax(topic_logits, dim=1).item()
    topic_label = label_encoder.inverse_transform([topic_class])[0]

    # Stance prediction (rescale from [0, 1] to [-1, 1])
    stance_score = ((stance_output.item() * 2) - 1)*10

    return {
        "topic": topic_label,
        "stance": stance_score
    }

# Example usage
if __name__ == "__main__":
    result = predict("To give everyone free money")
    print("Predicted Topic:", result["topic"])
    print("Predicted Stance (from -1 to 1):", result["stance"])


result = predict("To give everyone free money")
print(result)
# Output:
# Predicted Topic: U.S. Banking System and Financial Institution Regulation
# Predicted Stance (from -1 to 1): -0.17(Liberal)