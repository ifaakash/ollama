set -e
echo -e "\n --- Current working directory ---" pwd
allm_monitoring_directory="/home/ubuntu/ollama/LLM-Monitoring"

# Safely change to the target monitoring directory
if [ -d "$allm_monitoring_directory" ]; then
   cd "$allm_monitoring_directory"
else
   echo "Error: Directory $allm_monitoring_directory does not exist!"
   exit 1
fi

echo -e "\n --- Listing files in current directory ---"
ls


echo "\n --- Starting monitoring stack ( Prometheus, Node Exporter and Grafana ) ---"
docker compose -f monitoring-compose.yaml up -d

ascrapper_image="ollama-metric-scrapper:latest"
container_name="local-metric-scrapper"
echo "\n --- Starting scrapper python script to fetch raspberry temperature and memory usage ---"

ascrapper_directory="/home/ubuntu/ollama/ollama-calls/monitoring"

# checking directory to validate if the compose file for running python scrapper script is presetn or not
# scrapper fetch the temperature and update the RAM usage
if [ -d "${ascrapper_directory}" ]; then
  cd "${ascrapper_directory}"
else
  echo "Error: Directory $ascrapper_directory does not exists!"
fi

echo -e "\n--- Cleaning up stopped containers ---"
stopped_containers= $(docker ps -a --filter status=exited -q)

if [ -n "${stopped_containers}" ]; then
  docker rm $stopped_containers
else
  echo "No stale container found!"
fi

if [ "$(docker ps -a -q -f name=^/${container_name}$)" ]; then
  if [ "$(docker ps -q -f name=^/${container_name}$)" ]; then
  	  echo "Container '${container_name}' is already running."
  else
      echo "Container '${container_name}' exists but is stopped. Starting it now..."
      docker compose -f scrapper-compose.yml up -d
  fi
else
  echo "Creating and starting new container '${container_name}'..."
  docker compose -f scrapper-compose.yml up -d
fi

docker ps --filter name="local-metric-scrapper"
