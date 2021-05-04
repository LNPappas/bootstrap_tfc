import os
import sys
import socket
import json
import time

from dotenv import load_dotenv
# from github import Github
import pyterprise
from termcolor import colored

load_dotenv()

tf_version = "0.14.5"
tfe_org_id = "db_test"
tfe_hostname = "app.terraform.io"
tfe_workspace = "workspace_a"
tfe_token = os.getenv("TF_TOKEN", "Terraform Enterprise token")
github_token = os.getenv("GITHUB_TOKEN", "Github oauth client token")
github_owner = os.getenv("GITHUB_OWNER", "Github owner")
service_account = os.getenv("SERVICE_ACCOUNT", "GCP Service Account")
project_name = os.getenv("PROJECT_ID", "GCP Project ID")
region = os.getenv("REGION", "GCP Project Region")
google_app_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "GCP Credentials for service account")
google_credentials = os.getenv("GOOGLE_CREDENTIALS", "GCP Credentials for service account")
git_oauth_client_token = os.getenv("GIT_OAUTH_CLIENT_TOKEN", "oauth client token from github")
# ? workspace_names = ("workspace_b", "workspace_c")

#  *Initialize GitHub
# git = Github(github_token)
# user = git.get_user()


# *initialize pyterprise
tfe_client = pyterprise.Client()
tfe_client.init(token=tfe_token, url=f'https://{tfe_hostname}', cert=True)
org = tfe_client.set_organization(id=tfe_org_id)

vcs_options = {
    "identifier": "LNPappas/Terraform-Cloud",
    "oauth-token-id": git_oauth_client_token,
    "branch": "main",
    "default-branch": True
}

#  *Create Workspace
workspace_options = {'tf_version':tf_version, 'vcs_repo':vcs_options, 'auto_apply':False}
org.create_workspace(name=tfe_workspace, **workspace_options)
workspace = org.get_workspace(tfe_workspace)
id = workspace.id

variable_values = {
    'GITHUB_TOKEN':                          {'value':github_token,           'sensitive':True,  'category':'env'},
    'github_token':                          {'value':github_token,           'sensitive':True,  'category':'terraform'},
    'TFE_TOKEN':                             {'value':tfe_token,              'sensitive':True,  'category':'env'},
    'TFE_HOSTNAME':                          {'value':tfe_hostname,           'sensitive':False, 'category':'env'},
    'SERVICE_ACCOUNT':                       {'value':service_account,        'sensitive':True,  'category':'env'},
    'GITHUB_OWNER':                          {'value':github_owner,           'sensitive':True,  'category':'env'},
    'google_credentials':                    {'value':google_app_credentials, 'sensitive':True,  'category':'terraform'},
    'project_name':                          {'value':project_name,           'sensitive':True,  'category':'terraform'},
    'region':                                {'value':region,                 'sensitive':True,  'category':'terraform'},
    'workspace_trigger_id':                  {'value':id,                     'sensitive':False, 'category':'terraform'},
}

# Add any current workspace variables to dict
print(colored(f'Checking {tfe_workspace} variables: ', attrs=['dark']), end='', flush=True)
for variable_name, variable_attributes in variable_values.items():
    workspace.create_variable(key=variable_name, **variable_attributes)
    print(colored('+', 'yellow'), end='', flush=True)
print(colored('Finished adding variables.', 'green'))

print(colored('Running workspace: ', 'yellow'), end='', flush=True)
run = workspace.run('Run by Bootstrap Program')
print(colored("On completion go to TFE and confirm.", "green"))

print(colored("checking if main workspace applied...", "red"))

wait = time.sleep(60)
status = workspace.get_current_state_version()
while status == None:
    status = workspace.get_current_state_version()
    print(colored("applying...", "magenta"))
    wait = time.sleep(60)
print(colored("Workspace applied, queing Plans:", "yellow"))


organizations = tfe_client.list_organizations()
for o in organizations:
    print(colored(f'Organization Name: ${o.name}', "cyan"))
    org_current = tfe_client.set_organization(id=o.name)
    work = org_current.list_workspaces()
    for w in work:
        print(colored(f'Workspace Name: ${w.name}', "", "magenta"))
        print(colored(f'Workspace ID: ${w.id}', "blue"))
        if w.name != "workspace_a":
            sub_workspace = org_current.get_workspace(w.name)
            if sub_workspace.description != None:
                sub_workspace.run('ran by test bootstrap')
            
print(colored("Plans queued.", "green"))