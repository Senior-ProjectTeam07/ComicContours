def validate(epoch, model, dataloader, criterion, style_generator, scaler, verbose=False):
    model.eval()  # Set the model to evaluation mode.
    total_loss = 0  # Track total validation loss for this epoch.

    with torch.no_grad():  # Disable gradient tracking during validation.
        for landmarks, images in dataloader:  # Loop through validation data.
            landmarks, images = landmarks.to(device), images.to(device)  # Transfer data to GPU.
            
            # Zero gradients to ensure clean state before evaluation.
            model.zero_grad(set_to_none=True)

            # Get latent style vectors from the generator to avoid memory buildup.
            target_styles = style_generator.get_latent(images)  # Obtain style vectors for validation.
            
            with autocast():  # Use mixed precision to reduce memory usage.
                predicted_styles = model(landmarks)  # Predict the styles for validation.
                # Expand the predicted styles to match expected dimensions.
                predicted_styles = predicted_styles.view(4, 1, 128, 1).expand(-1, 3, -1, 128)

                loss = criterion(predicted_styles, target_styles)  # Calculate the validation loss.
            
            total_loss += loss.item()  # Add to total loss.

            # Free memory by clearing unused tensors and cached memory.
            del landmarks, images, target_styles, predicted_styles, loss
            clear_memory()  # Clear cached memory to reduce memory usage.

    print(f"Epoch {epoch}, Validation Loss: {total_loss / len(dataloader)}")  # Output the validation loss.