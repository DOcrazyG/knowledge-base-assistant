import uvicorn
from app.core.init_db import create_tables, init_data
from app.api.api import app

create_tables()
init_data()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
