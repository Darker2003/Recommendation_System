from .config_train import *
from .load_data import *

# Fine-tuning BERT for token classification
model = BertForTokenClassification.from_pretrained(
    # "bert-base-multilingual-cased",
    pretrain_model_name,
    num_labels=len(tag2idx),
    output_attentions = False,
    output_hidden_states = False
)
model.to(device)

