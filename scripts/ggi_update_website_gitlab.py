#!/usr/bin/python3
# ######################################################################
# Copyright (c) 2022 Boris Baldassari, Nico Toussaint and others
#
# SPDX-License-Identifier: EPL-2.0
######################################################################

"""
Update static website from GitLab metadata.
"""

import glob
import json
import os
from datetime import date

import gitlab
import pandas as pd

from ggi_update_website import *
from ggi_utils_gitlab import retrieve_params


def retrieve_gitlab_issues(params: dict):
    """
    Retrieve issues from GitLab instance.
    """
    print(f"\n# Connection to GitLab at {params['GGI_GITLAB_URL']} - {params['GGI_GITLAB_PROJECT']}.")
    gl = gitlab.Gitlab(url=params['GGI_GITLAB_URL'], per_page=50, private_token=params['GGI_GITLAB_TOKEN'])
    project = gl.projects.get(params['GGI_GITLAB_PROJECT'])

    print("# Fetching issues..")
    gl_issues = project.issues.list(state='opened', all=True)
    print(f"  Found {len(gl_issues)} issues.")

    issues, tasks, hist = [], [], []

    for i in gl_issues:
        desc = i.description
        a_id, description, workflow, a_tasks = extract_workflow(desc)
        for t in a_tasks:
            tasks.append([a_id, 'completed' if t['is_completed'] else 'open', t['task']])
        short_desc = '\n'.join(description)
        tasks_total = len(a_tasks)
        tasks_done = len([t for t in a_tasks if t['is_completed']])
        issues.append([i.iid, a_id, i.state, i.title, ','.join(i.labels),
                       i.updated_at, i.web_url, short_desc, workflow,
                       tasks_total, tasks_done])

        for n in i.resourcelabelevents.list():
            event = i.resourcelabelevents.get(n.id)
            label = n.label['name'] if n.label else ''
            user = n.user['username'] if n.user else 'unknown'
            hist.append([n.created_at, i.iid, n.id, 'label', user,
                         f"{n.action} {label}", i.web_url])

    return issues, tasks, hist


def main():
    args = parse_args()
    params = retrieve_params()

    issues, tasks, hist = retrieve_gitlab_issues(params)

    issues_df = pd.DataFrame(issues, columns=['issue_id', 'activity_id', 'state', 'title', 'labels',
                                              'updated_at', 'url', 'desc', 'workflow', 'tasks_total', 'tasks_done'])
    tasks_df = pd.DataFrame(tasks, columns=['issue_id', 'state', 'task'])
    hist_df = pd.DataFrame(hist, columns=['time', 'issue_id', 'event_id', 'type', 'author', 'action', 'url'])

    write_to_csv(issues_df, tasks_df, hist_df)
    write_activities_to_md(issues_df)
    write_data_points(issues_df, params)

    print("\n# Replacing keywords in static website.")
    keywords = {
        '[GGI_URL]': params['GGI_URL'],
        '[GGI_PAGES_URL]': params['GGI_PAGES_URL'],
        '[GGI_ACTIVITIES_URL]': params['GGI_ACTIVITIES_URL'],
        '[GGI_CURRENT_DATE]': str(date.today())
    }

    update_keywords('web/config.toml', keywords)
    update_keywords('web/content/includes/initialisation.inc', keywords)
    update_keywords('web/content/scorecards/_index.md', keywords)
    files = glob.glob("web/content/*.md")
    for file in files:
        if os.path.isfile(file):
            update_keywords(file, keywords)

    print("Done.")


if __name__ == '__main__':
    main()