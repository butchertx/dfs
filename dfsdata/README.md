# DFS Database

Accessing Postgresql in Windows host from WSL2:
https://stackoverflow.com/questions/56824788/how-to-connect-to-windows-postgres-database-from-wsl

What worked?
sudo apt install postgresql-client-14
Then 
psql -h winhost -p 5432 -U postgres
Then change host to "winhost" in .ini file
Unclear if the psql command above is needed to activate every time or not.