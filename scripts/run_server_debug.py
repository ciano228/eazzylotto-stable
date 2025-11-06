import uvicorn
from server_postgres_simple import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081, log_level="debug")