#!/bin/sh
set -e

# Start SQL Server in the background
/opt/mssql/bin/sqlservr &

# Give SQL Server time to start
sleep 10

# Run SQL script
/opt/mssql-tools*/bin/sqlcmd -C -S localhost -U sa -i /init/init.sql -b

# Wait for SQL Server to exit
wait