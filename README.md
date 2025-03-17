This is the home of your own **Good Governance Initiative tracking board**.

# Introduction

This project helps implementing the [Good Governance Initiative (GGI)](https://ospo-alliance.org/ggi) framework.  
The GGI framework is a guide to effectively implement, step by step, an Open Source Program Office in your organisation. It proposes 25 activities organised in 5 distinct goals.


The goal is
- to fork the [my-ggi-board repository](https://gitlab.ow2.org/ggi/my-ggi-board) in your own GitLab/GitHub space.
- fill the configuration file - including a GitLab/GitHub token
- then run a script that will automatically create
  - appropriate labels
  - GitLab/GitHub Issues that will stand for the GGI activities
  - an Issues Board for a clear overview of you current activities (still work in progress for GitHub)
  - a static website to share progress and current work

# How it works

Currently the deployment is supported on the following platforms:
- [GitLab](https://gitlab.com)
- [GitHub](https://github.com)

## GitLab deployment

### Fork the repository
Multiple options here: 
- use the Import feature proposed by GitLab
- fork manually.

**GitLab Import Project**  
Probably simpler, but be aware that all branches will be duplicated to you own repo.

In your own GitLab space:
- Create a new project
- Choose: _Import project_
- Choose: _Repository by URL_
- Enter `https://gitlab.ow2.org/ggi/my-ggi-board.git`
- Adjust parameters (project url, slug and visibility level)
- Click: _Create project_

    <img src="resources/setup_import-project.png" width="50%" height="50%">


**Manually Fork**  
1. Create an empty project on your target GitLab instance.

    <img src="resources/setup_create-project.png" width="50%" height="50%">

1. Clone the [my-ggi-board repository](https://gitlab.ow2.org/ggi/my-ggi-board) to your new project.

To do so, clone the my-ggi-board repository locally, and add the new project's reference to the remotes:
```
$ git clone https://gitlab.ow2.org/ggi/my-ggi-board.git
$ git remote add my-ggi-board git@gitlab.com:<your-gitlab-space>/my-ggi-board.git
$ git push my-ggi-board
```

### Create your GitLab token

Two possibilities to create your [GitLab token](https://docs.gitlab.com/ee/security/tokens/index.html), depending on your GitLab environment: use a [Project access tokens](https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html#project-access-tokens) of a [Personal access tokens](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)

**Project access tokens**  
Create an access token (Project settings > Access Tokens) with the `api` privilege and with role `Maintainer`. Remember it, you will never see it again.

<img src="resources/setup_project-token.png" width="50%" height="50%">

**Personal access tokens**  
In case the instance admin has disabled the _project_ access token, you can use an _personal_ access token, although we recommend creating a dedicated account for security purposes in that case. Go to Preferences > Access Tokens and create the token from there.

<img src="resources/setup_personal-token.png" width="50%" height="50%">

### Setup the environment

1. Edit the file in `conf/ggi_deployment.json`, and set the variables `gitlab_url` (such as `https://gitlab.com`) and `gitlab_project` (such as `ggi/my-ggi-board-test`)
2. Commit and publish that file to your repository
3. (Optional) Export the access token as an environment variable: `export GGI_GITLAB_TOKEN=xxxxxxx`.
4. Enable CI/CD feature for the project : go to Settings > Visibility, project features, permissions > CI/CD and save changes
5. (Optional) Configure GitLab Pages feature for the project : go to Deploy > Pages, uncheck 'Use unique domain' and Save changes
6. Create a CI/CD env variable: go to Settings > CI/CD > Variables, then add a variable named `GGI_GITLAB_TOKEN` and set the access token as the value. Make it `Masked and hidden` (will not be shown in Jobs logs and revealed once set), `Protected` (cannot be used in non-protected branches) and non-expandable. 

    <img src="resources/setup_create-variable-1.png" width="50%" height="50%"> <img src="resources/setup_create-variable-2.png" width="50%" height="50%">

7. Run the pipeline: go to Build > Pipelines, click on the button 'New Pipeline' and then click on the button 'Run Pipeline'
8. Once the pipeline is over, you are done, your dashboard is ready !


## GitHub deployment

### Fork the repository

To deploy on GitHub, the simplest is to fork the [GitHub mirror repository](https://github.com/ospo-alliance/my-ggi-board) in your own space, using the [_Fork_ feature](https://github.com/ospo-alliance/my-ggi-board/fork).

<img src="resources/setup_fork-repo_github.png" width="50%" height="50%">

### Configure the project

1. Go to the repository _Settings_ > _General_ > _Features_ and enable 'Issues' and 'Projects'.
1. Edit the file in `conf/ggi_deployment.json`, and set the variables `github_url` (such as `https://github.com`) and `github_project` (such as `myuser/my-own-ggi-board`).

### Configure your GitHub token

1. Go to _User Settings_ > _Developer setting_ > _Personal access tokens_ > [_Tokens (classic)_](https://github.com/settings/tokens).
1. Click on 'Generate a new token' then 'Generate new token (classic)'
1. Name it 'my-ggi-board', choose an expiration and select scopes 'Repo' and 'Workflow'
1. Click on 'Generate token'

    <img src="resources/setup_personal-token_github.png" width="50%" height="50%">

1. Create a GitHub Actions env variable:
   - go to the repository _Settings_ > _Secrets and Variables_ > _Actions_
   - Click on `New repository secret`
   - Name the secret `GGI_GITHUB_TOKEN` and paste your newly created _access token_ below. Click on 'Add secret'.

    <img src="resources/setup_create-variable_github.png" width="50%" height="50%"> 

### Run the GitHub Action

1. Click on the Action menu entry
1. Make sure you agree with the text, click `I understant my workflows, go ahead and enable them`
1. Click on `My GGI Deploy deployment` to enable the workflow

    <img src="resources/setup_run-action_github_1.png" width="50%" height="50%"> 

1. Click on `Run workflow`

    <img src="resources/setup_run-action_github_2.png" width="50%" height="50%"> 

This will:
  - Create labels, activities and board.
  - Setup the static website configuration.
  - Replace the URL in the description.
  - Update the website's content.
  - Publish the result on GitHub pages.

    <img src="resources/setup_run-pipeline_github.png" width="50%" height="50%"> 

1. You can then create your issues board by creating a new 'Project' into your GitHub organisation, link the project to your repository and finally link the issues to it.