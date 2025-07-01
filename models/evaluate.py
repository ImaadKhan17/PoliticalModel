import torch
import tqdm

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

