MANIFEST=$(aws ecr batch-get-image \
  --repository-name "repo" \
  --image-ids imageTag="internal-api-5.64.0.138" \
  --query 'images[0].imageManifest' \
  --output text)


aws ecr put-image \
  --repository-name "repo" \
  --image-tag "internal-api-uat-approved" \
  --image-manifest "$MANIFEST"
