import mlflow
import torch
from mlflow import pytorch as mlflow_pytorch
import os

mlflow.set_tracking_uri("http://localhost:5000")

model_paths = ["./static/trained_model/multi_input_classifier.pt", "./static/trained_model/multi_input_embedder.emb",
 "./static/trained_model/multi_input_label_encoder.lbl"]

# Register models in MLflow
for i, model_path in enumerate(model_paths, start=1):
    with mlflow.start_run() as run:
        # Log the model
        mlflow.log_artifact(model_path, artifact_path=f"models/model")
        print(f"Logged model {os.path.basename(model_path)}: Run ID {run.info.run_id}")
