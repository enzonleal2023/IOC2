import sqlite3
import uvicorn
import os
import secrets
from typing import Annotated
from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse
from fastapi import FastAPI


app = FastAPI()
security = HTTPBasic()

def get_current_username(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    current_username_bytes = credentials.username.encode("utf-8")
    correct_username_bytes = b"admin"
    is_correct_username = secrets.compare_digest(current_username_bytes, correct_username_bytes)
    current_password_bytes = credentials.password.encode("utf-8")
    correct_password_bytes = b"admin"
    is_correct_password = secrets.compare_digest(current_password_bytes, correct_password_bytes)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/")
async def root(username: Annotated[str, Depends(get_current_username)]):
    return RedirectResponse(url="/docs")

@app.get("/ips", )
async def read_ips():
    script_dir = os.path.dirname(__file__)
    db = os.path.join(script_dir, 'attackers_ips.db')

    conection = sqlite3.connect(db)
    cursor = conection.cursor()
    cursor.execute("SELECT * FROM attackers")

    ips = cursor.fetchall()
    ips_return = dict(ips)

    return {"IPS": ips_return}


@app.get("/ips/{ip}")
async def read_ip(ip: str):
    script_dir = os.path.dirname(__file__)
    db = os.path.join(script_dir, 'attackers_ips.db')
    conection = sqlite3.connect(db)
    cursor = conection.cursor()
    cursor.execute("SELECT * FROM attackers WHERE ip = ?", (ip,))
    ip = cursor.fetchall()

    ip_return = dict(ip)
    key = list(ip_return.keys())
    value = list(ip_return.values())

    return {"IP": key[0], "Ports": value[0]}

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8099,
                log_level="info", reload=True)
    print("running")