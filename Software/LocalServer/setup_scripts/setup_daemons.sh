#!/bin/bash

cp pub.service /etc/systemd/system/pub.service
cp pulldb.service /etc/systemd/system/pulldb.service

systemctl enable pub.service
systemctl enable pulldb.service

systemctl daemon-reload

systemctl restart pub.service
systemctl restart pulldb.service
