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

# This script:
# - downloads the Activities Metadata JSON file from the GGI repository
# - saves additional file source information
# - dumps the resulting JSON file in the local filesystem, 
#   so it can be manually committed to the my-gg-board repository.

# usage: ggi_deploy [-h] [-r]
#
# optional arguments:
#   -h, --help        Show this help message and exit
#   -r, --refefence   Target branch or tag
#

import argparse
import copy
import datetime
import json
import os
import requests 
import tarfile
import tempfile

local_conf_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/conf'
local_activities_file_path = local_conf_dir + '/ggi_activities_full.json'

remote_git_url='https://gitlab.ow2.org'
remote_git_project='ggi/ggi'
remote_git_reference='dev'

tmp_gz_dir = tempfile.TemporaryDirectory()
tmp_gz_filename=tmp_gz_dir.name+'/ggi_content.tar.bz2'
tmp_gz_filename='/tmp/ggi_content.tar.bz2'

#
# Parse arguments from command line.
#

parser = argparse.ArgumentParser(prog='ggi_deploy')
parser.add_argument('-r', '--reference',
    dest='target_git_ref',
    action='store',
    default=remote_git_reference,
    help='Specify target branch or tag')
args = parser.parse_args()

# Build download URL
# https://gitlab.ow2.org/ggi/ggi/-/archive/main/ggi-main.tar.bz2?path=handbook/content
remote_git_contents_url = \
    remote_git_url + '/' + \
    remote_git_project + '/-/archive/' + \
    args.target_git_ref + '/ggi-' + \
    args.target_git_ref + '.tar.bz2?path=handbook/content'

print(f"\n# Download Activities from remote repository")
print(f"# URL: {remote_git_contents_url}")
resp = requests.get(remote_git_contents_url)
if (resp.status_code != 200):
    print("Status code: " + resp.status_code)

# And store content as a gz file in a temporary folder
with open(tmp_gz_filename, 'wb') as fd:
    for chunk in resp.iter_content(chunk_size=128):
        fd.write(chunk)

activities = []
print("\n# Build activities")
tf = tarfile.open(tmp_gz_filename, 'r:bz2')
tf_main_folder=tf.next()
tmp_gz_dir.cleanup() # Delete temporary folder and file

# Load Metadata file
activities_content = json.load(tf.extractfile(
          tf_main_folder.name
          + '/handbook/content/' 
          + 'ggi_activities_metadata.json'))
# Add actual Activities description
for activity in activities_content['activities']:
    print(f"  - Building activity [{activity['id']}]..")
    content = tf.extractfile(
          tf_main_folder.name
          + '/handbook/content/' 
          + activity['path']
      ).readlines()
    activity['content'] = "".join( [ i.decode() for i in content ] )
    activities.append(activity)

# Add activities reference metadata
activities_content.update({"source": {}})
metadata_source = activities_content.get("source")
metadata_source.update({"git-remote" : remote_git_url})
metadata_source.update({"git-project" : remote_git_project})
metadata_source.update({"git-reference" : args.target_git_ref})
metadata_source.update({"download-timestamp" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
print(f"# Additional source information:\n" + json.dumps(metadata_source, indent=True) + "\n")

# Save file locally
print(f"# Save file in locally: {local_activities_file_path}")
with open(local_activities_file_path, 'w') as out_file:
    json.dump(activities_content, out_file, indent=2)
