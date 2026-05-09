import time
import json
import urllib.request
import os

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/ps"
# Replace with the actual path your Node Exporter is watching
METRIC_FILE = "/home/ubuntu/ollama/LLM-Monitoring/textfile_collector/local-metrics.prom"
# METRIC_FILE = "/var/lib/prometheus/node-exporter/ollama_metrics.prom"
# Polling interval in seconds
INTERVAL = 15

def get_pi_temp():
    """Reads the Pi 5 SoC temperature."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            # Convert millidegrees to Celsius
            return float(f.read().strip()) / 1000.0
    except Exception:
        return 0.0

def get_ram_usage():
    """Calculates used RAM in bytes from /proc/meminfo."""
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
        mem_total = 0
        mem_available = 0
        for line in lines:
            if line.startswith("MemTotal:"):
                mem_total = int(line.split()[1]) * 1024
            elif line.startswith("MemAvailable:"):
                mem_available = int(line.split()[1]) * 1024
        return mem_total - mem_available
    except Exception:
        return 0

def get_ollama_memory():
    """Hits the Ollama API to see how much RAM the loaded models are using."""
    try:
        req = urllib.request.Request(OLLAMA_URL)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            # Sum up the 'size' of all currently loaded models
            total_size = sum(model.get("size", 0) for model in data.get("models", []))
            return total_size
    except Exception:
        # Returns 0 if Ollama is down or no models are loaded
        return 0

def main():
    print(f"Starting custom metrics exporter... Writing to {METRIC_FILE}")
    while True:
        temp = get_pi_temp()
        ram_used = get_ram_usage()
        ollama_mem = get_ollama_memory()

        metrics_payload = f"""# HELP pi5_custom_temperature_celsius Pi 5 CPU Temperature
# TYPE pi5_custom_temperature_celsius gauge
pi5_custom_temperature_celsius {temp}

# HELP pi5_custom_ram_used_bytes Pi 5 RAM Used
# TYPE pi5_custom_ram_used_bytes gauge
pi5_custom_ram_used_bytes {ram_used}

# HELP ollama_custom_model_memory_bytes Total memory used by loaded Ollama models
# TYPE ollama_custom_model_memory_bytes gauge
ollama_custom_model_memory_bytes {ollama_mem}
"""
        # Write to temporary file first
        with open(METRIC_FILE, "w") as f:
            f.write(metrics_payload)
        
        # Atomic rename prevents Node Exporter from reading a half-written file
        # os.rename(METRIC_FILE_TMP, METRIC_FILE)
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
