from .config_train import *

with open(DEFAULT_TEXT_ANNOTATION_FILE, 'r', encoding='utf-8') as file:
    data = json.load(file)
    
# Prepare sentences and labels
sentences = [item[0] for item in data["annotations"]]
"""
List[str]: A list of sentences extracted from the dataset.
Each sentence corresponds to an annotation in the dataset.
"""

labels = [item[1]['entities'] for item in data["annotations"]]
"""
List[List[Tuple[str, str]]]: A list of entity labels for each sentence.
Each label is a tuple containing the entity text and its corresponding tag.
"""

# Define tags
tags = data["classes"]
"""
List[str]: A list of all possible entity tags (classes) in the dataset.
These tags will be used to label the tokens in each sentence.
"""

# Convert tags to indices
tag2idx = {tag: 0 for idx, tag in enumerate(tags)}
for label in labels:
    for entity in label:
        tag2idx[entity[1]] = tag2idx[entity[1]] + 1
# Sort the dictionary by values
sorted_tags = dict(sorted(tag2idx.items(), key=lambda item: item[1],reverse=True))
sorted_tags = {key: value for key, value in sorted_tags.items() if value != 0}

new_tag = {'<pad>': 0}

sorted_tags = {**new_tag, **sorted_tags}

# Convert tags to indices
tag2idx = {tag: idx for idx, tag in enumerate(list(sorted_tags.keys()))}
"""
Dict[str, int]: A dictionary mapping each tag to a unique index.
This is used to convert tag labels into numerical format for model training.
"""

# Count the occurrences of each tag
tag_counts = defaultdict(int)
for item in data["annotations"]:
    for entity in item[1]["entities"]:
        tag_counts[entity[1]] += 1

# Create a list of annotations for each tag
tag_annotations = defaultdict(list)
for item in data["annotations"]:
    for entity in item[1]["entities"]:
        tag_annotations[entity[1]].append(item)

# Split the annotations for each tag into training and testing sets
train_annotations = []
test_annotations = []
for tag, annotations in tag_annotations.items():
    random.shuffle(annotations)
    split_point = len(annotations) // 2
    train_annotations.extend(annotations[:split_point])
    test_annotations.extend(annotations[split_point:])

# Prepare training and testing datasets
sentences_train = [item[0] for item in train_annotations]
sentences_test = [item[0] for item in test_annotations]
labels_train = [item[1]['entities'] for item in train_annotations]
labels_test = [item[1]['entities'] for item in test_annotations]

# Encode the sentences and labels into input IDs and tag IDs
input_ids_train = []
tag_ids_train = []
for index in range(len(sentences_train)):
    input_ids = tokenizer.encode(sentences_train[index])  # Tokenize the sentence
    input_ids_train.append(input_ids)

    tag_ids = [0 for ids in input_ids]  # Initialize tag IDs with padding
    for labels in labels_train[index]:
        key_ids = tokenizer.encode(labels[0])  # Encode entity text
        for ids in key_ids[1:len(key_ids)-1]:
            ids = input_ids.index(ids)  # Find the index of the token
            tag_ids[ids] = tag2idx[labels[1]]  # Assign tag ID
    tag_ids_train.append(tag_ids)

input_ids_test = []
tag_ids_test = []
for index in range(len(sentences_test)):
    input_ids = tokenizer.encode(sentences_test[index])  # Tokenize the sentence
    input_ids_test.append(input_ids)

    tag_ids = [0 for ids in input_ids]  # Initialize tag IDs with padding
    for labels in labels_test[index]:
        key_ids = tokenizer.encode(labels[0])  # Encode entity text
        for ids in key_ids[1:len(key_ids)-1]:
            ids = input_ids.index(ids)  # Find the index of the token
            tag_ids[ids] = tag2idx[labels[1]]  # Assign tag ID
    tag_ids_test.append(tag_ids)


"""
padded torch.Tensor: A padded tensor of tag IDs for the training set.
All tag sequences are padded to the same length as their corresponding token sequences.
"""
# Pad sequences
padded_input_ids_train = pad_sequence([torch.tensor(ids) for ids in input_ids_train], batch_first=True, padding_value=0)
# Convert to tensor
input_ids_train= padded_input_ids_train.clone().detach()

# Pad sequences
padded_input_ids_test = pad_sequence([torch.tensor(ids) for ids in input_ids_test], batch_first=True, padding_value=0)
# Convert to tensor
input_ids_test= padded_input_ids_test.clone().detach()

# Pad sequences
padded_tag_ids_train = pad_sequence([torch.tensor(ids) for ids in tag_ids_train], batch_first=True, padding_value=0)

# Convert to tensor
tag_ids_train= padded_tag_ids_train.clone().detach()

# Pad sequences
padded_tag_ids_test = pad_sequence([torch.tensor(ids) for ids in tag_ids_test], batch_first=True, padding_value=0)

# Convert to tensor
tag_ids_test= padded_tag_ids_test.clone().detach()

# Find the maximum sequence length
max_length = max(padded_input_ids_train.size(1), padded_input_ids_train.size(1), padded_tag_ids_train.size(1), padded_tag_ids_test.size(1))
# Pad input_ids and tag_ids to have the same length
padded_input_ids_train = torch.nn.functional.pad(padded_input_ids_train, (0, max_length - padded_input_ids_train.size(1)), value=tokenizer.pad_token_id)
padded_input_ids_test = torch.nn.functional.pad(padded_input_ids_test, (0, max_length - padded_input_ids_test.size(1)), value=tokenizer.pad_token_id)
padded_tag_ids_train = torch.nn.functional.pad(padded_tag_ids_train, (0, max_length - padded_tag_ids_train.size(1)), value=0)
padded_tag_ids_test = torch.nn.functional.pad(padded_tag_ids_test, (0, max_length - padded_tag_ids_test.size(1)), value=0)

# Convert to tensor
input_ids_train = padded_input_ids_train.clone().detach()
tag_ids_train = padded_tag_ids_train.clone().detach()

input_ids_test = padded_input_ids_test.clone().detach()
tag_ids_test = padded_tag_ids_test.clone().detach()

"""
Mask torch.Tensor: A tensor containing the attention masks.
This tensor indicates which tokens are real and which are padding.
"""
attention_masks_train = torch.tensor([[1.0 if i != tokenizer.pad_token_id and i!= tokenizer.cls_token_id and i!= tokenizer.sep_token_id else 0 for i in ii] for ii in input_ids_train])
attention_masks_test = torch.tensor([[1.0 if i != tokenizer.pad_token_id and i!= tokenizer.cls_token_id and i!= tokenizer.sep_token_id else 0 for i in ii] for ii in input_ids_test])

# Convert data to PyTorch tensors
train_inputs = input_ids_train.clone().detach()
validation_inputs = input_ids_test.clone().detach()
train_labels = tag_ids_train.clone().detach()
validation_labels = tag_ids_test.clone().detach()
train_masks = attention_masks_train.clone().detach()
validation_masks = attention_masks_test.clone().detach()

# Create DataLoader for training data
train_data = TensorDataset(train_inputs, train_masks, train_labels)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)

# Create DataLoader for validation data
validation_data = TensorDataset(validation_inputs, validation_masks, validation_labels)
validation_sampler = SequentialSampler(validation_data)
validation_dataloader = DataLoader(validation_data, sampler=validation_sampler, batch_size=batch_size)
