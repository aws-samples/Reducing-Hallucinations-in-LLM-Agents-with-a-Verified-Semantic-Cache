## Building a Data Analytics Bedrock Agent

This repository contains a comprehensive workshop demonstrating how to build powerful SQL assistants using Amazon Bedrock Agents. The code shows how to create an AI agent that translates natural language questions into SQL queries for data analysis in a returns and recommerce business context.

### Prerequisites

- An AWS account with access to Amazon Bedrock
- Access to the following foundation models:
  - Anthropic Claude 3.5 Haiku (us.anthropic.claude-3-5-haiku-20241022-v1:0)

### Getting Started

0. Create your [Burner AWS account](https://access.amazon.com/aws/burner) and log in. Please ensure you're operating in `us-east-1` region for all following steps.

1. Navigate to [SageMaker Service Quotas](https://us-east-1.console.aws.amazon.com/servicequotas/home/services/sagemaker/quotas/L-8E454C05) and request additional account-level quota for `ml.t3.large for notebook instance usage` instances. Set it to **6** for burner accounts.

2. Ensure you have enabled [Model Access](https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess) to all the foundation models in Amazon Bedrock:

3. Navigate to your [AWS CloudShell Console](https://us-east-1.console.aws.amazon.com/cloudshell) and run the following command. It will deploy a AWS CloudFormation stack in your account.
```
git clone -b devcon-2025-branch --single-branch \
    https://github.com/aws-samples/Reducing-Hallucinations-in-LLM-Agents-with-a-Verified-Semantic-Cache.git && \
cd Reducing-Hallucinations-in-LLM-Agents-with-a-Verified-Semantic-Cache && \
aws cloudformation deploy \
    --template-file ./sagemaker_notebook.yaml \
    --stack-name DevConLabStack \
    --capabilities CAPABILITY_NAMED_IAM
```

4. Navigate to the Amazon SageMaker AI console (https://us-east-1.console.aws.amazon.com/sagemaker/home?region=us-east-1#/notebooks-and-git-repos), and click on "Notebooks." Open "DevConLabStack-SageMakerNotebook" as a Jupyter Notebook and follow the instructions in main.ipynb.