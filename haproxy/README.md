

#help 
echo "?" | sudo -u haproxy socat stdio unix-connect:/var/run/haproxy/admin.sock

# show backend fleet
echo "show backend" | sudo -u haproxy socat stdio unix-connect:/var/run/haproxy/admin.sock

# show servers status
echo "show servers state <backend name>" | sudo -u haproxy socat stdio unix-connect:/var/run/haproxy/admin.sock


#health status
echo "show servers state <backend name>" | sudo -u haproxy socat stdio unix-connect:/var/run/haproxy/admin.sock | awk '{ print $4, $5, $6 }'




watch 'echo "show stat" | sudo -u haproxy socat stdio unix-connect:/var/run/haproxy/admin.sock | cut -d "," -f 1,2,5-11,18,24,27,30,36,50,37,56,57,62 | column -s, -t'


srv_op_state:
srv_op_state: Server operational state (UP/DOWN/...).
0 = SRV_ST_STOPPED - The server is down.
1 = SRV_ST_STARTING - The server is warming up (up but throttled).
2 = SRV_ST_RUNNING - The server is fully up.
3 = SRV_ST_STOPPING - The server is up but soft-stopping (eg: 404).
