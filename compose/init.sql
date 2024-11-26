IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'urlshortener')
BEGIN
    CREATE DATABASE urlshortener;
END;
GO