# Azure Functions in Python

## Usage

### Bootstrap a new project

```shell
# To bootstrap a new project, run the following commands
mkdir templates/azure_functions_basic
cd azure_functions_basic

# Create a new Azure Functions project
func init --python --docker
```

### Development

```shell
# Export poetry dependencies
poetry export --with=azure-functions -f requirements.txt --output ./templates/azure_functions_basic/requirements.txt --without-hashes

# Create virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install the required packages
pip install -r requirements.txt

# Run the project locally
func start --verbose
```

### Deployment

```shell
# Export poetry dependencies
poetry export --with=azure-functions -f requirements.txt --output ./templates/azure_functions_basic/requirements.txt --without-hashes

# Deploy resources to Azure
cd templates/azure_functions_basic
bash scripts/deploy_resources.sh

# Deploy the Function App to Azure
FUNCTION_APP_NAME="adhoc-azure-functions-..."
func azure functionapp publish $FUNCTION_APP_NAME
```
