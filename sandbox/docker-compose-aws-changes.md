# Docker Compose AWS Credential Changes (AWS SSO)

Since you are using AWS SSO, the AWS SDK needs access to both your `config` file and the temporary tokens stored in the `sso/cache` directory. 

Many AWS SDKs hardcode the search path for the SSO cache to `~/.aws/sso/cache` (ignoring custom environment variables). Therefore, the most reliable way to make SSO work inside Docker is to mount your local `~/.aws` folder directly to the container user's home directory.

Assuming your container runs as `root`, add the following to both the `modx-php` and `laravel` services in your `docker-compose.yml`:

### 1. Add to `volumes:`
```yaml
      # Mount the entire .aws directory (including config and sso/cache) to the container's home
      - ~/.aws:/root/.aws:ro
```
*(Note: If your container runs as a different user like `www-data`, change `/root/.aws` to `/var/www/.aws` or the appropriate home path).*

### 2. Add to `environment:`
```yaml
      # Tell the AWS SDK to use the 'optic' profile
      - AWS_PROFILE=optic
```
