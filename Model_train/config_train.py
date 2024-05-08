import json

import torch
from sklearn.model_selection import train_test_split
from torch.nn.functional import pad
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import (DataLoader, RandomSampler, SequentialSampler,
                              TensorDataset)
from tqdm import tqdm
from transformers import (AdamW, AutoTokenizer, BertForTokenClassification,
                          get_linear_schedule_with_warmup)

# Assuming the JSON data is stored in a file named 'data.json'
DEFAULT_TEXT_ANNOTATION_FILE = "Datasets/Query/datasets_text.json"

#Pretrained model
pretrain_model_name = "vinai/phobert-base-v2"
tokenizer = AutoTokenizer.from_pretrained(pretrain_model_name)

batch_size = 64
epochs = 50
device = "cuda" if torch.cuda.is_available() else "cpu"

model_saved_path = "Saved_Model/key_ner"

save_respone_tags_path = "Datasets/Query/answer_test.json"
