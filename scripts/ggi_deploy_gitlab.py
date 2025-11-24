#!/usr/bin/python3
# ######################################################################
# Copyright (c) ...
# SPDX-License-Identifier: EPL-2.0
######################################################################

"""
Deploy script for GitLab — python-gitlab 7.x compatible refactor.
"""

import os
import random
import urllib.parse
import gitlab
from ggi_deploy import *
from ggi_utils_gitlab import retrieve_params


def main():
    """
    Main GitLab entrypoint.
    """
    args = parse_args()

    print("* Using GitLab backend.")
    metadata, init_scorecard = retrieve_env()
    params = retrieve_params()
    setup_gitlab(metadata, params, init_scorecard, args)

    print("\nDone.")


def create_gitlab_label(project, existing_labels, new_label, label_args):
    """
    Create label if it does not already exist.
    """
    if new_label in existing_labels:
        print(f" Ignore label: {new_label}")
        return

    print(f" Create label: {new_label}")
    project.labels.create(label_args)


def setup_gitlab(metadata, params: dict, init_scorecard, args: dict):
    """
    Execute the deployment on a GitLab instance (python-gitlab 7.x).
    """

    print(f"\n# Connection to GitLab at {params['GGI_GITLAB_URL']}")

    # python-gitlab 7.x enforces explicit parameters
    gl = gitlab.Gitlab(
        url=params['GGI_GITLAB_URL'],
        private_token=params['GGI_GITLAB_TOKEN'],
        per_page=50
    )

    # python-gitlab 7.x: .projects.get() unchanged
    project = gl.projects.get(params['GGI_GITLAB_PROJECT'])

    # ----------------------------------------------------------------------
    # Update project description
    # ----------------------------------------------------------------------
    if args.opt_projdesc:
        print("\n# Update Project description")

        if 'CI_PAGES_URL' not in os.environ:
            print("Cannot find environment variable 'CI_PAGES_URL', skipping.")
        else:
            ggi_activities_url = params['GGI_ACTIVITIES_URL']
            ggi_handbook_version = metadata['handbook_version']
            ggi_pages_url = params['GGI_PAGES_URL']

            desc = (
                'Your own Good Governance Initiative project.\n\n'
                'Here you will find '
                f'[**your dashboard**]({ggi_pages_url})\n'
                f'and the [**GitLab Board**]({ggi_activities_url}) with all activities describing the local GGI '
                f'deployment, based on version {ggi_handbook_version} of the [GGI handbook]('
                f'https://ospo-alliance.org/ggi/)\n\n'
                'For more information please see https://ospo-alliance.org/'
            )

            print(f"\nNew description:\n<<<---------\n{desc}\n--------->>>\n")

            project.description = desc
            project.save()

    # ----------------------------------------------------------------------
    # Labels and activities
    # ----------------------------------------------------------------------
    if args.opt_activities:

        print("\n# Manage labels")

        # python-gitlab 7.x: must specify all=True to list all labels
        existing_labels = [l.name for l in project.labels.list(all=True)]

        # Role labels
        print("\n Roles labels")
        for label, color in metadata['roles'].items():
            create_gitlab_label(
                project,
                existing_labels,
                label,
                {'name': label, 'color': color}
            )

        # Progress labels
        print("\n Progress labels")
        for name, label in params['progress_labels'].items():
            create_gitlab_label(
                project,
                existing_labels,
                label,
                {'name': label, 'color': '#ed9121'}
            )

        # Goal labels
        print("\n Goal labels")
        for goal in metadata['goals']:
            create_gitlab_label(
                project,
                existing_labels,
                goal['name'],
                {'name': goal['name'], 'color': goal['colour']}
            )

        # Create activities
        print("\n# Create activities.")
        issues_test = project.issues.list(state='opened', all=True)

        if len(issues_test) > 0:
            print(" Ignore, Issues already exist")
        else:
            for activity in metadata['activities']:

                progress_label = params['progress_labels']['not_started']

                if args.opt_random:
                    progress_idx = random.choice(
                        list(params['progress_labels']) + ['none']
                    )
                    if progress_idx != 'none':
                        progress_label = params['progress_labels'][progress_idx]

                labels = [activity['goal']] + activity['roles'] + [progress_label]

                print(f"  - Issue: {activity['name']:<60} Labels: {labels}")

                project.issues.create({
                    'title': activity['name'],
                    'description': extract_sections(args, init_scorecard, activity),
                    'labels': labels
                })

    # ----------------------------------------------------------------------
    # Create Goals Board
    # ----------------------------------------------------------------------
    if args.opt_board:
        print(f"\n# Create Goals board: {ggi_board_name}")

        # python-gitlab 7.x: list() needs all=True for full listing
        boards_list = project.boards.list(all=True)
        board_exists = any(b.name == ggi_board_name for b in boards_list)

        if board_exists:
            print(" Ignore, Board already exists")
        else:
            board = project.boards.create({'name': ggi_board_name})

            print('\n# Create Goals board lists.')

            # Build list of label objects for goals
            all_labels = project.labels.list(all=True)

            for g in metadata['goals']:
                for lbl in all_labels:
                    if lbl.name == g['name']:
                        print(f"  - Create list for {lbl.name}")
                        board.lists.create({'label_id': lbl.id})

    # ----------------------------------------------------------------------
    # Nightly pipeline schedule
    # ----------------------------------------------------------------------
    if args.opt_schedulepipeline:
        print("\n# Schedule nightly pipeline to refresh the Dashboard")

        schedules = project.pipelineschedules.list(all=True)

        if len(schedules) > 0:
            print(f" Ignore, already {len(schedules)} scheduled pipeline(s)")
        else:
            sched = project.pipelineschedules.create({
                'ref': 'main',
                'description': 'Nightly Update',
                'cron': '0 3 * * *'
            })
            print(f" Pipeline created: '{sched.description}'")


if __name__ == '__main__':
    main()