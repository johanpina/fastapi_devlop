# Clase en vídeo (01/12/2022): https://www.twitch.tv/videos/1667582141

### Users API ###

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Inicia el server: uvicorn users:app --reload

router = APIRouter(tags=["users"],
                   responses={404:{"message":"No encontrado"}})


class User(BaseModel):
    id: int
    name: str
    surname: str
    url: str
    age: int


users_list = [User(id=1, name="Brais", surname="Moure", url="https://moure.dev", age=35),
              User(id=2, name="Moure", surname="Dev",
                   url="https://mouredev.com", age=35),
              User(id=3, name="Brais", surname="Dahlberg", url="https://haakon.com", age=33)]


@router.get("/usersjson")
async def usersjson():  # Creamos un JSON a mano
    return [{"name": "Brais", "surname": "Moure", "url": "https://moure.dev", "age": 35},
            {"name": "Moure", "surname": "Dev",
                "url": "https://mouredev.com", "age": 35},
            {"name": "Haakon", "surname": "Dahlberg", "url": "https://haakon.com", "age": 33}]


@router.get("/users")
async def users():
    return users_list


@router.get("/user/{id}")  # Path
async def user(id: int):
    return search_user(id)


@router.get("/user/")  # Query
async def user(id: int):
    return search_user(id)


@router.post("/user/", response_model= User ,status_code=201)
async def user(user: User):
    if type(search_user(user.id)) == User:
        raise HTTPException(status_code=404,detail="El usuario ya existe")
        #return {"error": "El usuario ya existe"}
    
    users_list.append(user)
    return user #{"msg": "El usuario ha sido creado"}

@router.put("/user/")
async def user(user: User):

    found = False

    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            users_list[index] = user
            found = True

    if not found:
        return {"error": "No se ha actualizado el usuario"}
    
    return user

@router.delete("/user/{id}")
async def user(id : int):

    found = False

    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            del users_list[index]
            found = True

    if not found:
        return {"error": "No se ha eliminado el usuario"}
    
    return {"msg": "Usuario eliminado con éxito"}

def search_user(id: int):
    users = filter(lambda user: user.id == id, users_list)
    try:
        return list(users)[0]
    except:
        return {"error": "No se ha encontrado el usuario"}
