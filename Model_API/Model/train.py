from .config_train import *
from .load_data import *
from .model import *


class Key_Ner_Training:
    def __init__(self, model, train_dataloader, validation_dataloader, epochs, lr, eps, weight_decay, device, model_saved_path):
        """
        Initializes the Key_Ner_Training with the necessary components for training.

        Args:
            model (torch.nn.Module): The model to be trained.
            train_dataloader (DataLoader): DataLoader for training data.
            validation_dataloader (DataLoader): DataLoader for validation data.
            epochs (int): Number of training epochs.
            lr (float): Learning rate for the optimizer.
            eps (float): Epsilon value for the optimizer.
            weight_decay (float): Weight decay for the optimizer.
            device (str): Device to run the model on ("cuda" or "cpu").
            model_saved_path (str): Path to save the trained model.
        """
        self.model = model.to(device)
        self.train_dataloader = train_dataloader
        self.validation_dataloader = validation_dataloader
        self.epochs = epochs
        self.device = device
        self.model_saved_path = model_saved_path

        # AdamW optimizer
        self.optimizer = AdamW(self.model.parameters(), lr=lr, eps=eps, weight_decay=weight_decay)

        # Total number of training steps
        self.total_steps = len(train_dataloader) * epochs

        # Learning rate scheduler
        self.scheduler = get_linear_schedule_with_warmup(self.optimizer, num_warmup_steps=0, num_training_steps=self.total_steps)

        # Metrics
        self.train_losses = []
        self.val_losses = []
        self.train_f1_scores = []
        self.val_f1_scores = []

    def train(self):
        """Trains the model over the specified number of epochs."""
        for epoch in range(self.epochs):
            print(f'Epoch {epoch + 1}/{self.epochs}')
            print('-' * 10)

            # Training
            avg_train_loss, train_f1 = self._train_epoch()
            self.train_losses.append(avg_train_loss)
            self.train_f1_scores.append(train_f1)
            print(f'Training loss: {avg_train_loss}, F1-score: {train_f1}')

            # Validation
            avg_val_loss, val_f1 = self._validate_epoch()
            self.val_losses.append(avg_val_loss)
            self.val_f1_scores.append(val_f1)
            print(f'Validation Loss: {avg_val_loss}, F1-score: {val_f1}')

        print("Training complete!")

        # Plot losses and F1 scores
        self._plot_metrics()

        # Save model
        self.model.save_pretrained(self.model_saved_path)

    def _train_epoch(self):
        """Runs a single training epoch."""
        self.model.train()

        total_loss = 0
        train_predictions = []
        train_targets = []

        train_dataloader_iterator = tqdm(self.train_dataloader, desc="Training")

        for step, batch in enumerate(train_dataloader_iterator):
            b_input_ids = batch[0].to(self.device)
            b_input_mask = batch[1].to(self.device)
            b_labels = batch[2].to(self.device)

            self.model.zero_grad()

            outputs = self.model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask, labels=b_labels)
            loss = outputs.loss

            total_loss += loss.item()

            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            self.scheduler.step()

            train_dataloader_iterator.set_postfix({"Loss": loss.item()})

            logits = outputs.logits
            predictions = torch.argmax(logits, dim=2)
            train_predictions.extend(predictions.cpu().numpy().flatten())
            train_targets.extend(b_labels.cpu().numpy().flatten())

        avg_train_loss = total_loss / len(self.train_dataloader)
        train_f1 = f1_score(train_targets, train_predictions, average='macro')

        return avg_train_loss, train_f1

    def _validate_epoch(self):
        """Runs a single validation epoch."""
        self.model.eval()

        total_eval_loss = 0
        val_predictions = []
        val_targets = []

        validation_dataloader_iterator = tqdm(self.validation_dataloader, desc="Validation")

        for batch in validation_dataloader_iterator:
            b_input_ids = batch[0].to(self.device)
            b_input_mask = batch[1].to(self.device)
            b_labels = batch[2].to(self.device)

            with torch.no_grad():
                outputs = self.model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask, labels=b_labels)
                loss = outputs.loss

            total_eval_loss += loss.item()

            validation_dataloader_iterator.set_postfix({"Loss": loss.item()})

            logits = outputs.logits
            predictions = torch.argmax(logits, dim=2)
            val_predictions.extend(predictions.cpu().numpy().flatten())
            val_targets.extend(b_labels.cpu().numpy().flatten())

        avg_val_loss = total_eval_loss / len(self.validation_dataloader)
        val_f1 = f1_score(val_targets, val_predictions, average='macro')

        return avg_val_loss, val_f1

    def _plot_metrics(self):
        """Plots training and validation losses and F1 scores."""
        epochs_range = range(1, self.epochs + 1)

        # Plotting Loss
        plt.figure(figsize=(12, 6))
        plt.plot(epochs_range, self.train_losses, label='Training Loss')
        plt.plot(epochs_range, self.val_losses, label='Validation Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.title('Training and Validation Loss')
        plt.legend()
        plt.show()

        # Plotting F1-score
        plt.figure(figsize=(12, 6))
        plt.plot(epochs_range, self.train_f1_scores, label='Training F1-score')
        plt.plot(epochs_range, self.val_f1_scores, label='Validation F1-score')
        plt.xlabel('Epochs')
        plt.ylabel('F1-score')
        plt.title('Training and Validation F1-score')
        plt.legend()
        plt.show()


# Example usage:
if __name__ == "__main__":
    trainer = Key_Ner_Training(
        model=model,
        train_dataloader=train_dataloader,
        validation_dataloader=validation_dataloader,
        epochs=epochs,
        lr=lr,
        eps=eps,
        weight_decay=weight_decay,
        device=device,
        model_saved_path=model_saved_path
    )
    trainer.train()
