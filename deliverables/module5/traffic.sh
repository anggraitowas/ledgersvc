for i in $(seq 1 60); do
  curl -s -o /dev/null http://10.0.110.240:30080/ready
  curl -s -o /dev/null http://10.0.110.240:30080/health
  curl -s -o /dev/null http://10.0.110.240:30080/balance
  sleep 1
done

echo "Traffic generation selesai"
