docker run --rm -d --name prometheus -p 9090:9090 \
       -v `pwd`/conf_dir:/etc/prometheus \
       --add-host=host.docker.internal:host-gateway \
       prom/prometheus
