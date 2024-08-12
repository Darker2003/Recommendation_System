from .config_train import *
from .DataProcessing import read_input
from .load_data import *


class Key_Ner_Predictor:
    def __init__(self, model_path, tokenizer, device, tag_map):
        """
        Initialize the Key_Ner_Predictor with the model, tokenizer, and device.

        Args:
            model_path (str): Path to the pre-trained model.
            tokenizer (BertTokenizer): Tokenizer to process input sentences.
            device (torch.device): Device to run the model on.
            tag_map (Dict[int, str]): Mapping of indices to tags.
        """
        self.model = BertForTokenClassification.from_pretrained(model_path).to(device)
        self.tokenizer = tokenizer
        self.device = device
        self.tag_map = tag_map

    def predict(self, sentence):
        """
        Predict the tags for each token in the given sentence.

        Args:
            sentence (str): Input sentence to predict.

        Returns:
            Tuple[str, List[str]]: The original sentence and its predicted tags.
        """
        # Process the sentence
        sentence = read_input(sentence)

        # Tokenize the sentence
        input_ids = self.tokenizer.encode(sentence, return_tensors="pt").to(self.device)

        # Create attention masks
        attention_masks = (input_ids != self.tokenizer.pad_token_id).float().to(self.device)

        # Set model to evaluation mode
        self.model.eval()

        with torch.no_grad():
            # Forward pass
            outputs = self.model(input_ids, token_type_ids=None, attention_mask=attention_masks)
            logits = outputs.logits

        # Get predicted tags for each token in the sentence
        predicted_tags = torch.argmax(logits, dim=2).cpu().numpy()[0]

        # Map indices to tags
        predicted_tags = [self.tag_map[idx] for idx in predicted_tags]
        predicted_tags = set(predicted_tags)
        predicted_tags.remove('<pad>')
        predicted_tags = list(predicted_tags)

        return self.tokenizer.decode(input_ids[0], skip_special_tokens=True), predicted_tags


# Initialize the Key_Ner_Predictor
predictor = Key_Ner_Predictor(
    model_path=model_saved_path,
    tokenizer=tokenizer,
    device=device,
    tag_map=dict(enumerate(sorted_tags))
)

# # Define the sentence to predict
# sentence = "Tôi muốn đi cắm trại ngắm hoàng hôn trên biển cùng gia đình"

# # Get the prediction
# original_sentence, predicted_tags = predictor.predict(sentence)

# # Print the sentence and its predicted tags
# print("Sentence:", original_sentence)
# print("Predicted Tags:", predicted_tags)

