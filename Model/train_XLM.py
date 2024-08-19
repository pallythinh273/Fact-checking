import json
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification, AdamW
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import numpy as np


# Đọc file JSON
def load_data_from_json(path):
    with open(path, 'r') as f:
        data = json.load(f)

    return data

def save_data_to_json(data, path):
    with open(path, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)
        
data = load_data_from_json("/root/final_data_new.json")
context_data = load_data_from_json("/root/merged_data_file.json")

# Gộp dữ liệu
for item in data:
    context_id = item['metadata']['context_id']
    if context_id in context_data:
        item['context'] = context_data[context_id]['context']

# Chuyển đổi thành DataFrame
df = pd.DataFrame(data)
# Xáo trộn dữ liệu
df = df.sample(frac=1).reset_index(drop=True)

# Chuyển đổi label thành số
label_map = {"HỖ TRỢ": 0, "PHỦ NHẬN": 1}
df['label'] = df['metadata'].apply(lambda x: label_map[x['label']])

# Chia dữ liệu thành tập huấn luyện và tập kiểm tra
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
train_df = train_df.reset_index(drop=True)
test_df = test_df.reset_index(drop=True)


# Định nghĩa Dataset
class ClaimDataset(Dataset):
    def __init__(self, claims, contexts, labels, tokenizer, max_len):
        self.claims = claims
        self.contexts = contexts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
    
    def __len__(self):
        return len(self.claims)
    
    def __getitem__(self, item):
        claim = str(self.claims[item])
        context = str(self.contexts[item])
        label = self.labels[item]

        encoding = self.tokenizer.encode_plus(
            claim,
            context,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=True,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )

        return {
            'claim_text': claim,
            'context_text': context,
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'token_type_ids': encoding['token_type_ids'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

# Khởi tạo tokenizer và model
tokenizer = XLMRobertaTokenizer.from_pretrained('xlm-roberta-base')
model = XLMRobertaForSequenceClassification.from_pretrained('xlm-roberta-base', num_labels=2)

# Tạo datasets
MAX_LEN = 512
train_dataset = ClaimDataset(
    claims=train_df.claim.to_numpy(),
    contexts=train_df.context.to_numpy(),
    labels=train_df.label.to_numpy(),
    tokenizer=tokenizer,
    max_len=MAX_LEN
)

test_dataset = ClaimDataset(
    claims=test_df.claim.to_numpy(),
    contexts=test_df.context.to_numpy(),
    labels=test_df.label.to_numpy(),
    tokenizer=tokenizer,
    max_len=MAX_LEN
)

# Tạo dataloaders
BATCH_SIZE = 5
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

# Chuẩn bị training
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

optimizer = AdamW(model.parameters(), lr=2e-5, correct_bias=False)
total_steps = len(train_loader) * 3  # number of epochs
scheduler = torch.optim.lr_scheduler.LinearLR(optimizer, total_iters=total_steps)

# Hàm training
def train_epoch(model, data_loader, optimizer, device, scheduler):
    model.train()
    losses = []
    for batch in data_loader:
        optimizer.zero_grad()
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        scheduler.step()
        losses.append(loss.item())
    return np.mean(losses)

# Hàm evaluation
def eval_model(model, data_loader, device):
    model.eval()
    predictions = []
    actual_labels = []
    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            outputs = model(input_ids, attention_mask=attention_mask)
            _, preds = torch.max(outputs.logits, dim=1)
            predictions.extend(preds.cpu().tolist())
            actual_labels.extend(labels.cpu().tolist())
    return accuracy_score(actual_labels, predictions), classification_report(actual_labels, predictions), predictions

# Training loop
EPOCHS = 3
for epoch in range(EPOCHS):
    print(f'Epoch {epoch + 1}/{EPOCHS}')
    train_loss = train_epoch(model, train_loader, optimizer, device, scheduler)
    print(f'Train loss: {train_loss}')
    
    accuracy, report, predictions = eval_model(model, test_loader, device)
    print(f'Test Accuracy: {accuracy}')
    print(f'Classification Report:\n{report}')

# Lưu model
# torch.save(model.state_dict(), 'xlm_roberta_claim_classifier.pt')

# Lưu dữ liệu vào file CSV
test_df['predicted_label'] = predictions
train_df.to_csv('train_data.csv', index=False)
test_df.to_csv('test_data_with_predictions.csv', index=False)