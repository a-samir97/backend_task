# Backend Task

## Changes 
- I have added two instances in docker compose `backend instance (django)` and `redis stack instance`

### How to run the project ?
- `docker-compose up`

### How to run unittests ?
- run the instance first by `docker-compose up`
- go to the terminal of backend instance 
- and run this command `python manage.py test`


### Documentation (Swagger page)
- run the project by `docker-compose up`
- then go to swagger page, `http://127.0.0.1:8000/swagger/`

### Endpoints 

- Get stock by name -> `GET /api/stocks/{stock_name}/`
- Get user details -> `GET /api/users/{user_id}/`
- User deposit -> `POST /api/users/{user_id}/deposit/`
- User withdraw -> `POST /api/users/{user_id}/withdraw/`
- Sell stocks -> `POST /api/users/{user_id}/sell/`
- Buy stocks -> `POST /api/users/{user_id}/buy/`

### Tools and frameworks used 
- Python 
- Django
- Django Rest Framework
- Redis
- Swagger Documentation 

## Improvments
- I think we can use noSQL database instead of redis `for example rethink database used for realtime database`
- use `base script` to run the backend instance after all other instances 
