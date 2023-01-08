# my-departures

Docker Compose file
    
    version: '3'

    services:
      my-departures:
        # latest and dev images available
        image: "truhponen/my-departures:latest"
        restart: unless-stopped
        privileged: true

        # Host network mode is used to avoid random troubles 
        network_mode: host

        volumes:
        # Configuration expects that there is volume
        # Docker image is build so that app is in "/app"-folder
          - my-departures:${APP_DIR}/data:rw
        # Mapping localtime to container ensures that time in message is correct ... of course assuming server time is correct
          - /etc/localtime:/etc/localtime:ro

    volumes:
      my-departures:
        external: true

# Mounting NFS drive

Followed these instructions: https://cloudinfrastructureservices.co.uk/how-to-install-nfs-on-debian-11-server/

1. Create folder

2. Add to "exports"-file...

        sudo nano /etc/exports

3. ... a statement that allows NFS-connections to folder

        /nfs/postgres 192.168.68.0/24(rw,sync,no_subtree_check,no_root_squash)

4. Restart NFS server

        systemctl restart nfs-server
        
5. Create volume in Docker
