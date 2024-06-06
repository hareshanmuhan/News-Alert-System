import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_path = r"D:\content deadline\04062024\test_trainer\model-3"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

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
    'present perfect': 11,
}
inv_label_mapping = {v: k for k, v in label_mapping.items()}

# Real-time inference
while True:
    user_input = input("Enter a sentence to predict its tense: ")
    if user_input.lower() == 'exit':
        break

    inputs = tokenizer(user_input, return_tensors="pt")

    with torch.no_grad():
        logits = model(**inputs).logits

    predicted_class_id = logits.argmax().item()
    predicted_label = inv_label_mapping[predicted_class_id]

    print(f"Tense: {predicted_label}")
