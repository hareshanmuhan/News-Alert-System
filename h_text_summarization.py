# from transformers import PegasusTokenizer, PegasusForConditionalGeneration
#
# model_name = "human-centered-summarization/financial-summarization-pegasus"
# tokenizer = PegasusTokenizer.from_pretrained(model_name)
# model = PegasusForConditionalGeneration.from_pretrained(model_name)
#
# while True:
#     text_to_summarize = input("Enter text to summarize: ")
#     if text_to_summarize == 0:
#         break
#
#
#     input_ids = tokenizer(text_to_summarize, return_tensors="pt").input_ids
#
#     output = model.generate(
#         input_ids,
#         max_length=10,
#         num_beams=5,
#         early_stopping=True
#     )
#
#     print("Generated Summary:", tokenizer.decode(output[0], skip_special_tokens=True))

from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

while True:
    ARTICLE = input("Enter text to summarize: ")

    if ARTICLE.lower() == 'exit':
        print("Exiting the summarization tool.")
        break

    summary = summarizer(ARTICLE, max_length=150, min_length=17, do_sample=False)
    print("Generated Summary:", summary[0]['summary_text'])
