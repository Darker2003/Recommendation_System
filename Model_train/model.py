from config_train import *
from load_data import *

# Fine-tuning BERT for token classification
model = BertForTokenClassification.from_pretrained(
    # "bert-base-multilingual-cased",
    pretrain_model_name,
    num_labels=len(tag2idx),
    output_attentions = False,
    output_hidden_states = False
)

# AdamW optimizer
optimizer = AdamW(model.parameters(),
                  lr = 5e-5,
                  eps = 1e-8
                )

# Total number of training steps
total_steps = len(train_dataloader) * epochs

# Learning rate scheduler
scheduler = get_linear_schedule_with_warmup(optimizer, 
                                            num_warmup_steps = 0,
                                            num_training_steps = total_steps)
model.to(device)
# Training loop
for epoch in range(epochs):
    print(f'Epoch {epoch + 1}/{epochs}')
    print('-' * 10)

    # Set the model to training mode
    model.train()

    # Initialize variables for tracking training loss
    total_loss = 0

    # Wrap the train_dataloader with tqdm to visualize progress
    train_dataloader_iterator = tqdm(train_dataloader, desc="Training")

    # Iterate over batches of training data
    for step, batch in enumerate(train_dataloader_iterator):
        # Unpack the inputs from DataLoader
        b_input_ids = batch[0].to(device)
        b_input_mask = batch[1].to(device)
        b_labels = batch[2].to(device)

        # Clear previously calculated gradients
        model.zero_grad()

        # Forward pass
        outputs = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask, labels=b_labels)
        loss = outputs.loss

        # Backward pass
        loss.backward()

        # Accumulate the training loss
        total_loss += loss.item()

        # Clip the norm of the gradients to 1.0 to prevent exploding gradients
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

        # Update parameters and learning rate
        optimizer.step()
        scheduler.step()

        # Update tqdm progress bar description
        train_dataloader_iterator.set_postfix({"Loss": loss.item()})

    # Calculate average training loss
    avg_train_loss = total_loss / len(train_dataloader)
    print(f'Training loss: {avg_train_loss}')

    # Validation
    model.eval()

    # Initialize variables for tracking validation loss
    total_eval_loss = 0

    # Wrap the validation_dataloader with tqdm to visualize progress
    validation_dataloader_iterator = tqdm(validation_dataloader, desc="Validation")

    # Iterate over batches of validation data
    for batch in validation_dataloader_iterator:
        b_input_ids = batch[0].to(device)
        b_input_mask = batch[1].to(device)
        b_labels = batch[2].to(device)

        with torch.no_grad():
            # Forward pass
            outputs = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask, labels=b_labels)
            loss = outputs.loss

        # Accumulate the validation loss
        total_eval_loss += loss.item()

        # Update tqdm progress bar description
        validation_dataloader_iterator.set_postfix({"Loss": loss.item()})

    # Calculate average validation loss
    avg_val_loss = total_eval_loss / len(validation_dataloader)
    print(f'Validation Loss: {avg_val_loss}')

print("Training complete!")

# Save model
model.save_pretrained(model_saved_path)
