# Advanced GitLab deployment

Alternatively to the straight forward deployement (see the [README file](README.md#gitlab-deployment)), you may want to fork and execute the scripts locally.

## Manually fork the repository

1. Create an empty project on your target GitLab instance.

    <img src="resources/setup_create-project.png" width="50%" height="50%">

1. Clone the [my-ggi-board repository](https://gitlab.ow2.org/ggi/my-ggi-board) to your new project.

To do so, clone the my-ggi-board repository locally, and add the new project's reference to the remotes:
```
$ git clone https://gitlab.ow2.org/ggi/my-ggi-board.git
$ git remote add my-ggi-board git@gitlab.com:<your-gitlab-space>/my-ggi-board.git
$ git push my-ggi-board
```

## Setup the environment

1. Edit the file in `conf/ggi_deployment.json`, and set the variables `gitlab_url` (such as `https://gitlab.com`) and `gitlab_project` (such as `ggi/my-ggi-board-test`)
1. Commit and publish that file to your repository
1. Export the access token as an environment variable: `export GGI_GITLAB_TOKEN=xxxxxxx`.
1. Enable CI/CD feature for the project : go to Settings > Visibility, project features, permissions > CI/CD and save changes
1. Configure GitLab Pages feature for the project : go to Deploy > Pages, uncheck 'Use unique domain' and Save changes
1. Create a CI/CD env variable: go to Settings > CI/CD > Variables, then add a variable named `GGI_GITLAB_TOKEN` and set the access token as the value. Make it `Masked and hidden` (will not be shown in Jobs logs and revealed once set), `Protected` (cannot be used in non-protected branches) and non-expandable. 

    <img src="resources/setup_create-variable-1.png" width="50%" height="50%"> <img src="resources/setup_create-variable-2.png" width="50%" height="50%">

1. Clone your repository locally
1. Create a virtual env and install requirements.

    ```
    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```
1. Run the deploy script: `python scripts/ggi_deploy_gitlab.py -a -b -d -p`. That will:
  - Create labels, activities, board.
  - Setup the static website configuration (GitLab Pages)
  - Replace the URL in the README.

10. Commit your changes: `git commit -m 'initial commit' -a`
1. Push to the local gitlab instance on the `main` branch: `git push my-ggi`. That will:
  - Create a pipeline and gitlab page thanks to the `.gitlab_ci.yml` file.
  - Execute the ggi_update_website script, updating the website's content.
  - Publish the gitlab page.