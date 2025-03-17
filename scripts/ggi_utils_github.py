#!/usr/bin/python3
# ######################################################################
# Copyright (c) 2025 The OSPO Alliance contributors
#
# This program and the accompanying materials are made
# available under the terms of the Eclipse Public License 2.0
# which is available at https://www.eclipse.org/legal/epl-2.0/
#
# SPDX-License-Identifier: EPL-2.0
######################################################################

"""

"""
import glob
import json
import os
import urllib.parse
from datetime import date

import tldextract
from github import Auth, Github

from ggi_update_website import *


def retrieve_env_github():
    """
    Read metadata for activities and deployment options.

    Determine GitHub server URL and Project name
    * From Environment variable if available, or
    * From configuration file otherwise
    """
    # Get conf: Token
    if 'GGI_GITHUB_TOKEN' in os.environ:
        print("- Using token from env var 'GGI_GITHUB_TOKEN'")
        params['github_token'] = os.environ['GGI_GITHUB_TOKEN']
    else:
        print("- Cannot find env var GGI_GITHUB_TOKEN. Please set it and re-run me.")
        exit(1)
    auth = Auth.Token(params['github_token'])

    # Get conf: URL
    public_github="https://github.com"
    if 'GGI_GITHUB_URL' in os.environ:
        params['github_url'] = os.environ['GGI_GITHUB_URL']
        print("- Using URL from env var 'GGI_GITHUB_URL'")
    elif 'github_url' in params and params['github_url'] != None:
        print("- Using URL from configuration file")
    else:
        params['github_url'] = public_github
        print("- Using default public URL")

    # Manage authenticatation
    if params['github_url'].startswith(public_github):
        # Public Web Github
        print("- Using public GitHub instance.")
        g = Github(auth=auth)
    else:
        print(f"- Using GitHub on-premise host {params['github_url']} ")
        # Github Enterprise with custom hostname
        params['github_url'] = f"{params['github_url']}/api/v3"
        g = Github(auth=auth, base_url=params['github_url'])

    # Get conf: Project
    # P1: Search environment variable
    if 'GGI_GITHUB_PROJECT' in os.environ:
        params['github_project'] = os.environ['GGI_GITHUB_PROJECT']
        print("- Using Project from env var 'GGI_GITHUB_PROJECT'")
    # P2: Search Json configuration file
    elif 'github_project' in params and params['github_project'] != None:
        print(f"- Using Project from configuration file")
    # P3: Search GitHub action environment
    elif 'GGI_GITHUB_REPOSITORY' in os.environ:
        params['github_project'] = os.environ['GGI_GITHUB_REPOSITORY']
        print(f"- Using Project from GitHub action environment")
    else: # Give up.
        github.action_repository
        print("Could not determine project (org + repo), e.g. ospo-alliance/" +
              "my-ggi-board. Exiting.")
        exit(1)

    params['github_repo_url'] = urllib.parse.urljoin(params['github_url'], params['github_project'])
    params['github_activities_url'] = params['github_repo_url'] + '/projects'

    print("Configuration:")
    print("URL     : " + params['github_url'])
    print("Project : " + params['github_project'])
    print("Full URL: " + params['github_repo_url'])

#####################################################################""
    print(f"# Reading deployment options from {file_conf}.")
    with open(file_conf, 'r', encoding='utf-8') as f:
        params = json.load(f)

    if 'GGI_GITHUB_REPOSITORY' in os.environ: # github.repository
        params['GGI_GITHUB_PROJECT'] = os.environ['GGI_GITHUB_REPOSITORY']
        print(f"- Using GitHub project {params['GGI_GITHUB_PROJECT']} " +
              "from environment variable file.")
    elif 'github_project' in params:
        params['GGI_GITHUB_PROJECT'] = params['github_project']
        print(f"- Using GitHub project {params['github_project']} " +
              "from configuration file.")
    else:
        print("I need a project (org + repo), e.g. ospo-alliance/" +
              "my-ggi-board. Exiting.")
        exit(1)

    if 'GGI_GITHUB_TOKEN' in os.environ:
        print("- Using ggi_github_token from env var.")
        params['GGI_GITHUB_TOKEN'] = os.environ['GGI_GITHUB_TOKEN']
    else:
        print("- Cannot find env var GGI_GITHUB_TOKEN. Please set it and re-run me.")
        exit(1)

    if 'github_host' in params and params['github_host'] != 'null':
        print(f"- Using GitHub on-premises host {params['github_host']} " +
              "from configuration file.")
        # Github Enterprise with custom hostname
        params['GGI_API_URL'] = f"{params['github_host']}/api/v3"
        params['GGI_GITHUB_URL'] = urllib.parse.urljoin(params['github_host'] + '/', params['GGI_GITHUB_PROJECT'])
        params['GGI_PAGES_URL'] = 'https://fix.me'
    else:
        # Public Web GitHub
        params['GGI_API_URL'] = None
        params['GGI_GITHUB_URL'] = urllib.parse.urljoin('https://github.com/', params['GGI_GITHUB_PROJECT'])
        params['GGI_PAGES_URL'] = urllib.parse.urljoin(
            'https://' + re.sub('/.*$', '', params['GGI_GITHUB_PROJECT']) + '.github.io/', 
            re.sub('^.*/', '', params['GGI_GITHUB_PROJECT']))
        print("- Using public GitHub instance.")

    params['GGI_ACTIVITIES_URL']= urllib.parse.urljoin(params['GGI_GITHUB_URL'] + '/', 'issues')

    return params

def main():
    """
    Test Utils lib
    """
    params = retrieve_env_github()
    print("- GGI_GITHUB_PROJECT: " + params['GGI_GITHUB_PROJECT'])
    print("- GGI_GITHUB_URL: " + params['GGI_GITHUB_URL'])
    print("- GGI_PAGES_URL: " + params['GGI_PAGES_URL'])

if __name__ == '__main__':
    main()
