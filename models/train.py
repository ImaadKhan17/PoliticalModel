import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from final_Longformer_model import PolitcalModel  #  custom model

# Load dataset and drop unnecessary column
df = pd.read_csv("/content/drive/MyDrive/datasets/combined.csv")
df.drop(columns={'Unnamed: 0'}, inplace=True)

# Normalize stance values from [-1, 1] to [0, 1]
df['nominate_mid_1'] = (df['nominate_mid_1'] + 1) / 2

# Initialize tokenizer for Longformer model
tokenizer = AutoTokenizer.from_pretrained("allenai/longformer-base-4096")

# Encode string topic labels into integers
le = LabelEncoder()
df['label'] = le.fit_transform(df['topic'])

model_name = "allenai/longformer-base-4096"
num_classes = 199
device = torch.device("cuda")
max_length = 1028  # max input tokens for Longformer
learning_rate = 2e-5
batch_size = 2
num_epochs = 4

class BillDataset(Dataset):
    def __init__(self, data, tokenizer, max_length=4096):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.labels = list(data["label"])
        self.stances = list(data["nominate_mid_1"])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # Combine title and summary into one input string
        text = f"Title: {self.data.iloc[idx]['title']} Summary: {self.data.iloc[idx]['summary']}"
        encoded = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt'
        )
        # Return inputs and labels as tensors
        return {
            'input_ids': encoded['input_ids'].squeeze(0),
            'attention_mask': encoded['attention_mask'].squeeze(0),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long),
            'stance': torch.tensor(self.stances[idx], dtype=torch.float)
        }

    def get_title(self, idx):
        return str(self.data.iloc[idx]['title'])


# Split dataset into train and validation sets (80/20 split)
train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)

# Create Dataset objects for training and validation
train_dataset = BillDataset(train_df, tokenizer, max_length)
val_dataset = BillDataset(val_df, tokenizer, max_length)

# DataLoaders provide batching and shuffling for training
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

# Initialize model and move to device(usually GPU)
model = PolitcalModel(model_name, num_classes).to(device)

# Setup optimizer and learning rate scheduler
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', factor=0.3, patience=1)

# Loss functions for classification and regression tasks
topic_loss_fn = nn.CrossEntropyLoss()
stance_loss_fn = nn.MSELoss()

def train(model, data_loader, optimizer, device):
    model.train()
    for i, batch in enumerate(tqdm(data_loader, desc='Training', dynamic_ncols=True)):
        optimizer.zero_grad()

        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        stances = batch['stance'].to(device)

        # Forward pass: get both topic logits and stance prediction
        topic_logits, stance_pred = model(input_ids, attention_mask)

        # Compute losses
        topic_loss = topic_loss_fn(topic_logits, labels)
        stance_loss = stance_loss_fn(stance_pred.squeeze(), stances)
        loss = topic_loss + stance_loss

        loss.backward()
        optimizer.step()

        # Print loss every 500 steps
        if (i + 1) % 500 == 0:
            print(f"Step {i+1}, Loss: {loss.item():.4f}")

def validate(model, data_loader, device):
    model.eval()
    total_loss = 0
    total_correct = 0
    total_samples = 0
    total_mae = 0  # mean absolute error for stance regression

    with torch.no_grad():
        for batch in tqdm(data_loader, desc='Validating', dynamic_ncols=True):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            stances = batch['stance'].to(device)

            topic_logits, stance_pred = model(input_ids, attention_mask)

            # Calculate accuracy for topic classification
            topic_preds = topic_logits.argmax(dim=1)
            total_correct += (topic_preds == labels).sum().item()
            total_samples += labels.size(0)

            # Calculate MAE for stance prediction
            stance_pred = stance_pred.squeeze()
            total_mae += torch.abs(stance_pred - stances).sum().item()

            # Sum classification and regression losses
            topic_loss = topic_loss_fn(topic_logits, labels)
            stance_loss = stance_loss_fn(stance_pred, stances)
            total_loss += (topic_loss + stance_loss).item()

    avg_loss = total_loss / len(data_loader)
    accuracy = total_correct / total_samples
    avg_mae = total_mae / total_samples

    return avg_loss, accuracy, avg_mae


best_val_loss = float('inf')

for epoch in range(num_epochs):
    print(f"Epoch {epoch + 1}/{num_epochs}")
    train(model, train_loader, optimizer, device)
    validation_loss, val_acc, val_mae = validate(model, val_loader, device)
    print(f"Val Loss: {validation_loss:.4f} | Accuracy: {val_acc:.4f} | MAE: {val_mae:.4f}")

    # Save best model weights
    if validation_loss < best_val_loss:
        best_val_loss = validation_loss
        torch.save(model.state_dict(), "/content/drive/MyDrive/datasets/best_model.pt")

    # Save checkpoint every epoch
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'accuracy_class': val_acc,
        'mae': val_mae
    }, "/content/drive/MyDrive/datasets/checkpoint.pth")

    scheduler.step(validation_loss)

# Save final model after training
torch.save(model.state_dict(), '/content/drive/MyDrive/datasets/final_model.pth')
