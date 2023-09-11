#!/bin/bash

cat > user_data <<EOF
#cloud-config
password: ubuntu
chpasswd: { expire: False }
ssh_pwauth: True
EOF

cloud-localds user_data.img user_data

rm user_data
