## Database Migrations

## Initialize Database

WARNING: RUN THIS IN DEVELOPMENT

```shell
docker exec -it backend-api bash

# alembic init alembic
alembic -c db/migrations/alembic.ini revision --autogenerate -m "Initialize DB"
alembic -c db/migrations/alembic.ini upgrade head
```
