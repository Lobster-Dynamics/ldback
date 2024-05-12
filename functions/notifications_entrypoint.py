from dotenv import load_dotenv 
load_dotenv("./.api.env")

from notifications_server import app # type: ignore
import uvicorn

if __name__ == "__main__": 
    uvicorn.run(app, host="0.0.0.0", port=8000)
