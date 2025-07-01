from transformers import BertTokenizer, TFBertModel, TFBertForSequenceClassification
import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset
import tensorflow as tf 
import numpy as np
from sklearn.preprocessing import LabelEncoder
import multiprocessing
import pickle

df = pd.read_csv("datasets/combined_bills.csv")

# Encode labels
label_encoder = LabelEncoder()
label_encoder.fit(df['Minor'])
df['Minor_Encoded'] = label_encoder.transform(df['Minor'])

# Save encoder for future use
with open("label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

df = df[["Title", "Minor_Encoded"]]
df.rename(columns={"Title": "title", "Minor_Encoded": "minor_encoded"}, inplace=True)

# Convert to HuggingFace Dataset
data = df.to_dict(orient="records")
dataset = Dataset.from_list(data)
dataset = dataset.train_test_split(test_size=0.2)

# Load BERT and tokenizer
bert_model = TFBertModel.from_pretrained('bert-base-uncased')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

def tokenize(data):
    return tokenizer(data["title"], padding="max_length", truncation=True)

# Tokenize with multiprocessing
num_cores = multiprocessing.cpu_count()
tokenized_dataset = dataset.map(tokenize, batched=True, batch_size=16, load_from_cache_file=True)

# Format for TensorFlow
tokenized_dataset.set_format('tf', 
    columns=['input_ids', 'attention_mask', 'token_type_ids', 'minor_encoded'])

BATCH_SIZE = 64

def order(inp):
    # Reorder inputs for model input + label
    data = list(inp.values())
    return {
        'input_ids': data[1],
        'attention_mask': data[2],
        'token_type_ids': data[3]
    }, data[0]

# Build train dataset
train_dataset = tf.data.Dataset.from_tensor_slices(tokenized_dataset['train'][:])
train_dataset = train_dataset.batch(BATCH_SIZE).shuffle(1000)
train_dataset = train_dataset.map(order, num_parallel_calls=tf.data.AUTOTUNE)

# Build test dataset
test_dataset = tf.data.Dataset.from_tensor_slices(tokenized_dataset['test'][:])
test_dataset = test_dataset.batch(BATCH_SIZE)
test_dataset = test_dataset.map(order, num_parallel_calls=tf.data.AUTOTUNE)

# Custom BERT classifier
class BERTForClassification(tf.keras.Model):
    def __init__(self, bert_model, num_classes):
        super().__init__()
        self.bert = bert_model
        self.fc = tf.keras.layers.Dense(num_classes, activation='softmax')

    def call(self, inputs):
        x = self.bert(inputs)[1]  # Use pooled output
        return self.fc(x)

# Compile model
classifier = BERTForClassification(bert_model, num_classes=232)
classifier.compile(
    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss = tf.keras.losses.SparseCategoricalCrossentropy(),
    metrics = ['accuracy']
)
