
sudo rabbitmqctl add_user fcs_user $1
sudo rabbitmqctl add_vhost fcs_vhost
sudo rabbitmqctl set_user_tags fcs_user mytag
sudo rabbitmqctl set_permissions -p fcs_vhost fcs_user ".*" ".*" ".*"

rabbitmq-plugins enable rabbitmq_management