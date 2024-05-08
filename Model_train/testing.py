from config_train import *
from load_data import *

# Load model and tokenizer
model = BertForTokenClassification.from_pretrained(model_saved_path)
tokenizer = AutoTokenizer.from_pretrained(pretrain_model_name)

model.to(device)
model.eval()

# List to store predicted tags
predicted_tags = []

# Iterate over batches of validation data
for batch in validation_dataloader:
    b_input_ids = batch[0].to(device)
    b_input_mask = batch[1].to(device)
    
    with torch.no_grad():
        # Forward pass
        outputs = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask)
        logits = outputs.logits
    
    # Get predicted tags for each token in the batch
    predicted_batch_tags = torch.argmax(logits, dim=2).cpu().numpy()
    
    # Append predicted tags to the list
    predicted_tags.extend(predicted_batch_tags)

# Convert predicted tags from indices to tag labels
predicted_tags = [[tags[idx] for idx in sequence] for sequence in predicted_tags]

# Print predicted tags for each sentence
json_respone = {}
for sentence, tags in zip(validation_input, predicted_tags):
    sentence = tokenizer.decode(sentence, skip_special_tokens=True)
    tags = set(tags)
    if 'ẩm_thực' not in sentence:
        tags.remove('ẨM THỰC')
    json_respone[sentence] = list(tags)
    print("Sentence:", sentence)
    print("Predicted Tags:", tags)

with open(save_respone_tags_path, 'w', encoding='utf-8') as file:
    json.dump(json_respone, file, ensure_ascii=False)
    print(f"Save: {save_respone_tags_path}")
