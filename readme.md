# Hack the North Backend Challenge

Start with:


```bash
python3 create.py # only run once, nukes DB
export FLASK_APP=server.py && export FLASK_DEBUG=1 && flask run
```


Endpoints:

`GET localhost:5000/users` lists all users

`GET localhost:5000/users/<id>` lists a user by id

`POST localhost:5000/users/123/` updates a user with the passed fields (requires `application/json` Content-Type)

`GET localhost:5000/skills` lists all skills, with optional querystring parameters of `rating` and `frequency` which selects skills with a minimum average rating and frequency
