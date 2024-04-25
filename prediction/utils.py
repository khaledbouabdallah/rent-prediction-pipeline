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





df_classic = pd.read_csv('../data/ads_clean.csv')
df_stations_basic = pd.read_csv('../data/ads_stations_basic.csv')
df_stations_weighted = pd.read_csv('../data/ads_stations_weighted.csv')

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split

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
    
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=test_size, random_state=42)

    # Second split: Validation and test sets
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
    
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


def evaluate_model(X_train, X_test, y_train, y_test, model_cls, hyperparams, metrics):
    # Initialize the MaxAbsScaler
    scaler = MaxAbsScaler()
    # Fit the scaler on the training set and transform the training and testing sets
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Create the model
    model = model_cls(**hyperparams)

    # Fit the model
    model.fit(X_train_scaled, y_train)

    # Predict on the testing set
    y_pred = model.predict(X_test_scaled)

    # Calculate the metric (mean absolute error)
    scores = {metric.__name__: metric(y_test, y_pred) for metric in metrics}

    return scores