import boto3  

client = boto3.client("bedrock-runtime", region_name="us-east-1")  

response = client.converse( 
    modelId="amazon.nova-micro-v1:0", 
    messages=[ 
        { 
            "role": "user", 
            "content": [{"text": "Write a one-sentence bedtime story about a unicorn."}]
        } 
    ] 
)  

print(response["output"]["message"]["content"][0]["text"])
