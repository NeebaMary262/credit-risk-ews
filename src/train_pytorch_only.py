import os
import logging
import joblib
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

# Set up production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RiskNet(nn.Module):
    """PyTorch Neural Network Architecture"""
    def __init__(self, input_size):
        super(RiskNet, self).__init__()
        self.layer1 = nn.Linear(input_size, 16)
        self.relu = nn.ReLU()
        self.output = nn.Linear(16, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.output(x)
        return self.sigmoid(x)


class PyTorchTrainer:
    """Handles data preparation, training, and saving of the PyTorch Risk Model."""
    
    def __init__(self, raw_data_path: str, artifacts_dir: str = "artifacts"):
        self.raw_data_path = raw_data_path
        self.artifacts_dir = artifacts_dir
        self.target_col = 'loan_status'
        
        # Determine if a GPU is available for faster training
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initialized PyTorchTrainer using device: {self.device}")

        # Placeholders for loaded artifacts
        self.encoders = None
        self.scaler = None
        self.feature_names = None
        self.model = None

    def load_sklearn_artifacts(self):
        """Loads the existing Sklearn preprocessing tools."""
        logger.info("Loading existing Sklearn artifacts...")
        try:
            self.encoders = joblib.load(os.path.join(self.artifacts_dir, 'encoders.pkl'))
            self.scaler = joblib.load(os.path.join(self.artifacts_dir, 'scaler.pkl'))
            self.feature_names = joblib.load(os.path.join(self.artifacts_dir, 'feature_names.pkl'))
        except FileNotFoundError as e:
            logger.error(f"Missing artifact: {e}")
            raise

    def prepare_data(self) -> tuple:
        """Loads raw data, applies Sklearn transformations, and converts to Tensors."""
        logger.info(f"Loading historical data from {self.raw_data_path}...")
        if not os.path.exists(self.raw_data_path):
            raise FileNotFoundError(f"Data file not found at: {self.raw_data_path}")

        df = pd.read_csv(self.raw_data_path).dropna()

        logger.info("Applying Label Encoders to categorical columns...")
        categorical_cols = ["person_home_ownership", "loan_intent", "loan_grade", "cb_person_default_on_file"]
        for col in categorical_cols:
            if col in df.columns:
                df[col] = self.encoders[col].transform(df[col])

        X = df[self.feature_names]
        y = df[self.target_col]

        logger.info("Scaling features...")
        X_scaled = self.scaler.transform(X)

        # Convert to PyTorch Tensors and send to CPU/GPU
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(self.device)
        y_tensor = torch.tensor(y.values, dtype=torch.float32).view(-1, 1).to(self.device)

        return X_tensor, y_tensor

    def train_model(self, X_tensor, y_tensor, epochs: int = 150, lr: float = 0.01):
        """Builds and trains the PyTorch Neural Network."""
        logger.info("Initializing RiskNet Neural Network...")
        self.model = RiskNet(len(self.feature_names)).to(self.device)
        
        criterion = nn.BCELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)

        logger.info(f"Starting training loop for {epochs} epochs...")
        self.model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self.model(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 25 == 0:
                logger.info(f'Epoch [{epoch+1}/{epochs}] - Loss: {loss.item():.4f}')

    def save_model(self):
        """Saves the trained network weights to the artifacts directory."""
        if self.model is None:
            raise RuntimeError("Model has not been trained yet. Call train_model() first.")
        
        save_path = os.path.join(self.artifacts_dir, 'pytorch_risk_model.pth')
        logger.info(f"Saving PyTorch model weights to {save_path}...")
        
        # Always save to CPU memory structure so it can run on any machine later
        torch.save(self.model.cpu().state_dict(), save_path)
        logger.info("Training complete and model saved successfully.")



    #     logger.error(f"Training pipeline failed: {str(e)}")
