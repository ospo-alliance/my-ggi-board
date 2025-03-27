#!/usr/bin/python3
# ######################################################################
# Copyright (c) 2022 Boris Baldassari, Nico Toussaint and others
#
# This program and the accompanying materials are made
# available under the terms of the Eclipse Public License 2.0
# which is available at https://www.eclipse.org/legal/epl-2.0/
#
# SPDX-License-Identifier: EPL-2.0
######################################################################

"""
This script:
- reads the metadata defined in the `conf` directory,
- connects to the GitLab/GitHub instance as configured in the ggi_deployment.json file
- optionally creates the activities on a new (empty) gitlab project,
- optionally creates a board and its lists to display activities.

The script expects your GitLab private key in the environment variable: GGI_GITLAB_TOKEN
You may also set an environment variable 'GGI_DEMO_MODE' to 'true' to activate the demo mode.

usage: ggi_deploy [-h] [-a] [-b] [-d] [-p]

optional arguments:
  -h, --help                  Show this help message and exit
  -a, --activities            Create activities
  -r, --random-demo           Random Scorecard objectives and Activities status, for demo purposes
  -b, --board                 Create board
  -d, --project-description   Update Project Description with pointers to the Board and Dashboard
  -p, --schedule-pipeline     Schedule nightly pipeline to update dashboard
"""
import argparse
import json
import os
import random
import re
from collections import OrderedDict

# Define some variables.
conf_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/conf'
activities_file = conf_dir + '/ggi_activities_full.json'
conf_file = conf_dir + '/ggi_deployment.json'
init_scorecard_file = conf_dir + '/workflow_init.inc'


# Define some regexps
re_section = re.compile(r"^### (?P<section>.*?)\s*$")

ggi_board_name = 'GGI Activities/Goals'

#comment

def parse_args():
    """
    Parse arguments from command line.
    """
    desc = "Deploys an instance of the GGI Board on a GitLab/GitHub instance."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-a', '--activities',
                        dest='opt_activities',
                        action='store_true',
                        help='Create activities')
    parser.add_argument('-b', '--board',
                        dest='opt_board',
                        action='store_true',
                        help='Create board')
    parser.add_argument('-d', '--project-description',
                        dest='opt_projdesc',
                        action='store_true',
                        help='Update Project description')
    parser.add_argument('-p', '--schedule-pipeline',
                        dest='opt_schedulepipeline',
                        action='store_true',
                        help='Schedule nightly pipeline to update dashboard')
    parser.add_argument('-r', '--random-demo',
                        dest='opt_random',
                        action='store_true',
                        help='Random Scorecard objectives and Activities status, for demo purposes')
    args = parser.parse_args()

    if 'GGI_DEMO_MODE' in os.environ:
        if os.environ['GGI_DEMO_MODE'].lower() == 'true':
            opt_random = True

    return args


def retrieve_env():
    """
    Read metadata for activities and deployment options.

    """

    print(f"\n# Reading metadata from {activities_file}")
    with open(activities_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # Read the custom scorecard init file.
    print(f"# Reading scorecard init file from {init_scorecard_file}.")
    with open(init_scorecard_file, 'r', encoding='utf-8') as f:
        init_scorecard = f.readlines()

    return metadata, init_scorecard


def get_scorecard(opt_random, init_scorecard):
    """
    Build a scorecard with a random number of objectives,
    randomly checked, if required by user.
    Otherwise, simply return the untouched scorecard text
    """

    if opt_random:
        # Create between 4 and 10 objectives per Scorecard
        num_lines = random.randint(4, 10)
        objectives_list = []
        for idx in range(num_lines):
            objectives = "- [ ] objective " + str(idx) + " \n"
            # aim at 25% of objectives done
            if random.randint(1, 4) == 1:
                objectives = objectives.replace("[ ]", "[x]")
            objectives_list.append(objectives)
        return ''.join(init_scorecard).replace("What we aim to achieve in this iteration.", ''.join(objectives_list))
    else:
        return init_scorecard


def extract_sections(args, init_scorecard, activity):
    """
    Extracts the scorecard from the "Introduction" section in the
    description field of an issue.
    """
    paragraphs = activity['content'].split('\n\n')
    content_t = 'Introduction'
    content = OrderedDict()
    content = {content_t: []}
    for p in paragraphs:
        match_section = re.search(re_section, p)
        if match_section:
            content_t = match_section.group('section')
            content[content_t] = []
        else:
            content[content_t].append(p)
    # Add Activity ID
    content_text = content['Introduction'][1] + '\n\n'
    # Add Scorecard
    content_text += ''.join(get_scorecard(args.opt_random, init_scorecard))
    del content['Introduction']
    # Add description content.
    for key in content.keys():
        content_text += f"\n\n### {key}\n\n"
        content_text += '\n\n'.join(content[key])
    return content_text

