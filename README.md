This is the home of your own **Good Governance Initiative tracking board**.

# Introduction

The _My GGI Board_ project helps implementing the [Good Governance Initiative (GGI)](https://ospo-alliance.org/ggi) framework.  
The GGI framework is a guide to effectively implement, step by step, an Open Source Program Office in your organisation. It proposes 25 activities organised in 5 distinct goals.

This document below is a simple guide to deploy _My GGI Board_ on [GitLab](https://gitlab.com) (see [here](#gitlab-deployment)) or [GitHub](https://github.com) (see [here](#github-deployment)) platforms within a few minutes.  
You will find more advanced guidelines to fork and deploy manually in the dedicated pages for [GitLab](docs/gitlab-advanced.md) and [GitHub](docs/github-advanced.md).


The main steps are:
- Fork the [my-ggi-board repository](https://gitlab.ow2.org/ggi/my-ggi-board) in your own GitLab/GitHub space.
- Create an authentication token and configure an environment variable for the token
- A pipeline will automatically create
  - Appropriate labels
  - Issues that will stand for the GGI activities
  - An Issues Board for a clear overview of you current activities (still work in progress for GitHub)
  - A static website to share progress and current work

Currently the deployment is supported and documented on the following platforms:
- [GitLab](#gitlab-deployment)
- [GitHub](#github-deployment)

## Fork the repository

In your own GitLab space:
- Create a new project
- Choose: _Import project_
- Choose: _Repository by URL_
- Enter `https://gitlab.ow2.org/ggi/my-ggi-board.git`
- Adjust parameters (project url, slug and visibility level)
- Click: _Create project_

    <img src="resources/setup_import-project.png" width="50%" height="50%">

## Create your GitLab token

Two possibilities to create your [GitLab token](https://docs.gitlab.com/ee/security/tokens/index.html), depending on your GitLab environment: use a [Project access tokens](https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html#project-access-tokens) of a [Personal access tokens](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)

**Project access tokens**  
Create an access token (Project settings > Access Tokens) with the `api` privilege and with role `Maintainer`. Remember it, you will never see it again.

<img src="resources/setup_project-token.png" width="50%" height="50%">

**Personal access tokens**  
In case the instance admin has disabled the _project_ access token, you can use an _personal_ access token, although we recommend creating a dedicated account for security purposes in that case. Go to Preferences > Access Tokens and create the token from there.

<img src="resources/setup_personal-token.png" width="50%" height="50%">

## Setup the environment

The pipeline might have already been executed and failed, since the token is not configured yet.

1. Enable CI/CD feature for the project : go to Settings > Visibility, project features, permissions > CI/CD and save changes
1. (Optional) Configure GitLab Pages feature for the project : go to Deploy > Pages, uncheck 'Use unique domain' and Save changes
1. Create a CI/CD env variable: go to Settings > CI/CD > Variables, then add a variable named `GGI_GITLAB_TOKEN` and set the access token as the value. Make it `Masked and hidden` (will not be shown in Jobs logs and revealed once set), `Protected` (cannot be used in non-protected branches) and non-expandable. 

    <img src="resources/setup_create-variable-1.png" width="50%" height="50%"> <img src="resources/setup_create-variable-2.png" width="50%" height="50%">

1. Run the pipeline manually: go to Build > Pipelines, click on the button 'New Pipeline' and then click on the button 'Run Pipeline'
1. Once the pipeline is over, you are done, your dashboard is ready !

# GitHub deployment

## Fork the repository

The easiest way to deploy on GitHub is to fork the [GitHub mirror repository](https://github.com/ospo-alliance/my-ggi-board) in your own space, using the [_Fork_ feature](https://github.com/ospo-alliance/my-ggi-board/fork).

<img src="resources/setup_fork-repo_github.png" width="50%" height="50%">

## Configure the project

1. Go to the repository _Settings_ > _General_ > _Features_ and enable 'Issues' and 'Projects'.

## Configure your GitHub token

1. Go to _User Settings_ > _Developer setting_ > _Personal access tokens_ > [_Tokens (classic)_](https://github.com/settings/tokens).
1. Click on 'Generate a new token' then 'Generate new token (classic)'
1. Name it 'my-ggi-board', choose an expiration date and select scopes 'Repo' and 'Workflow'
1. Click on 'Generate token'

    <img src="resources/setup_personal-token_github.png" width="50%" height="50%">

1. Create a GitHub Actions env variable:
   - Go to the repository _Settings_ > _Secrets and Variables_ > _Actions_
   - Click on `New repository secret`
   - Name the secret `GGI_GITHUB_TOKEN` and paste your newly created _access token_ below. Click on 'Add secret'.

    <img src="resources/setup_create-variable_github.png" width="50%" height="50%"> 

## Run the GitHub Action

The action might have already been executed and failed, since the token was not configured yet.

1. Click on the Action menu entry
1. Make sure you agree with the text, click `I understant my workflows, go ahead and enable them`
1. Click on `My GGI Deploy deployment` to enable the workflow

    <img src="resources/setup_run-action_github_1.png" width="50%" height="50%"> 

1. Click on `Run workflow`

    <img src="resources/setup_run-action_github_2.png" width="50%" height="50%"> 

1. You can then create your issues board by creating a new 'Project' into your GitHub organisation, link the project to your repository and finally link the issues to it.
