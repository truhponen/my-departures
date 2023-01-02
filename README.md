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
