from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# OAuth2PasswordBearer gestina el usuario y la contraseña
# OAuth2PasswordRequestForm la forma en la que el backend envia desde el cliente el usr y la contraseña


app = FastAPI()

oauth2 = OAuth2PasswordBearer(tokenUrl='login') ## esta autenticación es más simple que la de jwt

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
        "password": "123456"
    },
    "moredev2": {
        "username": "mouredev2",
        "full_name": "Brais_moure",
        "email": "braismoure@mourede.com",
        "disable": True,
        "password": "123456"
    }
}


def search_user_db(username: str):
    if username in users_db:
        return(UserDB(**users_db[username]))

def search_user(username: str):
    if username in users_db:
        return(User(**users_db[username]))

async def current_user(token: str = Depends(oauth2)):
    user =  search_user(token)
    if not user: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Credenciales de atenticacion invalidas", 
                            headers={"www-Authenticate": "Bearer"})
    
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
    
    user = search_user_db(form.username)

    if not form.password == user.password:
        raise HTTPException(status_code=400,detail="La contraseña no es correcta")
    
    return {"access_token": user.username,"token_type":'bearer'}

    
@app.get("/users/me")## ve a decir cual es mi usuario
async def me(user: User = Depends(current_user)):
    return user
    
