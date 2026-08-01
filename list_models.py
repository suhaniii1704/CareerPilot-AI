from utils.config import client

models = client.models.list()

for model in models:
    if "embed" in model.name.lower():
        print(model.name)