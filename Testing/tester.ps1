

$endpoint = "ak3vkd3cgbh1r.iot.us-east-1.amazonaws.com"
$rootCert = "root-CA.crt"
$certName = "af6ff9c159"
$id = "seatTester"
$topic = "seating"


$cert = $certName + "-certificate.pem.crt"
$privKey = $certName + "-private.pem.key"

python publishtester.py -e $endpoint -r $rootCert -c $cert -k $privKey -id $id -t $topic