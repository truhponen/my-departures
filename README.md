# my-departures

My Deartures is a small utility that pulls stop schedules from HSL (Helsinki metropolitan transportation) APIs and publishes them to Telegram bots.

Image for Raspberry Pi is available in https://github.com/truhponen/my-departures/pkgs/container/my-departures

## Docker Compose

Docker Compose file used to setup Docker container
    
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

## Configuration

Configuration file is used to configure solution.

properly filled config.yaml needs to be added to "/data"-folder.

    # Settings for sending HSL data to app.
    stops:
      HSL_1000103:  # Add ID of preferred station here
        stop_type: 'station' # Needed because HSL separates "stations" and "stop"
        app: 'Telegram'
        token: '[Add the bot token from Telegram here]'
        chat_id: '[add chat ID here]'  # Later this will be automated
      HSL_2000109:
        stop_type: 'station'
        app: 'Telegram'
        token: '[Add the bot token from Telegram here]'
        chat_id: '[add chat ID here]'  # Later this will be automated

    digitransit-subscription-key: '[Add HSL secret here]'

    # Settings for sending messages
    # How much earlier departures are sent
    time_distance: 900

    # Setting for updating data from HSL.
    initialize_departures_db: False  # If departures database is truncated during startup.
    update_frequency: 60  # How ofter new departures is requested from HSL.

    # Other settings
    logging_level: INFO  # Logs are stored in folder "logs/"
