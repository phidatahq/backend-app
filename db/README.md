## Database Migrations

## Initialize Database

WARNING: RUN THIS IN DEVELOPMENT

```shell
docker exec -it backend001-api-container zsh

# alembic init alembic
alembic -c db/alembic.ini revision --autogenerate -m "Initialize DB"
alembic -c db/alembic.ini upgrade head
```
