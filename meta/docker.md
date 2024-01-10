## Docker cheatsheet

| Command                                                                                                                           | Description                                                                                                |
| --------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Remove all containers, images, volumes <br> ⚠️ EXTEMELY DESTRUCTIVE ⚠️                                                            | `docker system prune -a`                                                                                   |
| Clean run: remove all containers and builds it, useful for testing as it rebuilds it with one command <br> ⚠️ VERY DESTRUCTIVE ⚠️ | `docker ps -q \| xargs -r docker stop && docker ps -aq \| xargs -r docker rm && docker-compose up --build` |
