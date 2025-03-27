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
import urllib.parse

from github import Github, Auth

from ggi_deploy import *

public_github_root_url="https://github.com/"

def retrieve_params():
    """
    Read metadata for activities and deployment options.

    Determine GitHub server URL and Project name
    * From Environment variable if available, or
    * From configuration file otherwise
    """

    print(f"# Reading deployment options from {conf_file}.")
    with open(conf_file, 'r', encoding='utf-8') as f:
        params = json.load(f)

    # Get GGI_GITHUB_PROJECT
    # P1: Search environment variable
    if 'github_project' in os.environ:
        params['GGI_GITHUB_PROJECT'] = os.environ['github_project']
        print("- Using Project from env var 'GGI_GITHUB_PROJECT'")
    # P2: Search Json configuration file
    elif 'github_project' in params and params['github_project'] is not None:
        params['GGI_GITHUB_PROJECT'] = params['github_project']
        print(f"- Using Project from configuration file")
    # P3: Search GitHub action environment
    elif 'GITHUB_REPOSITORY' in os.environ:
        params['GGI_GITHUB_PROJECT'] = os.environ['GITHUB_REPOSITORY']
        print(f"- Using Project from GitHub action environment")
    else: # Give up.
        print("Could not determine project (org + repo), e.g. ospo-alliance/" +
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
        # GitHub Enterprise with custom hostname
        params['GGI_API_URL'] = f"{params['github_host']}/api/v3"
        params['GGI_GITHUB_URL'] = urllib.parse.urljoin(params['github_host'] + '/', params['GGI_GITHUB_PROJECT'])
        params['GGI_PAGES_URL'] = 'https://fix.me'
    else:
        # Public Web GitHub
        params['GGI_API_URL'] = None
        params['GGI_GITHUB_URL'] = urllib.parse.urljoin(public_github_root_url, params['GGI_GITHUB_PROJECT'])
        params['GGI_PAGES_URL'] = urllib.parse.urljoin(
            'https://' + re.sub('/.*$', '', params['GGI_GITHUB_PROJECT']) + '.github.io/',
            re.sub('^.*/', '', params['GGI_GITHUB_PROJECT']))
        print("- Using public GitHub instance.")

    params['GGI_ACTIVITIES_URL']= urllib.parse.urljoin(params['GGI_GITHUB_URL'] + '/', 'issues')
    params['GITHUB_ACTIVITIES_URL'] = params['GGI_GITHUB_URL'] + '/projects'

    print("Configuration:")
    print("URL     : " + params['GGI_GITHUB_URL'])
    print("Project : " + params['GGI_GITHUB_PROJECT'])
    print("Full URL: " + params['GGI_GITHUB_URL'])

    return params

def get_authent(params: dict):
    headers = {
        "Authorization": f"Bearer {params['GGI_GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.inertia-preview+json"  # Needed for project board access
    }

    # Connecting to the GitHub instance.
    # Manage authentication
    auth = Auth.Token(params['GGI_GITHUB_TOKEN'])
    if params['GGI_GITHUB_URL'].startswith(public_github_root_url):
        # Public Web GitHub
        print("- Using public GitHub instance.")
        github_handle = Github(auth=auth)
    else:
        print(f"- Using GitHub on-premise host {params['GGI_GITHUB_URL']} ")
        # GitHub Enterprise with custom hostname
        params['GGI_GITHUB_URL'] = f"{params['GGI_GITHUB_URL']}/api/v3"
        github_handle = Github(auth=auth, base_url=params['GGI_GITHUB_URL'])

    print(f"\n# Retrieving project from GitHub at {params['GGI_GITHUB_URL']}.")
    repo = github_handle.get_repo(params['GGI_GITHUB_PROJECT'])

    return repo, github_handle, headers

def main():
    """
    Test Utils lib
    """
    params = retrieve_params()
    print("- GGI_GITHUB_PROJECT: " + params['GGI_GITHUB_PROJECT'])
    print("- GGI_GITHUB_URL: " + params['GGI_GITHUB_URL'])
    print("- GGI_PAGES_URL: " + params['GGI_PAGES_URL'])

if __name__ == '__main__':
    main()
