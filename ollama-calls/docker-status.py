import subprocess

def run_docker_ps():
    try:
        # Run the command and capture both standard output and errors
        result = subprocess.run(
            ["docker", "ps"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        # return the clean output string
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # Return the error message if the command fails (e.g., Docker daemon is stopped)
        return f"Error executing command: {e.stderr.strip()}"
    except FileNotFoundError:
        # Return error if docker itself is not installed on the system
        return "Error: 'docker' command line tool was not found."

# Run and print the result
output = run_docker_ps()
print(output)
