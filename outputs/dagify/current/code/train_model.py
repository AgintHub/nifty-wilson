from ._train_model.validate_inputs import validate_inputs
from ._train_model.load_configuration import load_configuration
from ._train_model.load_training_data import load_training_data
from ._train_model.create_model_architecture import create_model_architecture
from ._train_model.setup_optimizer import setup_optimizer
from ._train_model.setup_lr_scheduler import setup_lr_scheduler
from ._train_model.create_dataloader import create_dataloader
from ._train_model.setup_loss_criterion import setup_loss_criterion
from ._train_model.get_current_time import get_current_time
from ._train_model.train_single_epoch import train_single_epoch
from ._train_model.log_epoch_progress import log_epoch_progress
from ._train_model.calculate_duration_minutes import calculate_duration_minutes
from ._train_model.calculate_perplexity import calculate_perplexity
from ._train_model.save_model_checkpoint import save_model_checkpoint
from ._train_model.log_training_exception import log_training_exception
from ._train_model.save_partial_checkpoint_if_possible import save_partial_checkpoint_if_possible

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Validate parent inputs and set up training environment.
#   Reason: Ensures that training does not proceed with missing or corrupted data,
#           preventing downstream failures.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Check that split_data.train_data_path exists and is readable; confirm
#           initialize_model_weights.initialization_success is True. Log
#           any failures and set training_status=False immediately.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Load the training data from the file system into an efficient in‑memory
#   representation.
#   Reason: Allows batched processing without disk I/O bottlenecks during training.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a lightweight parser (e.g., TensorFlow's tf.data.TextLineDataset or
#           PyTorch's Dataset) to read the tokenized text file line by
#           line, converting each line into a tensor of token IDs using the
#           vocabulary built in create_vocabulary. Store the result in a
#           PyTorch Dataset that returns `(input_ids, target_ids)` pairs.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Instantiate the model architecture based on the parameters provided by
#   initialize_model_weights (or via a configuration file).
#   Reason: Creates a clean, correctly sized model ready for training.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Retrieve model_type, number_of_layers, hidden_size, attention_heads, and
#           vocab_size from a persisted architecture file or from
#           environment variables set by define_model_architecture.
#           Construct a `torch.nn.Module` subclass (e.g., a Transformer)
#           using `nn.TransformerEncoderLayer` repeated `number_of_layers`
#           times, with `hidden_size` and `attention_heads`. Initialize
#           weights using the method specified in
#           initialize_model_weights.initialization_method.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Prepare the optimizer and learning‑rate scheduler according to
#   load_configuration hyperparameters.
#   Reason: Ensures consistency between training configuration and execution.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Instantiate an AdamW optimizer with learning_rate from load_configuration.
#           Use a `StepLR` scheduler that decays the learning rate every
#           `config['decay_step']` epochs by factor
#           `config['decay_gamma']`.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Wrap the dataset in a DataLoader with the batch_size from load_configuration,
#   using `torch.utils.data.DataLoader`.
#   Reason: Provides shuffling, batching, and parallel loading.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Create DataLoader(dataset, batch_size=config['batch_size'], shuffle=True,
#           num_workers=4, pin_memory=True).
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Implement the training loop: iterate over epochs and batches, compute loss,
#   backpropagate, and update model weights.
#   Reason: Core of the training process that optimizes model parameters.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: For each epoch in range(max_epochs):   set model.train();   for batch in
#           dataloader:     inputs, targets = batch     outputs =
#           model(inputs)     loss = criterion(outputs.view(-1,
#           vocab_size), targets.view(-1))     optimizer.zero_grad()
#           loss.backward()     optimizer.step();   scheduler.step();
#           record epoch_loss += loss.item() * batch_size.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Compute epoch‑level metrics: loss average, perplexity (`exp(loss)`), and
#   accuracy.
#   Reason: Provides diagnostic information for each epoch and final metrics for the
#           output.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: After the inner loop, calculate `epoch_loss / total_examples`. Perplexity
#           is `math.exp(epoch_loss / total_examples)` capped at a
#           reasonable value to avoid overflow. Accuracy is computed by
#           comparing `outputs.argmax(dim=-1)` with `targets` and summing
#           correct predictions.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Measure and record training duration.
#   Reason: Necessary for reporting training performance and resource budgeting.
#   Impact: LOW
#   Complexity: LOW
#   Method: Wrap the entire epoch loop in `time.time()` start/stop calls, compute
#           `(stop - start) / 60` to get minutes.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Save the trained model checkpoint to disk.
#   Reason: Ensures the trained model can be reused by downstream nodes such as
#           evaluate_model.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use `torch.save(model.state_dict(), output_path)` where output_path is
#           constructed from load_configuration.model_output_path +
#           '/final_model.pt'. Include metadata such as training_epochs,
#           final_loss, etc.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Set the output fields according to the defined structure.
#   Reason: Matches the expected output schema of the node.
#   Impact: LOW
#   Complexity: LOW
#   Method: Create a dictionary with keys final_loss, final_perplexity,
#           training_accuracy, training_epochs, training_duration_minutes,
#           model_path, training_status. Populate each with the computed
#           values; set training_status=True if no exceptions were raised.
# 
# -----------------------------------------------------------------------------
# 11. BULLET: Implement robust exception handling and graceful failure reporting.
#   Reason: Prevents the entire DAG from crashing on transient errors and provides
#           clear diagnostics.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Wrap the training loop in a try/except block. On exception, log the
#           traceback, set training_status=False, and optionally write a
#           partial checkpoint if possible. Ensure that even in failure,
#           the node returns a consistent output structure.
# -- END PRD --



class SplitDataOutput(BaseModel):
    """Pydantic model for split_data node outputs."""
    train_set_size: int = Field(..., description="Number of examples in the training set")
    validation_set_size: int = Field(..., description="Number of examples in the validation set")
    test_set_size: int = Field(..., description="Number of examples in the test set")
    train_data_path: str = Field(..., description="Filesystem path to the training dataset file")
    validation_data_path: str = Field(..., description="Filesystem path to the validation dataset file")
    test_data_path: str = Field(..., description="Filesystem path to the test dataset file")
    split_ratios: float = Field(..., description="Ratios used for splitting the data, in order [train, validation, test]")
    split_seed: int = Field(..., description="Random seed used for reproducibility during splitting")


class InitializeModelWeightsOutput(BaseModel):
    """Pydantic model for initialize_model_weights node outputs."""
    initialization_success: bool = Field(..., description="Whether the weight initialization completed successfully")
    num_parameters: int = Field(..., description="Total number of trainable parameters in the model")
    initialization_method: str = Field(..., description="Method used for weight initialization (e.g., 'random', 'xavier', 'pretrained')")
    architecture_signature: str = Field(..., description="Hash or unique string representing the model architecture configuration")


class TrainModelOutput(BaseModel):
    """Pydantic model for train_model node outputs."""
    final_loss: float = Field(..., description="Final training loss after the last epoch.")
    final_perplexity: float = Field(..., description="Final training perplexity after the last epoch.")
    training_accuracy: float = Field(..., description="Training accuracy expressed as a percentage.")
    training_epochs: int = Field(..., description="Total number of training epochs performed.")
    training_duration_minutes: float = Field(..., description="Total training duration in minutes.")
    model_path: str = Field(..., description="Filesystem path to the final model checkpoint.")
    training_status: bool = Field(..., description="Indicates whether training completed successfully.")


def train_model(split_data_input: SplitDataOutput, initialize_model_weights_input: InitializeModelWeightsOutput, **kwargs) -> TrainModelOutput:
    """This node performs supervised training of the language model on the split training dataset, applying gradient descent to reduce the training loss. It also records key metrics (loss, perplexity, accuracy) and saves the trained model checkpoint.

    Args:
        split_data_input: Input from the 'split_data' node.
        initialize_model_weights_input: Input from the 'initialize_model_weights' node.
        **kwargs: Additional keyword arguments.

    Returns:
        TrainModelOutput: Object containing outputs for this node.
    """
    try:
        # Validate parent inputs and set up training environment
        validation_success: bool = validate_inputs(
            train_data_path=split_data_input.train_data_path,
            initialization_success=initialize_model_weights_input.initialization_success
        )
        
        if not validation_success:
            return TrainModelOutput(
                final_loss=0.0,
                final_perplexity=0.0,
                training_accuracy=0.0,
                training_epochs=0,
                training_duration_minutes=0.0,
                model_path="",
                training_status=False,
            )
        
        # Load configuration
        config: dict = load_configuration()
        
        # Load training data into efficient in-memory representation
        dataset = load_training_data(
            train_data_path=split_data_input.train_data_path,
            vocab_path=config.get('vocab_path')
        )
        
        # Instantiate model architecture
        model = create_model_architecture(
            initialization_method=initialize_model_weights_input.initialization_method,
            config=config
        )
        
        # Prepare optimizer and learning rate scheduler
        optimizer = setup_optimizer(model=model, config=config)
        scheduler = setup_lr_scheduler(optimizer=optimizer, config=config)
        
        # Wrap dataset in DataLoader
        dataloader = create_dataloader(dataset=dataset, config=config)
        
        # Setup loss criterion
        criterion = setup_loss_criterion(vocab_size=config['vocab_size'])
        
        # Start timing training
        training_start_time: float = get_current_time()
        
        # Training loop variables
        max_epochs: int = config['max_epochs']
        total_loss: float = 0.0
        total_accuracy: float = 0.0
        
        # Implement the training loop
        for epoch in range(max_epochs):
            epoch_metrics: dict = train_single_epoch(
                model=model,
                dataloader=dataloader,
                optimizer=optimizer,
                criterion=criterion,
                vocab_size=config['vocab_size']
            )
            
            scheduler.step()
            
            total_loss = epoch_metrics['loss']
            total_accuracy = epoch_metrics['accuracy']
            
            log_epoch_progress(epoch=epoch, metrics=epoch_metrics)
        
        # Calculate training duration
        training_end_time: float = get_current_time()
        training_duration_minutes: float = calculate_duration_minutes(
            start_time=training_start_time,
            end_time=training_end_time
        )
        
        # Compute final metrics
        final_perplexity: float = calculate_perplexity(loss=total_loss)
        
        # Save trained model checkpoint
        model_path: str = save_model_checkpoint(
            model=model,
            config=config,
            final_loss=total_loss,
            training_epochs=max_epochs
        )
        
        return TrainModelOutput(
            final_loss=total_loss,
            final_perplexity=final_perplexity,
            training_accuracy=total_accuracy,
            training_epochs=max_epochs,
            training_duration_minutes=training_duration_minutes,
            model_path=model_path,
            training_status=True,
        )
        
    except Exception as e:
        # Handle exceptions gracefully
        log_training_exception(exception=e)
        
        # Attempt to save partial checkpoint if possible
        partial_model_path: str = save_partial_checkpoint_if_possible(
            model=locals().get('model'),
            config=locals().get('config', {})
        )
        
        return TrainModelOutput(
            final_loss=0.0,
            final_perplexity=0.0,
            training_accuracy=0.0,
            training_epochs=0,
            training_duration_minutes=0.0,
            model_path=partial_model_path,
            training_status=False,
        )