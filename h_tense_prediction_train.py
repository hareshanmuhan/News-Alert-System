import numpy as np
import evaluate
from datasets import load_dataset
from transformers import AutoTokenizer, TrainingArguments, AutoModelForSequenceClassification, Trainer


csv_file_path = r"C:\Users\Admin\Downloads\tense - tense.csv (1).csv"
dataset = load_dataset("csv", data_files=csv_file_path, split="train")

label_mapping = {
    'present': 0,
    'future': 1,
    'past': 2,
    'present perfect continuous': 3,
    'future perfect': 4,
    'past perfect': 5,
    'future continuous': 6,
    'past perfect continuous': 7,
    'present continuous': 8,
    'past continuous': 9,
    'future perfect continuous': 10,
    'present perfect': 11}
def encode_labels(examples):
    examples['labels'] = label_mapping[examples['labels']]
    return examples

dataset = dataset.map(encode_labels)


split_datasets = dataset.train_test_split(test_size=0.2)
train_dataset = split_datasets["train"]
eval_dataset = split_datasets["test"]

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=len(label_mapping))

def tokenize_function(examples):
    return tokenizer(examples["sentence"], padding="max_length", truncation=True)

tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
tokenized_eval_dataset = eval_dataset.map(tokenize_function, batched=True)

tokenized_train_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])
tokenized_eval_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

training_args = TrainingArguments(
    output_dir="test_trainer/test_trainer",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    weight_decay=0.01,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    load_best_model_at_end=True,
    metric_for_best_model='accuracy',
)

metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = metric.compute(predictions=predictions, references=labels)
    return accuracy

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_eval_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()

model_path = r"D:\content deadline\04062024\test_trainer\model-3"
model.save_pretrained(model_path)
tokenizer.save_pretrained(model_path)
