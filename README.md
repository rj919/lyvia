# Pocket Lab
_A Vital Service for a Brand New Project_
**by [Collective Acuity](https://collectiveacuity.com)**

Benefits
--------
- Endless fascination
-

Features
--------
- Responds to input
-

Requirements
------------
- Dependencies listed in Dockerfile
- Credentials from third-party services
-

Components
----------
- Alpine Edge (OS)
- Python 3.5.2 (Environment)
-

Dev Environment
---------------
- Docker (Provisioning)
- BitBucket (Version Control)
- PyCharm (IDE)
- Dropbox (Sync, Backup)
- PocketLab (DevOps)

Languages
---------
- Python 3.5

Collaboration Notes
-------------------
The Git and Docker repos contain all the configuration information required for collaboration except access tokens. To synchronize access tokens across multiple devices, platforms and users without losing local control, you can use LastPass, an encrypted email platform such as ProtonMail or smoke signals. If you use any AWS services, use AWS IAM to assign user permissions and create keys for each collaborator individually.
Collaborators are required to install all service dependencies on their local device if they wish to test code on their localhost. A collaborate should always **FORK** the repo from the main master and fetch changes from the upstream repo so reality is controlled by one admin responsible for approving all changes. New dependencies should be added to the Dockerfile, **NOT** to the repo files. Collaborators should test changes to Dockerfile locally before making a pull request to merge any new dependencies:

```bash
docker build -t test-image .
```

.gitignore and .dockerignore have already been installed with the standard exclusions. To prevent unintended file proliferation through version control & provisioning, add/edit .gitignore and .dockerignore to include all new:

1. local environments folders
2. localhost dependencies
3. configuration files with credentials and local variables