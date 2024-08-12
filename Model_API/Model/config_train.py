import json
import random
from collections import defaultdict

import matplotlib.pyplot as plt
import torch
from sklearn.metrics import f1_score
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

# Pretrained model
pretrain_model_name = "vinai/phobert-base-v2"
tokenizer = AutoTokenizer.from_pretrained(pretrain_model_name)

# Hyperparameters for training
batch_size = 64  # Number of samples per batch
epochs = 50  # Number of training epochs
device = "cuda" if torch.cuda.is_available() else "cpu"  # Check if GPU is available
lr = 5e-5
eps = 1e-8
weight_decay= 1e-5

# Paths for saving the trained model and test response tags
model_saved_path = "Model_API\Saved_Model\key_ner_new_data_method"
save_respone_tags_path = "Datasets/Query/answer_test.json"

