from fastapi import FastAPI, Response
import argparse
import time

# Create the FastAPI instance
app = FastAPI()

# Define the root endpoint ("/")
@app.get("/")
async def read_root(response: Response):
    response.status_code = 200
    return {"message": f"Hello World from server {port_number}"}

@app.get("/health")
async def read_health(response: Response):
    response.status_code = 200
    return {"message": "Healthy"}

@app.get("/task1")
async def read_task1(response: Response):
    time.sleep(2)
    response.status_code = 200
    return {"message": "Task 1 completed"}

# Function to start the FastAPI app
def start_fastapi_server(port):
    import uvicorn
    global port_number
    port_number = port 
    uvicorn.run(app, host="0.0.0.0", port=port)

# Main entry point
if __name__ == "__main__":
    # Use argparse to get the port number from the command line
    parser = argparse.ArgumentParser(description="Start FastAPI server")
    parser.add_argument("--port", type=int, default=8080, help="Port number to run the server on")
    
    args = parser.parse_args()
    
    # Run the FastAPI app with the port from command-line argument
    start_fastapi_server(args.port)