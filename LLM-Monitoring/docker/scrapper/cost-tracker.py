import time

import requests

LITELLM_URL = "http://localhost:4000/spend/logs"
API_KEY = "qwertyuiop"
PARAMS = {"api_key": API_KEY, "summarize": "true"}
HEADERS = {"accept": "application/json", "x-litellm-api-key": API_KEY}
TEXTFILE_PATH = (
    "/home/ubuntu/ollama/LLM-Monitoring/textfile_collector/litellm-cost.prom"
)


def track_cost():
    while True:
        response = requests.get(LITELLM_URL, params=PARAMS, headers=HEADERS)

        if response.status_code == 200:
            result = response.json()
            metric = dict()

            for item in result:
                status = item.get("status")
                if not status and item.get("metadata"):
                    status = item["metadata"].get("status", "unknown")

                # Only track tokens for successful requests
                if status != "success":
                    continue

                model = item.get("model", "unknown_model")
                api_key = item.get("api_key", "unknown_key")
                prompt_tokens = item.get("prompt_tokens", 0)
                completion_tokens = item.get("completion_tokens", 0)

                key = (model, api_key)
                if key not in metric:
                    metric[key] = {"prompt_tokens": 0, "completion_tokens": 0}

                metric[key]["prompt_tokens"] += prompt_tokens
                metric[key]["completion_tokens"] += completion_tokens

            write_to_prom(TEXTFILE_PATH, metric)
            print("Metrics updated successfully.")

        else:
            print(f"Failed to fetch data: {response.status_code}")

        # Sleep happens no matter what (success or fail)
        time.sleep(15)


def write_to_prom(filepath, metric):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# HELP llm_prompt_tokens_total Total input tokens.\n")
        f.write("# TYPE llm_prompt_tokens_total counter\n")
        for (model, api_key), data in metric.items():
            f.write(
                f'llm_prompt_tokens_total{{model="{model}",api_key="{api_key}"}} {data["prompt_tokens"]}\n'
            )

        f.write("\n")
        f.write("# HELP llm_completion_tokens_total Total output tokens.\n")
        f.write("# TYPE llm_completion_tokens_total counter\n")
        for (model, api_key), data in metric.items():
            f.write(
                f'llm_completion_tokens_total{{model="{model}",api_key="{api_key}"}} {data["completion_tokens"]}\n'
            )


if __name__ == "__main__":
    track_cost()
