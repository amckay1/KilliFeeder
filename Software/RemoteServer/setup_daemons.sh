#!/bin/bash

cp sub.service /etc/systemd/system/sub.service
#cp dbsync.service /etc/systemd/system/dbsync.service

systemctl enable sub.service
#systemctl enable dbsync.service

systemctl daemon-reload

systemctl restart sub.service
#systemctl restart dbsync.service
