# Azure Functions in Python

## Usage

```shell
mkdir azure_functions_basic
cd azure_functions_basic

# Create a new Azure Functions project
func init --python --docker

# Create virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install the required packages
pip install -r requirements.txt

# Run the project locally
func start --verbose
```

## Deploy

```shell
# Deploy resources to Azure
bash scripts/deploy_resources.sh

# Deploy the Function App to Azure
FUNCTION_APP_NAME="adhoc-azure-functions-..."
func azure functionapp publish $FUNCTION_APP_NAME
```
