locust_file=$1
target_host='http://localhost:8042'
echo "Using file $locust_file"
locust --headless -f ./02-count-objects.py -u 2 -r 2 --run-time 1m --stop-timeout 30 --host=$target_host
