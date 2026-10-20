aws bedrock list-foundation-models --region us-east-1 \
  --by-provider amazon --by-output-modality TEXT \
  --query "modelSummaries[].[modelId,modelLifecycle.status,join(',',inferenceTypesSupported)]" \
  --output table

aws bedrock list-inference-profiles --region us-east-1 \
  --query "inferenceProfileSummaries[].inferenceProfileId" --output table
