# Turing @ DMF: containerization using Docker

## 1. Set up the host server

In the following we assume that the host server is based on Debian, or derivative distributions.

1. Install `docker` following the instructions in the [official documentation](https://docs.docker.com/engine/install/debian/#install-using-the-repository).
2. Clone the **Turing @ DMF** repository as follows:
```
git clone --recurse-submodules https://github.com/dmf-unicatt/turing-dmf.git
```

## 2. Set up the docker container

1. All the following instructions are supposed to be run in the `turing-dmf/docker` directory:
```
cd turing-dmf/docker
```
2. Create a secret key for `django` and a password for `postgresql`:
```
bash docker_create_secrets.sh
```
3. Create a docker volume that will contain the database:
```
bash docker_create_volume.sh
```
4. Create a `turing-dmf:latest` docker image based on the current **Turing @ DMF** repository:
```
bash docker_create_image.sh
```
5. Create a docker container based on the current `turing-dmf:latest` docker image:
```
bash docker_create_container.sh
```

## 3. Run the docker container

1. All the following instructions are supposed to be run in the `turing-dmf/docker` directory:
```
cd turing-dmf/docker
```
2. Start the container, including the `django` server:
```
bash docker_start.sh
```
**Turing** will be available at `https://host-server:8080`. The database will be initialized upon the first run.
3. Attach a terminal to the running docker container
```
bash docker_terminal.sh
```
4. Explore the database volume with
```
bash docker_explore_volume.sh
```
5. Stop the running docker container
```
bash docker_stop.sh
```

## 4. Rebuild the docker container

The docker container must be rebuilt upon doing a `git pull` of **Turing @ DMF**.

1. All the following instructions are supposed to be run in the `turing-dmf/docker` directory:
```
cd turing-dmf/docker
```
2. Destroy the existing container
```
bash docker_destroy_container.sh
```
Note that:
- the container must not be running in order to destroy it.
- secrets will be preserved upon destroying the container, and must not be regenarated.
- database volume (including the database itself) will be preserved upon the destroying the container, and must not be regenerated.
3. Refresh the `turing-dmf:latest` docker image based on the updated **Turing @ DMF** repository:
```
bash docker_create_image.sh
```
4. Create a docker container based on the refreshed `turing-dmf:latest` docker image:
```
bash docker_create_container.sh
```
