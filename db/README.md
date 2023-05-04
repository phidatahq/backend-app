## Database Migrations

## Initialize Database

WARNING: RUN THIS IN ONLY IN DEVELOPMENT

```shell
docker exec -it backend001-api-container zsh

# cd db
# alembic init migration
alembic -c db/alembic.ini revision --autogenerate -m "Initialize DB"
alembic -c db/alembic.ini upgrade head
```
