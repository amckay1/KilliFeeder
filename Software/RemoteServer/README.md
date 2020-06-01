On AWS: need to open custom TCP 8500 port to all IPs (0.0.0.0/0)

This works for code:
"""
 using Interact, Mux
 ui = button()
 display(ui)
 host = "0.0.0.0"
 WebIO.webio_serve(page(req -> ui), host, 8500)
"""

sudo iptables -A INPUT -i eth0 -p tcp --dport 8500 -j ACCEPT
sudo iptables -A INPUT -i eth0 -p tcp --dport 80 -j ACCEPT






make sure ufw allows 80 and 8500 
Do I need IP tables? [Doesn't seem to be critical]

https://www.digitalocean.com/community/tutorials/how-to-list-and-delete-iptables-firewall-rules
sudo iptables -t nat -A OUTPUT -o lo -p tcp --dport 80 -j REDIRECT --to-port 8500
sudo iptables -t nat -I OUTPUT -p tcp -o lo --dport 443 -j REDIRECT --to-ports 8500

sudo iptables -S looks like this:
-P INPUT ACCEPT
-P FORWARD ACCEPT
-P OUTPUT ACCEPT
-A INPUT -i eth0 -p tcp -m tcp --dport 80 -j ACCEPT
-A INPUT -i eth0 -p tcp -m tcp --dport 8500 -j ACCEPT

ufw is somehow inactive by status (sudo ufw status) so not sure if this is critical. 
