# Url shortener

Url shortener app with an API + web frontend, made in Python using Django and its ORM model, featuring a user panel where links are managed, custom paths, and QR code generation. Deployed with the CDK for Terraform on Azure Container Apps and more

By using the free tier of Azure Container Apps and the Azure SQL free offer this project can be deployed for free:

https://learn.microsoft.com/en-us/azure/azure-sql/database/free-offer?view=azuresql

The project structure is split into two, the app folder which was created using this django template:

```
django-admin startproject urlshortener
cd urlshortener
python manage.py startapp webapp 
```

and the infra folder which was created using this cdktf template:

`cdktf init --template=typescript --providers=azurerm --local`

# Setup instructions

Regardless of how you deploy this app, there are some environment variables that should be set in production, for development you don't need to set anything and default debug options will be used

<details>
  <summary>Environment variables</summary>
  For production you should turn off the debug mode, set a secret key and which domains the app will be served from

  ```
  DJANGO_KEY=(secret key)
  DJANGO_DEBUG=false
  DJANGO_HOSTS=example.com,www.example.com
  DJANGO_CSRF=https://example.com,https://www.example.com
  ```

  To generate the secret key you can use a service like https://djecrety.ir/ or a password manager, note that it should be at least 50 characters

  Setting `DB_EXTERNAL=true` will allow you to set the following, with the default values:

  ```
  DB_ENGINE=mssql
  DB_NAME=database
  DB_USER=root
  DB_PASSWORD=password
  DB_HOST=example.database.windows.net
  DB_PORT=1433
  ```

  Otherwise, a `db.sqlite3` file will be created at the root of the project (where manage.py is)

  See the `app/urlshortener/settings.py` file for more info
</details>

## Install the app 

There are several options for installing the app, here is a non exhaustive list:

<details>
  <summary>CDK for Terraform</summary>

  For this approach you will need cdktf-cli: https://developer.hashicorp.com/terraform/tutorials/cdktf/cdktf-install

  Running `ckdtf deploy` will automagically deploy this application to Azure, `cdktf destroy` will delete the provisioned resources

  The CI/CD pipleine of this repository does this for you
</details>

<details>
  <summary>Docker</summary>

  For this approach you will need Docker: https://www.docker.com

  Running `docker compose up` will build the Dockerfile in the current directory and start 3 containers, the python app, a mssql database and an nginx static file server

  Alternatively, you can run just the python app like this:

  ```
  docker build -t urlshortener:latest .
  docker run --name urlshortener -d --restart unless-stopped -p 8000:8000 urlshortener:latest
  ```

  If you're deploying to the cloud, make sure you build for the right platform e.g `--platform linux/amd64`
</details>

<details>
  <summary>Manual installation</summary>

  For this approach you will need Python (and pip): https://www.python.org/ 

  to get started install the dependencies

  `pip install -r requirements.txt`

  Then this command to apply them

  `python manage.py migrate`

  Now you're ready to start the server, you may use the built in development server

  `python manage.py runserver`

  or gunicorn which is used in the docker image

  `gunicorn urlshortener.wsgi`
</details>

## Visit the website

If you started the app locally you can see it at http://127.0.0.1:8000/

Otherwise visit your domain e.g https://example.com/

To create the admin user run this from the root of the project

`python manage.py createsuperuser`

Then you will be able to login with those credentials at https://example.com/admin/

## Notes

When changing the database model run this command to create a migration file, then run the migrate command

`python manage.py makemigrations webapp`

This project was tested with Python 3.12, Terraform 1.9.5, and django 4.2, if you encounter any errors with newer versions do try to patch them up

## Thanks to

https://github.com/davidshimjs/qrcodejs
