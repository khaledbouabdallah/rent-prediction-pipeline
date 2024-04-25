import pandas as pd
import numpy as np


from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold

from sklearn.preprocessing import MaxAbsScaler

from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
)
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor

from sklearn.pipeline import make_pipeline

import cupy as cp
from xgboost import XGBRegressor

import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
from torch.optim.lr_scheduler import ReduceLROnPlateau

torch.cuda.manual_seed(42)
torch.manual_seed(42)
np.random.seed(42)
torch.backends.cudnn.deterministic = True





df_classic = pd.read_csv('../data/ads_clean.csv')
df_stations_basic = pd.read_csv('../data/ads_stations_basic.csv')
df_stations_weighted = pd.read_csv('../data/ads_stations_weighted.csv')




def prepare_data(version = 'classic', val_size = 0.2, test_size = 0.2, random_state = 42):
    
    versions = ['classic', 'stations_basic', 'stations_weighted_all', 'stations_weights_inverse',
                'stations_weights_gaussian', 'stations_weights_logarithmic', 'stations_weights_linear']
    
    if version not in versions:
        raise ValueError(f"version must be one of {versions}")
    
    if version == 'classic':
        df = df_classic.copy()
    elif version == 'stations_basic':
        df = df_stations_basic.copy()
    else:
        df = df_stations_weighted.copy()
        
    # drop the columns that are not needed (same for all versions)
    df = df.drop(columns=['id', 'department_name', 'department_number', 'city_name'])
    

    # idk have time to refactor it now :(
    if version == 'stations_weights_inverse':
        columns_to_drop = [column for column in df.columns if 'inverse' not in column and 'score' in column] 
        df = df.drop(columns=columns_to_drop)
    elif version == 'stations_weights_gaussian':
        columns_to_drop = [column for column in df.columns if 'gaussian' not in column and 'score' in column] 
        df = df.drop(columns=columns_to_drop)
    elif version == 'stations_weights_logarithmic':
        columns_to_drop = [column for column in df.columns if 'logarithmic' not in column and 'score' in column] 
        df = df.drop(columns=columns_to_drop)
    elif version == 'stations_weights_linear':
        columns_to_drop = [column for column in df.columns if 'linear' not in column and 'score' in column] 
        df = df.drop(columns=columns_to_drop)
    
    # split the data into features and target
    X = df.drop(columns=['price'])
    y = df['price']
    
    
    # split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    
    return X_train, X_test, y_train, y_test


def create_objective_function(X, y, metric, model_cls):
    # Define the inner objective function
    def objective(trial):
        # Suggest hyperparameters based on the model class
        if model_cls == RandomForestRegressor:
            hyperparams = {
                "n_estimators": trial.suggest_int("n_estimators", 100, 1500, step=100),
                "max_depth": trial.suggest_int("max_depth", 2, 30, step=2),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 4),
                "max_features": trial.suggest_categorical("max_features", [None, "sqrt", "log2"]),
                "random_state":42,
            }
        elif model_cls == GradientBoostingRegressor:
            hyperparams = {
                "n_estimators": trial.suggest_int("n_estimators", 100, 1500, step=100),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.5),
                "max_depth": trial.suggest_int("max_depth", 2, 30, step=2),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 4),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "max_features": trial.suggest_categorical("max_features", [None, "sqrt", "log2"]),
                "alpha": trial.suggest_float("alpha", 0.1, 0.9),
                "random_state":42,
            }
        elif model_cls == AdaBoostRegressor:
            hyperparams = {
                "estimator": trial.suggest_categorical("estimator", [DecisionTreeRegressor(max_depth=5),
                                                                     DecisionTreeRegressor(max_depth=10),
                                                                     DecisionTreeRegressor(max_depth=20)]),
                "n_estimators": trial.suggest_int("n_estimators", 50, 500),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 1.0),
                "random_state":42,
            }
        elif model_cls == LinearRegression:
            # LinearRegression has no hyperparameters to tune
            hyperparams = {}
        elif model_cls == Ridge:
            hyperparams = {
                "alpha": trial.suggest_float("alpha", 0.1, 10),
                "random_state":42,
            }
        elif model_cls == Lasso:
            hyperparams = {
                "alpha": trial.suggest_float("alpha", 0.1, 10),
                "max_iter": trial.suggest_categorical("max_iter", [1000, 5000, 10000]),
                "random_state":42,
            }
        elif model_cls == ElasticNet:
            hyperparams = {
                "alpha": trial.suggest_float("alpha", 0.1, 10),
                "l1_ratio": trial.suggest_float("l1_ratio", 0.1, 0.9),
                "max_iter": trial.suggest_categorical("max_iter", [1000, 5000, 10000]),
                "random_state":42
            }
        elif model_cls == SVR:
            hyperparams = {
                "C": trial.suggest_float("C", 0.1, 10),
                "kernel": trial.suggest_categorical("kernel", ["linear", "poly", "rbf", "sigmoid"]),
            }
        elif model_cls == KNeighborsRegressor:
            hyperparams = {
                "n_neighbors": trial.suggest_int("n_neighbors", 2, 100),
                "weights": trial.suggest_categorical("weights", ["uniform", "distance"]),
                "p": trial.suggest_int("p", 1, 2),
                "leaf_size": trial.suggest_int("leaf_size", 10, 50),
            }
        elif model_cls == DecisionTreeRegressor:
            hyperparams = {
                "max_depth": trial.suggest_int("max_depth", 2, 20),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
                "random_state":42
            }
        elif model_cls == MLPRegressor:
            hyperparams = {
                "hidden_layer_sizes": trial.suggest_categorical("hidden_layer_sizes", [(100,), (50, 50), (100, 100)]),
                "activation": trial.suggest_categorical("activation", ["relu", "tanh", "logistic"]),
                "alpha": trial.suggest_float("alpha", 0.1, 10),
                "random_state":42
            }
        elif model_cls == XGBRegressor:
            hyperparams = {
                "tree_method":"hist",
                "device": "cuda",
                "n_estimators": trial.suggest_int("n_estimators", 100, 1500, step=100),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.5),
                "max_depth": trial.suggest_int("max_depth", 2, 30, step=2),
                "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 0.1, 10, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 0.1, 10, log=True),
                "random_state":42,
            }
        else:
            raise ValueError("Unknown model class")
        
        # reduce the number of folds for slow models
        if model_cls in [RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor]:
            n_splits = 3
        else:
            n_splits = 5

        # K-Fold cross-validation
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        metric_scores = []

        # Perform K-Fold cross-validation
        for train_index, val_index in kf.split(X):
            X_train, X_val = X.iloc[train_index], X.iloc[val_index]
            y_train, y_val = y.iloc[train_index], y.iloc[val_index]
            
            # Initialize the MaxAbsScaler
            scaler = MaxAbsScaler()
            # Fit the scaler on the training set and transform the training and validation sets
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)

            X_train_scaled = cp.array(X_train_scaled)
            X_val_scaled = cp.array(X_val_scaled)
            y_train = cp.array(y_train)

            # Create the model with suggested hyperparameters
            model = model_cls(**hyperparams)

            # Fit the model
            model.fit(X_train_scaled, y_train)

            # Predict on validation set
            y_pred = model.predict(X_val_scaled)

            # Calculate the metric (mean absolute error)
            score = metric(y_val, y_pred)
            metric_scores.append(score)

        # Return the average metric score
        return np.mean(metric_scores)

    return objective





class EarlyStopper:
    def __init__(self, patience=1, min_delta=0):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.min_validation_loss = float('inf')

    def early_stop(self, validation_loss, epoch):
        if validation_loss < self.min_validation_loss:
            if self.min_validation_loss - validation_loss >= self.min_delta:
                self.counter = 0
                #print(f"New best validation loss epoch {epoch} = {self.min_validation_loss}")  
            self.min_validation_loss = validation_loss     
        else: 
            self.counter += 1
            if self.counter >= self.patience:
                return True
        return False

def plot_train_val(train_losses,validation_losses):
    # Plot the validation losses
    plt.plot(validation_losses, label='Validation Losses', color='orange')
    # Plot the train losses
    plt.plot(train_losses, label='Train Losses', color='blue')
    # Add labels and title
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Losses')
    # Add legend
    plt.legend()
    # Show plot
    plt.show()

def plot_val(validation_losses):
    # Plot the validation losses
    plt.plot(validation_losses[-30:], label='Validation Losses', color='orange')
    # Add labels and title
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Last 30 Validation Losses')
    # Add legend
    plt.legend()
    # Show plot
    plt.show()

class FlexibleMLP(nn.Module):
    def __init__(self, input_size, layer_sizes, output_size, activation_fn=F.relu, dropout_rate=0.0):
        """
        Create a flexible MLP.
        
        :param input_size: Number of input features
        :param layer_sizes: List of sizes for each hidden layer
        :param output_size: Number of output units (e.g., 1 for regression, number of classes for classification)
        :param activation_fn: Activation function (default is ReLU)
        :param dropout_rate: Dropout rate (default is 0.0, meaning no dropout)
        """
        super(FlexibleMLP, self).__init__()
        self.activation_fn = activation_fn
        self.dropout_rate = dropout_rate
        
        # Build the layers
        layers = []
        
        # First hidden layer connects input to the first hidden layer
        previous_size = input_size
        for i,size in enumerate(layer_sizes):
            layers.append(nn.Linear(previous_size, size))
            if i % 2 != 0:
                layers.append(nn.Dropout(dropout_rate))  # Add dropout
            previous_size = size
        
        # Output layer
        layers.append(nn.Linear(previous_size, output_size))
        
        # Register layers as a Sequential module
        self.model = nn.Sequential(*layers)
    
    def forward(self, x):
        # Apply activation function to each layer except the last one
        for layer in self.model[:-1]:
            if isinstance(layer, nn.Linear):
                x = self.activation_fn(layer(x))
            else:
                x = layer(x)
        
        # Output layer (no activation function here, depending on the problem)
        return self.model[-1](x)


def train(model, X_train, y_train, X_val, y_val, criterion, optimizer, epochs=100, verbose = False):
    
    losses_val = []
    losses_train = []
    best_val = float('inf')

    early_stopper = EarlyStopper(patience=100, min_delta=0.000001)
    scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=30)
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        output = model(X_train)
        loss = criterion(output, y_train)  
        loss.backward()
        optimizer.step()
        losses_train.append(loss.item())
        # validation
        model.eval()
        with torch.no_grad():
           output = model(X_val)
           validation_loss =  criterion(output, y_val)
           losses_val.append(validation_loss.item()) 
            
        scheduler.step(validation_loss)
            
                 
        if early_stopper.early_stop(validation_loss, epoch):
            #print(f"early stopping in epoch = {epoch}")         
            break
            
        if best_val > validation_loss:
              validation_loss = best_val
              torch.save(model.state_dict(), 'model_weights.pth')
            
        if epoch % 10 == 0:
            pass
            #print(f'Epoch {epoch}/{epochs} train Loss {loss.item()} lr: {optimizer.param_groups[0]["lr"]}')
    if verbose:
        plot_train_val(losses_train,losses_val)
        plot_val(losses_val)
    
def predict(model, X):
    model.eval()
    with torch.no_grad():
        y_pred = model(X)
    return y_pred.cpu().numpy().flatten()

def serialize_tuple(t):
    return ",".join(map(str, t))
                    
def deserialize_tuple(s):
    return tuple(map(int, s.split(",")))
    
def create_objective_mlp(X_train, X_val, y_train, y_val, epochs=100, lr = 0.003):


        
    # Define the inner objective function
    def objective(trial):
        # Suggest hyperparameters

        layer_sizes = [(100,),
                       (100, 50, 50),  
                       (200, 200, 100),
                      (512,256,64),
                      (1024,512,256,64),
                      (2048,1024,1024,256),
                       (2048,1024,1024,512,256), 
                      ]
        
        hyperparams = {
            "input_size": X_train.shape[1],
            "layer_sizes":  trial.suggest_categorical("layer_sizes", [serialize_tuple(t) for t in layer_sizes]),
            "output_size": 1,
            "activation_fn": F.relu,
            "dropout_rate": trial.suggest_float("dropout_rate", 0.0, 0.8),
        }

        hyperparams['layer_sizes'] = deserialize_tuple( hyperparams['layer_sizes'])


        
        # Define the model
        model = FlexibleMLP(**hyperparams)
        model = model.cuda()
        
        # Define the loss function and optimizer
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
               
        # Convert data to PyTorch tensors
        X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32).to('cuda')
        y_train_tensor = torch.tensor(y_train.values, dtype=torch.float32).view(-1, 1).to('cuda')
        X_val_tensor = torch.tensor(X_val.values, dtype=torch.float32).to('cuda')
        y_val_tensor = torch.tensor(y_val.values, dtype=torch.float32).view(-1, 1).to('cuda')
        
        train(model, X_train_tensor, y_train_tensor, X_val_tensor, y_val_tensor, criterion, optimizer, epochs=epochs)
         
        y_pred = predict(model, X_val_tensor)
        
        mae = mean_absolute_error(y_val_tensor.cpu(), y_pred.flatten())
        
        return mae
    
    return objective