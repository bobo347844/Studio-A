#startup script for Proximity Occupation Sensor - Remote Client
# Daniel Osmond
# 7/08/18

#User Configurable Variables
endpoint = "ak3vkd3cgbh1r.iot.us-east-1.amazonaws.com"
rootCert = "root-CA.crt"
certName = "af6ff9c159"
id = "seat01"
topic = "seating"
seat = "CB11.XX.XXX"

#assemble certificate names
cert = $certName + "-certificate.pem.crt"
privKey = $certName + "-private.pem.key"

#start client
python client.py -e $endpoint -r $rootCert -c $cert -k $privKey -id $id -t $topic -loc $seat -verbose