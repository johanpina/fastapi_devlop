from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta


## Debemos usar e instalar python-jose[cryptography]
## passlib[bcrypt]


ALGORITHM = "HS256"
ACCES_TOKEN_DURATION = 1
## Se genera el secret así: openssl rand -hex 22
SECRET = "7d912e0a15a7e663e526a90167119f193a9348d291c2"

app = FastAPI()
oauth2 = OAuth2PasswordBearer(tokenUrl='login') ## esta autenticación es más simple que la de jwt
# vamos a seguir trabajando con autenticación por contraseña pero ahora encriptación.

crypt = CryptContext(schemes=["bcrypt"])

class User(BaseModel):
    username: str
    full_name: str
    email: str
    disable: bool

class UserDB(User):
    password: str

users_db = {
    "mouredev": {
        "username": "mouredev",
        "full_name": "Brais_moure",
        "email": "braismoure@mourede.com",
        "disable": False,
        "password": "$2a$12$WavWn//F9YjzvZiZrBS8ROhva7Rh9jGTsWAb/tvEaXjCqVNJYUoFO"
    },
    "moredev2": {
        "username": "mouredev2",
        "full_name": "Brais_moure",
        "email": "braismoure@mourede.com",
        "disable": True,
        "password": "$2a$12$WavWn//F9YjzvZiZrBS8ROhva7Rh9jGTsWAb/tvEaXjCqVNJYUoFO"
    }
}

def search_userdb(username: str):
    if username in users_db:
        return(User(**users_db[username]))

async def auth_user(token: str = Depends(oauth2)):
    
    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Credenciales de atenticacion invalidas", 
                            headers={"www-Authenticate": "Bearer"})

    try:
        username = jwt.decode(token,SECRET,algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception
  
    except JWTError:
        raise exception
    

    return search_userdb(username)


async def current_user(user: User = Depends(auth_user)):    
    if user.disable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Usuario inactivo", 
                            )

    return user
@app.post('/login')
async def login(form: OAuth2PasswordRequestForm = Depends()): # depends dice que recibe datos pero no depende de nadie
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400,detail="El usuario no es correcto")
    
    user = search_userdb(form.username)

    if not crypt.verify(form.password,user.password):
        raise HTTPException(status_code=400,detail="La contraseña no es correcta")
    
    expire = datetime.utcnow() + timedelta(minutes=ACCES_TOKEN_DURATION)

    access_token = {"sub":user.username,
                    "exp":expire}

    return {"access_token": jwt.encode(access_token,SECRET, algorithm=ALGORITHM),"token_type":'bearer'}


@app.get("/users/me")## ve a decir cual es mi usuario
async def me(user: User = Depends(current_user)):
    return user