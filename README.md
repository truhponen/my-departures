# my-departures

My Deartures is a small utility that pulls stop schedules from HSL (Helsinki metropolitan transportation) APIs and publishes them to Telegram bots.

Image for Raspberry Pi is available in https://github.com/truhponen/my-departures/pkgs/container/my-departures


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
        # Configuration expects that there is volume. Docker image is build so that app is in "/app"-folder and configuration files are in "/app/data"-folder.
          - my-departures:${APP_DIR}/data:rw
        # Mapping localtime to container ensures that time in message is correct ... of course assuming server time is correct
          - /etc/localtime:/etc/localtime:ro

    volumes:
      my-departures:
        external: true

