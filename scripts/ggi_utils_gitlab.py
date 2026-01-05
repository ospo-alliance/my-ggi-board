#!/usr/bin/python3
# ######################################################################
# Copyright (c) 2025 The OSPO Alliance contributors
#
# This program and the accompanying materials are made available
# under the terms of the Eclipse Public License 2.0
# which is available at https://www.eclipse.org/legal/epl-2.0/
#
# SPDX-License-Identifier: EPL-2.0
######################################################################

"""
GitLab utilities for GGI tools.
"""

import json
import os
import urllib.parse
import tldextract

from ggi_deploy import *

def retrieve_params():
    """
    Read metadata for activities and deployment options.

    Determine GitLab server URL and Project name:
    * From environment variables if available, or
    * From configuration file otherwise.
    """

    print(f"# Reading deployment options from {conf_file}.")
    with open(conf_file, 'r', encoding='utf-8') as f:
        params = json.load(f)

    # GitLab URL
    if 'CI_SERVER_URL' in os.environ:
        params['GGI_GITLAB_URL'] = os.environ['CI_SERVER_URL']
        print("- Using GitLab URL from env var 'CI_SERVER_URL'")
    elif 'GGI_GITLAB_URL' in os.environ and params['gitlab_project'] is not None:
        params['GGI_GITLAB_URL'] = os.environ['GGI_GITLAB_URL']
        print("- Using GitLab URL from env var 'GGI_GITLAB_URL'")
    elif 'gitlab_url' in params and params['gitlab_url'] is not None:
        params['GGI_GITLAB_URL'] = params['gitlab_url']
        print("- Using GitLab URL from configuration file")
        print(params['GGI_GITLAB_URL'] )
    else:
        print("Cannot find GitLab URL. Exiting.")
        exit(1)

    # GitLab Project
    if 'CI_PROJECT_PATH' in os.environ:
        params['GGI_GITLAB_PROJECT'] = os.environ['CI_PROJECT_PATH']
        print("- Using Project from env var 'CI_PROJECT_PATH'")
    elif 'GGI_GITLAB_PROJECT' in os.environ:
        params['GGI_GITLAB_PROJECT'] = os.environ['GGI_GITLAB_PROJECT']
        print("- Using Project from env var 'GGI_GITLAB_PROJECT'")
    elif 'gitlab_project' in params:
        params['GGI_GITLAB_PROJECT'] = params['gitlab_project']
        print("- Using Project from configuration file")
    else:
        print("Cannot find GitLab project (org/repo). Exiting.")
        exit(1)

    # GitLab Token
    if 'GGI_GITLAB_TOKEN' in os.environ:
        params['GGI_GITLAB_TOKEN'] = os.environ['GGI_GITLAB_TOKEN']
        print("- Using token from env var 'GGI_GITLAB_TOKEN'")
    else:
        print("Cannot find env var 'GGI_GITLAB_TOKEN'. Exiting.")
        exit(1)

    # Pages URL
    if 'CI_PAGES_URL' in os.environ:
        params['GGI_PAGES_URL'] = os.environ['CI_PAGES_URL']
        print("- Using Pages URL from env var 'CI_PAGES_URL'")
    else:
        print("- Pages URL not found in env. Computing fallback.")
        pieces = tldextract.extract(params['GGI_GITLAB_URL'])
        params['GGI_PAGES_URL'] = 'https://' + params['GGI_GITLAB_PROJECT'].split('/')[0] +                                   '.' + pieces.domain + '.io/' + params['GGI_GITLAB_PROJECT'].split('/')[-1]

    # Compose URLs
    params['GGI_URL'] = urllib.parse.urljoin(params['GGI_GITLAB_URL'], params['GGI_GITLAB_PROJECT'])
    params['GGI_ACTIVITIES_URL'] = os.path.join(params['GGI_URL'] + '/', '-/boards')

    print("Configuration:")
    print("URL     : " + params['GGI_GITLAB_URL'])
    print("Project : " + params['GGI_GITLAB_PROJECT'])
    print("Full URL: " + params['GGI_URL'])

    return params


def main():
    """
    Test GitLab utils.
    """
    params = retrieve_params()
    print("- GGI_GITLAB_PROJECT: " + params['GGI_GITLAB_PROJECT'])
    print("- GGI_GITLAB_URL: " + params['GGI_GITLAB_URL'])
    print("- GGI_PAGES_URL: " + params['GGI_PAGES_URL'])

if __name__ == '__main__':
    main()