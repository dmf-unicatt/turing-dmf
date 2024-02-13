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
./create_secrets.sh
```
3. Create a docker volume that will contain the database:
```
./create_volume.sh
```
4. Create a `turing-dmf:latest` docker image based on the current **Turing @ DMF** repository:
```
./create_image.sh
```
5. Create a docker container based on the current `turing-dmf:latest` docker image:
```
./create_container.sh
```
6. Database is created upon the first run of the container with
```
./start_container.sh
```
The terminal will display the username and password of the administrator account, which can be subsequently changed through the web interface.

## 3. Run the docker container

1. All the following instructions are supposed to be run in the `turing-dmf/docker` directory:
```
cd turing-dmf/docker
```
2. Start the container, including the `django` server:
```
./start_container.sh
```
**Turing** will be available at `https://host-server:8080`.
3. Attach a terminal to the running docker container
```
./attach_terminal.sh
```
4. Explore the database volume with
```
./explore_volume.sh
```
5. Stop the running docker container
```
./stop_container.sh
```

## 4. Rebuild the docker container

The docker container must be rebuilt upon doing a `git pull` of **Turing @ DMF**.

1. All the following instructions are supposed to be run in the `turing-dmf/docker` directory:
```
cd turing-dmf/docker
```
2. Destroy the existing container
```
./destroy_container.sh
```
Note that:
- the container must not be running in order to destroy it.
- secrets will be preserved upon destroying the container, and must not be regenarated.
- database volume (including the database itself) will be preserved upon the destroying the container, and must not be regenerated.
3. Refresh the `turing-dmf:latest` docker image based on the updated **Turing @ DMF** repository:
```
./create_image.sh
```
4. Create a docker container based on the refreshed `turing-dmf:latest` docker image:
```
./create_container.sh
```

## 5. Tips and tricks

1. Protect secret and volume file from accidental deletion by running
```
./prevent_accidental_deletion.sh
```
