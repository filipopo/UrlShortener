#!/usr/bin/env python

import os
from constructs import Construct

from cdktf import App, TerraformStack, CloudBackend, TerraformOutput, NamedCloudWorkspace

from cdktf_cdktf_provider_azurerm import (
    provider, resource_group, static_web_app,
    container_app_environment, container_app,
    mssql_server, mssql_database
)

from cdktf_cdktf_provider_azurerm.container_app import (
    ContainerAppTemplate, ContainerAppTemplateContainer, ContainerAppTemplateContainerEnv,
    ContainerAppTemplateHttpScaleRule, ContainerAppIngress, ContainerAppIngressTrafficWeight
)


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # Initialize the Azure Provider
        provider.AzurermProvider(
            self,
            'AzureRm',
            features=[{}],
            subscription_id=os.getenv('SUBSCRIPTION_ID'),
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            tenant_id=os.getenv('TENANT_ID')
        )

        # Define Resource Group
        rg = resource_group.ResourceGroup(
            self,
            'ResourceGroup',
            location='WestEurope',
            name='url-resource-group'
        )

        # Define Static Web App
        app_web = static_web_app.StaticWebApp(
            self,
            'StaticWebApp',
            name='urlshortener',
            resource_group_name=rg.name,
            location=rg.location
        )

        # Define Container App Environment
        app_env = container_app_environment.ContainerAppEnvironment(
            self,
            'AppEnv',
            name='urlshortener-env',
            resource_group_name=rg.name,
            location=rg.location
        )

        # Define Container App
        app = container_app.ContainerApp(
            self,
            'App',
            name='urlshortener',
            resource_group_name=rg.name,
            container_app_environment_id=app_env.id,
            revision_mode='Single',
            workload_profile_name='Consumption',
            template=ContainerAppTemplate(
                min_replicas=0,
                max_replicas=2,
                container=[
                    ContainerAppTemplateContainer(
                        name='web',
                        image=os.getenv('DOCKER_IMAGE', 'filipmania/urlshortener:latest-mssql'),
                        cpu=0.25,
                        memory='0.5Gi',
                        env=self.template_env({
                            'DJANGO_KEY': os.getenv('DJANGO_KEY', 'f5e(7#=7yo#v2-*5@_0o-2ru9ok!0axucv)=_p$!7fg)4lp=0##x24p2=)9$zck_o('),
                            'DJANGO_DEBUG': 'false',
                            'DJANGO_HOSTS': os.getenv('DJANGO_HOSTS', '*'),
                            'DJANGO_CSRF': os.getenv('DJANGO_CSRF', 'http://127.0.0.1,http://127.0.0.1:8000'),
                            'DJANGO_STATIC': os.getenv('DJANGO_STATIC', 'static/'),
                            'DB_EXTERNAL': 'true',
                            'DB_NAME': os.getenv('DB_NAME', 'urlshortener'),
                            'DB_USER': os.getenv('DB_USER', 'urlshortener'),
                            'DB_PASSWORD': os.getenv('DB_PASSWORD', 'P@ssw0rd!'),
                            'DB_HOST': os.getenv('DB_HOST', 'urlshortener.database.windows.net')
                        })
                    )
                ],
                http_scale_rule=[
                    ContainerAppTemplateHttpScaleRule(
                        name='http-scaler',
                        concurrent_requests='10'
                    )
                ]
            ),
            ingress=ContainerAppIngress(
                external_enabled=True,
                target_port=8000,
                traffic_weight=[
                    ContainerAppIngressTrafficWeight(
                        latest_revision=True,
                        percentage=100
                    )
                ]
            )
        )

        # Define Azure SQL
        sql_server = mssql_server.MssqlServer(
            self,
            'SqlServer',
            name=os.getenv('DB_NAME', 'urlshortener'),
            location=rg.location,
            resource_group_name=rg.name,
            administrator_login=os.getenv('DB_USER', 'urlshortener'),
            administrator_login_password=os.getenv('DB_PASSWORD', 'P@ssw0rd!'),
            version='12.0'
        )

        _ = mssql_database.MssqlDatabase(
            self,
            'Database',
            name=sql_server.name,
            server_id=sql_server.id,
            storage_account_type='Local'
        )

        TerraformOutput(
            self,
            'fqdn',
            value=app.ingress.fqdn
        )

        TerraformOutput(
            self,
            'swa',
            sensitive=True,
            value=app_web.api_key
        )

    def template_env(self, env):
        res = []

        for key, value in env.items():
            res.append(ContainerAppTemplateContainerEnv(
                name=key,
                value=value
            ))

        return res


app = App()
stack = MyStack(app, 'urlshortener-stack')

CloudBackend(
    stack,
    hostname='app.terraform.io',
    organization='fistodul',
    workspaces=NamedCloudWorkspace('urlshortener')
)

app.synth()
