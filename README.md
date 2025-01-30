#  ❤️📦 Immich Auto Favorite/Archive 
This is a simple Python script (and a Docker container), that automatically marks images as favorite or archived depending on their rating in the Exif Metadata. The primary idea is to use this in combination with a backup script for another library (e.g. [icloudpd](https://github.com/icloud-photos-downloader/icloud_photos_downloader/) which marks hidden/deleted and favorite images with an exif rating in the xmp sidecar).

### 🔑 Obtaining an Immich API key
Instructions can be found in the Immich docs - [Obtain the API key](https://immich.app/docs/features/command-line-interface#obtain-the-api-key)

### 📃 Running as part of the Immich docker-compose.yml
Adding the container to Immich's `docker-compose.yml` file:

```yml
version: "3.8"
...
services:
  immich-server:
    container_name: immich_server
  ...

  immich-auto-archive-favorite:
    container_name: immich-auto-archive-favorite
    build: https://github.com/chkuendig/immich-auto-archive-favorite.git
    restart: unless-stopped
    environment:
  
      # This is default. Can be omitted. 
      API_URL: http://immich_server:3001/api

      # https://immich.app/docs/features/command-line-interface#obtain-the-api-key
      API_KEY: xxxxxxxxxxxxxxxxx

      # Run every hour. Use https://crontab.guru/ to generate new expressions.
      CRON_EXPRESSION: "0 */1 * * *"
```

## License

This project is licensed under the GNU Affero General Public License version 3 (AGPLv3) to align with the licensing of Immich, which this script interacts with. For more details on the rights and obligations under this license, see the [GNU licenses page](https://opensource.org/license/agpl-v3).

- Parts of this script are re-used from [tenekev/immich-auto-stack](https://github.com/tenekev/immich-auto-stack) which is also licensed under the AGPLv3.