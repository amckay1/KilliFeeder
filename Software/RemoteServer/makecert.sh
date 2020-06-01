 #!/bin/bash
 openssl req -new -x509 -days 365 -extensions v3_ca -keyout my-ca.key -out my-ca.crt
 openssl genrsa -out server.key 2048
 openssl req -out server.csr -key server.key -new
 openssl x509 -req -in server.csr -CA my-ca.crt -CAkey my-ca.key -CAcreateserial -out server.crt -days 365
 mosquitto_pub --cafile my-ca.crt -h www.KilliFeeder.com -t test -m test


