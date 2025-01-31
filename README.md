## Preventing Hallucinations in LLM Agents with Amazon Bedrock Knowledge Bases

This repository contains sample code demonstrating how to implement a verified semantic cache using Amazon Bedrock Knowledge Bases to prevent hallucinations in Large Language Model (LLM) responses while improving latency and reducing costs.

### Overview

The solution implements a read-only semantic cache that acts as an intelligent intermediary layer between users and Amazon Bedrock Agents. When a user submits a query, the system:

1. Evaluates semantic similarity with existing verified questions in the knowledge base
2. For highly similar queries (>80% match), returns curated & verified answers directly
3. For partial matches (60-80%), uses verified answers as few-shot examples
4. For low similarity matches (<60%), falls back to standard LLM processing

### Benefits

- **Reduced Hallucinations**: Uses verified answers for known queries
- **Lower Latency**: Provides near-instantaneous responses for cached queries
- **Cost Optimization**: Avoids unnecessary LLM invocations
- **Improved Accuracy**: Uses few-shot examples to guide LLM responses

### Prerequisites

- An AWS account with access to Amazon Bedrock
- Access to the following foundation models:
  - Anthropic Claude Sonnet v1 (claude-3-sonnet-20240229-v1:0)
  - Amazon Titan Text Embeddings v2
- AWS CLI configured with appropriate credentials

### Getting Started

1. Clone this repository.
```bash
git clone https://github.com/aws-samples/Preventing-Hallucinations-in-LLM-Agents-with-a-Verified-Semantic-Cache.git && cd Preventing-Hallucinations-in-LLM-Agents-with-a-Verified-Semantic-Cache
```

2. Deploy the provided AWS CloudFormation template to setup an Amazon SageMaker notebook.
```
aws cloudformation deploy \
    --template-file ./sagemaker_notebook.yaml \
    --stack-name PreventingHallucinationsDemoStack \
    --capabilities CAPABILITY_NAMED_IAM
```

3. Navigate to the Amazon SageMaker AI console (https://console.aws.amazon.com/sagemaker), and click on "Notebooks."

4. Open "PreventingHallucinationsDemoStack-SageMakerNotebook" as a Jupyter Notebook and follow the instructions in verified_semantic_cache.ipynb. This GitHub repository should already be cloned and available in the Notebook.

5. Delete the AWS CloudFormation stack to prevent unnecessary cost.
```
aws cloudformation delete-stack --stack-name PreventingHallucinationsDemoStack
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

