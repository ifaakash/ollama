# Learning: AWS Credentials with Docker Compose

## The Problem
When running an application inside a Docker container that uses the AWS SDK (like `boto3` or `botocore` in Python), it requires AWS credentials. A common approach is to mount the host machine's `~/.aws` directory into the container.

An error occurs if the volume is mounted incorrectly:

```yaml
    volumes:
     # INCORRECT: Mounts the ~/.aws directory as a folder named 'config' 
     # inside /root/.aws/
     - ${HOME}/.aws:/root/.aws/config:ro
```

This configuration results in the credentials file being located at `/root/.aws/config/credentials`, which is not where the AWS SDK expects it. This leads to a `botocore.exceptions.NoCredentialsError: Unable to locate credentials`.

## The Solution
To fix this, the host's `~/.aws` directory should be mounted directly to the container's `/root/.aws` directory (or the corresponding home directory for the container user).

```yaml
    volumes:
     # CORRECT: Mounts the ~/.aws directory directly to /root/.aws
     - ${HOME}/.aws:/root/.aws:ro
```

### Additional Note on AWS Profiles
If the application uses a specific AWS profile rather than the `default` profile, the `AWS_PROFILE` environment variable must also be passed to the container:

```yaml
    environment:
     - AWS_PROFILE=${AWS_PROFILE:-default}
```
