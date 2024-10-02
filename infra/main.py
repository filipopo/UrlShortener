#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack
from cdktf_cdktf_provider_azurerm import AzurermProvider, ResourceGroup, ContainerApp, ContainerAppEnvironment, PostgreSqlServer, PostgreSqlDatabase


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # Initialize the Azure Provider
        AzurermProvider(self, "AzureRm", features={})

        # Define Resource Group
        resource_group = ResourceGroup(
            self,
            "ResourceGroup",
            location="WestEurope",
            name="url-resource-group"
        )

        # Define Container App Environment
        app_env = ContainerAppEnvironment(
            self,
            "AppEnv",
            name="my-container-app-env",
            resource_group_name=resource_group.name,
            location=resource_group.location
        )

        # Define Container App
        app = ContainerApp(
            self,
            "App",
            name="my-django-app",
            resource_group_name=resource_group.name,
            container_app_environment_id=app_env.id,
            image="your-docker-image:latest",
            cpu="0.25", memory="0.5Gi"
        )

        # Define Azure SQL
        sql_server = PostgreSqlServer(
            self,
            "PostgreSqlServer",
            name="my-sql-server",
            location=resource_group.location,
            resource_group_name=resource_group.name,
            administrator_login="adminlogin",
            administrator_login_password="adminpassword",
            sku_name="GP_Gen5_2"
        )

        database = PostgreSqlDatabase(
            self,
            "Database",
            name="my-db",
            resource_group_name=resource_group.name,
            server_name=sql_server.name
        )


app = App()
MyStack(app, "urlshortener-stack")

app.synth()
