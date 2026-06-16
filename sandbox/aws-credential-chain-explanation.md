# AWS Default Credential Provider Chain

When an AWS SDK or CLI tool makes a request to AWS, it needs credentials. If you do not explicitly provide credentials in your code, the SDK searches for them automatically using a specific hierarchy known as the **Default Credential Provider Chain**.

The SDK evaluates the chain in the following order. It stops searching as soon as it finds a valid set of credentials.

### 1. Environment Variables
The SDK first checks the system environment variables. This is often the preferred method for CI/CD pipelines or running quick local scripts.
*   `AWS_ACCESS_KEY_ID`
*   `AWS_SECRET_ACCESS_KEY`
*   `AWS_SESSION_TOKEN` (Optional, required for assumed roles/temporary credentials)

### 2. Java System Properties (Java SDK Only)
If using Java, it checks `aws.accessKeyId` and `aws.secretKey`.

### 3. Web Identity Token credentials
This is typically used in environments like EKS (Elastic Kubernetes Service) where an OIDC token is injected into the container at the path defined by `AWS_WEB_IDENTITY_TOKEN_FILE`.

### 4. Credential Profiles (`~/.aws/credentials` and `~/.aws/config`)
The SDK looks for a local configuration file. This is the most common method for local developer environments.
*   It looks for the `AWS_PROFILE` environment variable to determine which profile to use.
*   If `AWS_PROFILE` is not set, it defaults to the profile named `default`.
*   **AWS SSO (Single Sign-On):** When using AWS Identity Center (SSO), the SDK reads the `~/.aws/config` file to find the SSO configuration and then automatically fetches temporary credentials from the local SSO cache directory (typically `~/.aws/sso/cache`).

### 5. Amazon ECS Container Credentials
If running within an Amazon Elastic Container Service (ECS) task, the SDK checks the `AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` or `AWS_CONTAINER_CREDENTIALS_FULL_URI` environment variables to fetch temporary credentials from the ECS agent.

### 6. Amazon EC2 Instance Metadata Service (IMDS)
**This is the final fallback.** If the SDK has found no credentials in steps 1-5, it assumes it is running on an Amazon EC2 instance. 
*   It attempts to connect to the non-routable IP address `169.254.169.254` to fetch temporary credentials associated with the IAM role attached to the EC2 instance (the Instance Profile).
*   If the code is actually running locally (or inside a local Docker container that hasn't had credentials mounted), this network request will fail or timeout, resulting in errors like: `cURL error 7: Failed to connect to 169.254.169.254`.
