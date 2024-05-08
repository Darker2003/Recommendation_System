from config_train import *

with open(DEFAULT_TEXT_ANNOTATION_FILE, 'r', encoding='utf-8') as file:
    data = json.load(file)
    
sentences = [item[0] for item in data["annotations"]]
labels = [item[1]['entities'] for item in data["annotations"]]

#Input to tensor
input_ids = [tokenizer.encode(sentence) for sentence in sentences]
padded_input_ids = pad_sequence([torch.tensor(ids) for ids in input_ids], batch_first=True, padding_value=0)
# Convert to tensor
input_ids= torch.tensor(padded_input_ids, dtype=torch.long)

# Create attention masks
attention_masks = torch.tensor([[float(i>0) for i in ii] for ii in input_ids])

#Tag to tensor
# Define tags
tags = data["classes"]
# Convert tags to indices
tag2idx = {tag: idx for idx, tag in enumerate(tags)}
# Tokenize tags
tag_ids = []
for label in labels:
    entity_ids = []
    for entity in label:
        entity_ids.append(tag2idx[entity[1]])
    tag_ids.append(entity_ids)

padded_tag_ids = pad_sequence([torch.tensor(ids) for ids in tag_ids], batch_first=True, padding_value=0)
# Convert to tensor
tag_ids= torch.tensor(padded_tag_ids, dtype=torch.long)

#find the maximum sequence length
max_length = max(input_ids.size(1), tag_ids.size(1))
#Padding to the same size
padded_input_ids = pad(padded_input_ids, (0,max_length - padded_input_ids.size(1)), value=0)
padded_tag_ids = pad(padded_tag_ids, (0, max_length - padded_tag_ids.size(1)), value=0)

input_ids = padded_input_ids.clone().detach()
tag_ids = padded_tag_ids.clone().detach()

#split data
train_input, validation_input, train_labels, validation_labels = train_test_split(input_ids, tag_ids, random_state=2021, test_size=0.1)
train_masks, validation_masks,_,_ = train_test_split(attention_masks, input_ids, random_state=2021, test_size=0.1)

train_input = torch.tensor(train_input)
validation_input = torch.tensor(validation_input)
train_masks = torch.tensor(train_masks)
validation_masks = torch.tensor(validation_masks)\

# Create DataLoader for training data
train_data = TensorDataset(train_input, train_masks, train_labels)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)

# Create DataLoader for validation data
validation_data = TensorDataset(validation_input, validation_masks, validation_labels)
validation_sampler = SequentialSampler(validation_data)
validation_dataloader = DataLoader(validation_data, sampler=validation_sampler, batch_size=batch_size)
