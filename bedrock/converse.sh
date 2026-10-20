aws bedrock-runtime converse --region us-east-1 \
  --model-id amazon.nova-micro-v1:0 \
  --messages '[{"role":"user","content":[{"text":"In one sentence, what does exit code 137 mean for a container?"}]}]' \
  --inference-config '{"maxTokens":100,"temperature":0.1}'
