#!/usr/bin/python3
# ######################################################################
# Copyright (c) 2022 Boris Baldassari, Nico Toussaint and others
#
# This program and the accompanying materials are made available under the terms of the Eclipse Public License 2.0
# which is available at https://www.eclipse.org/legal/epl-2.0/
#
# SPDX-License-Identifier: EPL-2.0
######################################################################

"""
Deploy script for GitLab.
"""

import urllib.parse
import gitlab
from ggi_deploy import *
from ggi_utils_gitlab import retrieve_params

def main():
    """
    Main GITLAB.
    """
    args = parse_args()

    print("* Using GitLab backend.")
    metadata, init_scorecard = retrieve_env()
    params = retrieve_params()
    setup_gitlab(metadata, params, init_scorecard, args)

    print("\nDone.")

def create_gitlab_label(project, existing_labels, new_label, label_args):
    """
    Creates a set of labels in the GitLab project.
    """
    if new_label in existing_labels:
        print(f" Ignore label: {new_label}")
    else:
        print(f" Create label: {new_label}")
        project.labels.create(label_args)

def setup_gitlab(metadata, params: dict, init_scorecard, args: dict):
    """
    Executes the deployment on a GitLab instance.
    """

    print(f"\n# Connection to GitLab at {params['GGI_GITLAB_URL']} ")
    gl = gitlab.Gitlab(url=params['GGI_GITLAB_URL'], per_page=50, private_token=params['GGI_GITLAB_TOKEN'])
    project = gl.projects.get(params['GGI_GITLAB_PROJECT'])

    # Update current project description with Website URL
    if args.opt_projdesc:
        print("\n# Update Project description")
        if 'CI_PAGES_URL' in os.environ:
            ggi_activities_url = params['GGI_ACTIVITIES_URL']
            ggi_handbook_version = metadata['handbook_version']
            ggi_pages_url = params['GGI_PAGES_URL']
            desc = (
                'Your own Good Governance Initiative project.\n\n'
                'Here you will find '
                f'[**your dashboard**]({ggi_pages_url})\n'
                f'and the [**GitLab Board**]({ggi_activities_url}) with all activities describing the local GGI '
                f'deployment, based on the version {ggi_handbook_version} of the [GGI handbook]('
                f'https://ospo-alliance.org/ggi/)\n\n'
                'For more information please see the official project home page at https://ospo-alliance.org/'
            )
            print(f"\nNew description:\n<<<---------\n{desc}\n--------->>>\n")

            project.description = desc
            project.save()
        else:
            print("Cannot find environment variable 'CI_PAGES_URL', skipping.")

    # Create labels & activities
    if args.opt_activities:
        print("\n# Manage labels")
        existing_labels = [i.name for i in project.labels.list()]

        print("\n Roles labels")
        for label, colour in metadata['roles'].items():
            create_gitlab_label(project, existing_labels, label, {'name': label, 'color': colour})

        print("\n Progress labels")
        for name, label in params['progress_labels'].items():
            create_gitlab_label(project, existing_labels, label, {'name': label, 'color': '#ed9121'})

        print("\n Goal labels")
        for goal in metadata['goals']:
            create_gitlab_label(project, existing_labels, goal['name'], {'name': goal['name'], 'color': goal['colour']})

        print("\n# Create activities.")
        issues_test = project.issues.list(state='opened')
        if len(issues_test) > 0:
            print(" Ignore, Issues already exist")
        else:
            for activity in metadata['activities']:
                progress_label = params['progress_labels']['not_started']
                if args.opt_random:
                    progress_idx = random.choice(list(params['progress_labels']) + ['none'])
                    if progress_idx != 'none':
                        progress_label = params['progress_labels'][progress_idx]
                labels = [activity['goal']] + activity['roles'] + [progress_label]
                print(f"  - Issue: {activity['name']:<60} Labels: {labels}")
                ret = project.issues.create({'title': activity['name'],
                                             'description': extract_sections(args, init_scorecard, activity),
                                             'labels': labels})

    # Create Goals board
    if args.opt_board:
        print(f"\n# Create Goals board: {ggi_board_name}")
        boards_list = project.boards.list()
        board_exists = any(b.name == ggi_board_name for b in boards_list)
        if board_exists:
            print(" Ignore, Board already exists")
        else:
            board = project.boards.create({'name': ggi_board_name})
            print('\n# Create Goals board lists.')
            goal_lists = [l for g in metadata['goals'] for l in project.labels.list() if l.name == g['name']]
            for goal_label in goal_lists:
                print(f"  - Create list for {goal_label.name}")
                b_list = board.lists.create({'label_id': goal_label.id})

    # Schedule nightly pipeline
    if args.opt_schedulepipeline:
        print(f"\n# Schedule nightly pipeline to refresh the Dashboard")
        nb_pipelines = len(project.pipelineschedules.list())
        if nb_pipelines > 0:
            print(f" Ignore, already {nb_pipelines} scheduled pipeline(s)")
        else:
            sched = project.pipelineschedules.create({
                'ref': 'main',
                'description': 'Nightly Update',
                'cron': '0 3 * * *'})
            print(f" Pipeline created: '{sched.description}'")


if __name__ == '__main__':
    main()