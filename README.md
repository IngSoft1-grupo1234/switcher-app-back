# swicher-app-back

## Build complete App
### Docker Compose Setup

This application its divided in two repositories independently (the frontend side and -this repo- the backend). We use docker-compose to connect  correctly both sides.

## Prerequisites

Make sure you have Docker desktop installed
```bash
docker-compose --version 

# Output must be like:
# docker-compose version 1.26.0, build d4451659
```
- [Docker Desktop](https://www.docker.com/products/)

## Getting Started

### 1. Download the bundle

- [Swicher App Bundle](https://drive.google.com/drive/folders/1DsaiK8SpzdQuC_8j8ipUK7_95a_7CCJw?usp=sharing)

### 2. Unzip the file and  open a terminal in the folder

```bash
. # <- You  must be here.
├── docker-compose.yml
├── swicher-app-back
└── swicher-app-front

```

### 3. Build and Start the Containers

To build the images and start the containers, run:

```bash
docker-compose up --build
```

This will build the Docker images specified in the `docker-compose.yml` file and start all services in detached mode.

### 4. Access the Application

Once the services are up, you can access the application in your browser (`http://localhost` to see the frontend and `http://localhost:8000` is the entry point to the backend).

You can check the logs of the containers in the same terminal:


### 5. Stop the Containers

To stop the running containers, run:

```bash
# Press: Ctrl+C
```

## Run Backend in dev mode

### 1. Download this repo
```bash
 git clone https://github.com/IngSoft1-grupo1234/swicher-app-back.git
 
 cd swicher-app-back
```

### 2. Built and Run virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --no-cache-dir --upgrade -r ./requirements.txt
```

### 3. Run views or tests
> Run uvicorn server 
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
 >This will start the server in development mode, and you will be able to access the API at [http://localhost/8000](http://localhost/8000) and the documentation with [Swagger UI endpoint](http://localhost:8000/docs).
 > To stop server: `Press: Ctrl+C`

> Run test with pytest
```bash
pytest
```
> If you want to exit from (.venv):
```bash
exit
```


