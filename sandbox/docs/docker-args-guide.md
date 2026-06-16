# Passing Arguments from Docker Compose to Dockerfile

To pass arguments into a Dockerfile from a Docker Compose file, you use the `ARG` instruction in your Dockerfile and the `build.args` mapping in your `docker-compose.yml`.

## 1. Define the `ARG` in your Dockerfile

In your `Dockerfile` (e.g., `gemini-sdbx.Dockerfile`), use the `ARG` instruction to declare a variable. You can also provide an optional default value. You then use this argument during the build process (like in a `RUN` command or to set an `ENV` variable).

```dockerfile
# gemini-sdbx.Dockerfile

FROM ubuntu:latest

# Declare the argument (with an optional default value)
ARG APP_VERSION="1.0"
ARG ENVIRONMENT

# You can use the ARG to set an Environment variable that persists in the running container
ENV APP_ENV=${ENVIRONMENT}

# Or use it during the build process
RUN echo "Building version $APP_VERSION for $ENVIRONMENT"
```

## 2. Pass the argument via `docker-compose.yml`

In your `docker-compose.yml` (e.g., `gemini-sdbx-compose.yml`), under the `build` section for your service, use the `args` keyword to pass values to the `ARG`s defined in the Dockerfile.

```yaml
# gemini-sdbx-compose.yml

services:
  my-app:
    build:
      context: .
      dockerfile: gemini-sdbx.Dockerfile
      args:
        # Pass a specific value
        ENVIRONMENT: production
        # Override the default value set in the Dockerfile
        APP_VERSION: "2.5"
```

## 3. (Optional) Pass arguments from your host environment

If you don't want to hardcode the values in your `docker-compose.yml`, you can pass them from your host machine's environment variables or an `.env` file.

**Using host environment variables in docker-compose.yml:**

```yaml
services:
  my-app:
    build:
      context: .
      dockerfile: gemini-sdbx.Dockerfile
      args:
        # This will take the value of the ENVIRONMENT variable from your host system
        ENVIRONMENT: ${ENVIRONMENT}
```

Then, you can run the compose command like this:
```bash
ENVIRONMENT=staging docker compose -f gemini-sdbx-compose.yml build
```

**Alternative shortcut:** 
If the key in `args` matches the environment variable name exactly, you can leave the value blank in the compose file, and Docker Compose will automatically look for it in your host environment or `.env` file:

```yaml
      args:
        - ENVIRONMENT # Grabs the value of $ENVIRONMENT from your shell
```
