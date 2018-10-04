#startup script for Proximity Occupation Sensor - Main Server
# Daniel Osmond
# 5/10/18
# Version 1.3

#User Configurable Variables
$endpoint = "ak3vkd3cgbh1r.iot.us-east-1.amazonaws.com"
$rootCert = "root-CA.crt"
$certName = "af6ff9c159"
$id = "seatServer"
$topic = "seating"

#assemble certificate names
$cert = $certName + "-certificate.pem.crt"
$privKey = $certName + "-private.pem.key"

#start server
python2.7 server.py -e $endpoint -r $rootCert -c $cert -k $privKey -id $id -t $topic -verbose

