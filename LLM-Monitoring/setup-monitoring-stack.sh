echo "\n --- Current working directory ---" pwd
allm_monitoring_directory= "/home/ubuntu/ollama/LLM-Monitoring"

echo "\n --- Listing files in current directory ---"
ls


echo "\n --- Starting monitoring stack ( Prometheus, Node Exporter and Grafana ) ---"
docker compose -f monitoring-compose.yaml up -d


echo "\n --- Starting scrapper python script to fetch raspberry temperature and memory usage ---"

ascrapper_image="ollama-metric-scrapper:latest"

docker ps --filter name="local-metric-scrapper"

# check if the above command return any container id or not
# if not, then start the container
docker run --name local-metric-scrapper -d ${ascrapper_image}
