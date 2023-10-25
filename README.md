# vlsp2023

## Set up

**Create a new virtual enviroment (Python>=3.9) and activate it**

```bash
    python -m venv venv
    source venv/bin/activate
```
**Install requirements**

```bash
    pip install -r requirements.txt
```

## Demo

**Backend**
```bash
    cd backend
    python main.py
```
**Frontend**
```bash
    cd frontend
    python [task1/task2].py
``` 

## Docker
**How to build docker image**
```bash
    docker compose up -d --build
```
**How to run**

```bash
    docker image ls -a # Find the image's name
    docker run -p 5000:5000 <IMAGE NAME>
``` 

