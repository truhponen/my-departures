# my-departures

Docker Compose file
    
    version: '3'
    
    # Transit-stack
    # My Departures service
    services:
      my-departures:
        image: "truhponen/my-departures:latest"
        restart: unless-stopped
        privileged: true

    # Host network mode is used to avoid random troubles 
        network_mode: host

    # Ports are needed only when webhook is developed
    #    ports:
    #      - 8123:8123/tcp

        volumes:
          - my-departures:/my-departures/data:rw
          - /etc/localtime:/etc/localtime:ro

# Mounting NFS drive

Followed these instructions: https://cloudinfrastructureservices.co.uk/how-to-install-nfs-on-debian-11-server/

1. Create folder

2. Add to "exports"-file...

    sudo nano /etc/exports

... a statement that allows NFS-connections to folder

    /nfs/postgres 192.168.68.0/24(rw,sync,no_subtree_check,no_root_squash)

3. Create volume in Docker
