To dump the database schema to a file, run

```
pg_dump -h winhost -p 5432 -d <database> -U postgres -s -F p -E UTF-8 -f <outfile>.sql
```