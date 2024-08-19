import json
import pandas as pd
from transformers import AutoTokenizer, DebertaV2ForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
from sklearn.model_selection import train_test_split
import torch


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

# Tạo dataset cho Hugging Face
train_dataset = Dataset.from_pandas(train_df[['claim', 'context', 'label']])
test_dataset = Dataset.from_pandas(test_df[['claim', 'context', 'label']])

# Tải tokenizer và model
tokenizer = AutoTokenizer.from_pretrained('/root/videberta-base-tokenizer')
model = DebertaV2ForSequenceClassification.from_pretrained('/root/videberta-base-model', num_labels=2)

# Tokenize dữ liệu
def tokenize_function(examples):
    return tokenizer(examples['claim'], examples['context'], truncation=True, padding='max_length', max_length=512)

train_dataset = train_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

# Định nghĩa các tham số huấn luyện
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
)

# Tạo Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)
trainer.train()

predictions = trainer.predict(test_dataset)
pred_labels = torch.argmax(torch.tensor(predictions.predictions), axis=1)

# Lưu dữ liệu vào file CSV
test_df['predicted_label'] = pred_labels.numpy()
train_df.to_csv('train_data.csv', index=False)
test_df.to_csv('test_data_with_predictions.csv', index=False)