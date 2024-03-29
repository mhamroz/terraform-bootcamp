# LAB 3 - Build CICD pipeline with Terraform

## Lab Overview

In this lab we'll dive into using GitLab's helpful CI/CD pipeline to manage your Terraform setups for Cisco Catalyst 9000 Series Switches with BGP EVPN VXLAN configuration. Building on what you've learned about Terraform and Cisco devices in [lab2](../lab2/README.md), this lab is all about smoothly putting GitLab's CI/CD tools to work, and integrating Terraform with GitLab CI.

<br>


## Pre-requisites

- Use an IDE of your choice. This tutorial will assume Visual Studio Code

- Git installed

- Docker installed

- Access to Catalyst 9000 series switches (2x Leafs, 1xSpine)

- Access to the internet

- Basic understanding of Terraform

## Time Estimates

60 minutes

<br></br>

## 1. Install GITLAB with Docker

Open terminal and pull gitlab-ce image from DockerHub:

`docker pull gitlab/gitlab-ce:latest`

```
C:\Users\Administrator\Desktop>docker pull gitlab/gitlab-ce:latest
```

Image will take 2-3 mins to download. Once downloaded, check if image was downloaded successfuly using `docker images` command:

```
C:\Users\Administrator\Desktop>docker images
REPOSITORY               TAG       IMAGE ID       CREATED         SIZE
gitlab/gitlab-ce         latest    c5dc32379073   4 days ago      3.01GB
yangsuite-dcloud         latest    f8cbf8617700   7 months ago    3.46GB
yangsuite                latest    79745a8cf9fd   11 months ago   2.58GB
tig_mdt                  latest    4922aa6e492d   12 months ago   4.32GB
portainer/portainer-ce   2.9.3     ad0ecf974589   21 months ago   252MB
```

<br>

## 2. Configure and Run Gitlab

To run Gitlab container you need to provide a few options at runtime:

```
docker run -d --hostname 198.18.133.252 -p 443:443 -p 80:80 -p 22:22 --name gitlab-linode --restart always  gitlab/gitlab-ce:latest
```

`-d` runs docker container in background

`--hostname` defines the container's internal hostname (use ip address of your workstation)

`-p` publish container's port(s) to the host

`--name` assign a name to the container

`--restart` restart policy to apply when a container exits


To check ip address of workstation use `ipconfig` command:

```
C:\Users\Administrator\Desktop>ipconfig

Windows IP Configuration


Ethernet adapter Ethernet0:

   Connection-specific DNS Suffix  . : demo.dcloud.cisco.com
   IPv4 Address. . . . . . . . . . . : 198.18.133.252
   Subnet Mask . . . . . . . . . . . : 255.255.192.0
   Default Gateway . . . . . . . . . : 198.18.128.1
```

Then run docker container use following command (replacing ip address with IP address of workstation):

```
C:\Users\Administrator\Desktop>docker run -d --hostname 198.18.133.252 -p 443:443 -p 80:80 -p 22:22 --name gitlab-linode --restart always  gitlab/gitlab-ce:latest
e692f708e88e7c0fb3d8e528dea5d2aabd95f6932e075abfc83cf6e1bd815675
```
Container may take couple minutes to start.
To find out more information about startup process inspect logs:

`docker logs -f gitlab-linode`

To exit from log monitoring process enter CTRL+C.

Open webbrowser and navigate to IP address you specified in --hostname option during container startup:

`http://198.18.133.252`

If you see HTTP error 502 try waiting few more minutes and refresh page.

First time you access Gitlab site you will be propmed to setup root password. Enter complex password and save it.

If you are not asked to set up a root password, follow this workaround:

1. Enter Gitlab-CE container shell: `docker exec -it gitlab-linode /bin/bash`
2. Run following command to setup new root password (minimum 8 characters): 
```
gitlab-rake "gitlab:password:reset[root]"
```

```
root@198:/# gitlab-rake "gitlab:password:reset[root]"
Enter password:
Confirm password:
Password successfully updated for user with username root.
```
3. Exit from shell container by typing `exit`

```
root@198:/# exit
exit

C:\Users\Administrator\Desktop>
```
4. Now you can login to Gitlab with your new password and root login.


![gitlab_1](images/gitlab_1.png)

<br>

## 3. Install and register Gitlab runner 

GitLab Runner is an open-source application that is used in conjunction with GitLab CI/CD (Continuous Integration/Continuous Deployment) pipelines. It's designed to run jobs and tasks as part of your CI/CD pipeline.

To start gitlab runner container use following command:

```
docker run -d --name gitlab-runner --restart always gitlab/gitlab-runner:latest
```

```
C:\Users\Administrator\Desktop>docker run -d --name gitlab-runner --restart always gitlab/gitlab-runner:latest
Unable to find image 'gitlab/gitlab-runner:latest' locally
latest: Pulling from gitlab/gitlab-runner
edaedc954fb5: Pull complete
8c3aebe7713f: Pull complete
5b1147e4eba7: Pull complete
Digest: sha256:9cabe88ca172e44ea41603aaf43cd7985fac76d46c6dac2d9c4e5899ba7a2be1
Status: Downloaded newer image for gitlab/gitlab-runner:latest
e0303ca291b233016529828448f9fc282dd03c7d7e0bd21d973a1b6ba6fcec16
```

Check if Gitlab runner is running:

```
C:\Users\Administrator\Desktop>docker ps
CONTAINER ID   IMAGE                          COMMAND                  CREATED              STATUS                       PORTS                                                                    NAMES
e0303ca291b2   gitlab/gitlab-runner:latest    "/usr/bin/dumb-init …"   About a minute ago   Up About a minute                                                                                     gitlab-runner
e692f708e88e   gitlab/gitlab-ce:latest        "/assets/wrapper"        About an hour ago    Up About an hour (healthy)   0.0.0.0:22->22/tcp, 0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp             gitlab-linode
f0d13245a4d0   yangsuite-dcloud:latest        "/start"                 7 months ago         Up Less than a second        0.0.0.0:8480->8480/tcp, 0.0.0.0:58500-58501->58500-58501/tcp             yangsuite
0615e3d8832a   tig_mdt:latest                 "/start.sh"              12 months ago        Up Less than a second        0.0.0.0:3000->3000/tcp, 0.0.0.0:57500-57501->57500-57501/tcp, 5201/tcp   tig_mdt
d7cc1df5338f   portainer/portainer-ce:2.9.3   "/portainer"             12 months ago        Up Less than a second        0.0.0.0:8000->8000/tcp, 0.0.0.0:9443->9443/tcp, 9000/tcp                 portainer
```

After you start your gitlab runner you need to register this runner to run jobs using following steps:

1. Navigate to Gitlab website: `http://198.18.133.252`

2. Click <b>Configure GitLab</b>

![gitlab_3](images/gitlab_3.png)

3. Go to <b>CI/CD -> Runners</b>

![gitlab_4](images/gitlab_4.png)

4. Click <b>New instance runner</b>

5. Create new runner with following options:

- Platform: Linux
- Enable option: <b>Run untagged jobs</b>

![gitlab_5](images/gitlab_5.png)

6. Click <b>Create runner</b> button

7. To register gitlab runner copy command from Step 1 from gitlab website:

![gitlab_6](images/gitlab_6.png)

8. Enter gitlab-runner container shell: `docker exec -it gitlab-runner /bin/bash`

9. Paste and run command copied in step 7:

`gitlab-runner register  --url http://198.18.133.252  --token glrt-ywdjYxddYVTEbR-wGKdb`

`Note` Use token from step 7.

- keep GitLab URL and name for the runner as defaults [] by hittng ENTER
- choose the shell executor

```
root@e0303ca291b2:/# gitlab-runner register  --url http://198.18.133.252  --token glrt-ywdjYxddYVTEbR-wGKdb
Runtime platform                                    arch=amd64 os=linux pid=42 revision=674e0e29 version=16.2.1
Running in system-mode.

Enter the GitLab instance URL (for example, https://gitlab.com/):
[http://198.18.133.252]:
Verifying runner... is valid                        runner=ywdjYxddY
Enter a name for the runner. This is stored only in the local config.toml file:
[e0303ca291b2]:
Enter an executor: kubernetes, docker, shell, parallels, ssh, virtualbox, docker-autoscaler, docker+machine, instance, custom, docker-windows:
shell
Runner registered successfully. Feel free to start it, but if it's running already the config should be automatically reloaded!

Configuration (with the authentication token) was saved in "/etc/gitlab-runner/config.toml"
root@e0303ca291b2:/#
```

11. To view runner, go to <b>Admin Area > Runners</b>

![gitlab_7](images/gitlab_7.png)

12. Verify that status of runner is Online:

![gitlab_8](images/gitlab_8.png)

If you see green circle next to your runner, it means that you have a runner available to proces your jobs and you can create your first project!

<br>

## 4. Install Terraform and other dependencies on Gitlab runner

To install terraform on Gitlab runner enter gitlab-runner container shell: `docker exec -it gitlab-runner /bin/bash` and paste following commands:


```
apt update && apt install lsb-release gpg

wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list

apt update && apt install terraform
```

Verify that terraform was installed succesfully:

```
root@e0303ca291b2:/# terraform --version
Terraform v1.5.6
on linux_amd64
```

Next, install python3-pip:

`apt install python3-pip`

```bash
root@e0303ca291b2:/# apt install python3-pip
Reading package lists... Done
Building dependency tree
Reading state information... Done
The following additional packages will be installed:
  binutils binutils-common binutils-x86-64-linux-gnu build-essential cpp cpp-9 dpkg-dev fakeroot g++ g++-9 gcc gcc-9
  gcc-9-base libalgorithm-diff-perl libalgorithm-diff-xs-perl libalgorithm-merge-perl libasan5 libatomic1 libbinutils
  libc-dev-bin libc6-dev libcc1-0 libcrypt-dev libctf-nobfd0 libctf0 libdpkg-perl libexpat1-dev libfakeroot
  libfile-fcntllock-perl libgcc-9-dev libgomp1 libisl22 libitm1 liblocale-gettext-perl liblsan0 libmpc3 libmpfr6
  libpython3-dev libpython3.8 libpython3.8-dev libquadmath0 libstdc++-9-dev libtsan0 libubsan1 linux-libc-dev make
  manpages manpages-dev patch python-pip-whl python3-dev python3-distutils python3-lib2to3 python3-pkg-resources
  python3-setuptools python3-wheel python3.8-dev zlib1g-dev
Suggested packages:
  binutils-doc cpp-doc gcc-9-locales debian-keyring g++-multilib g++-9-multilib gcc-9-doc gcc-multilib autoconf
  automake libtool flex bison gdb gcc-doc gcc-9-multilib glibc-doc bzr libstdc++-9-doc make-doc man-browser ed
  diffutils-doc python-setuptools-doc
The following NEW packages will be installed:
  binutils binutils-common binutils-x86-64-linux-gnu build-essential cpp cpp-9 dpkg-dev fakeroot g++ g++-9 gcc gcc-9
  gcc-9-base libalgorithm-diff-perl libalgorithm-diff-xs-perl libalgorithm-merge-perl libasan5 libatomic1 libbinutils
  libc-dev-bin libc6-dev libcc1-0 libcrypt-dev libctf-nobfd0 libctf0 libdpkg-perl libexpat1-dev libfakeroot
  libfile-fcntllock-perl libgcc-9-dev libgomp1 libisl22 libitm1 liblocale-gettext-perl liblsan0 libmpc3 libmpfr6
  libpython3-dev libpython3.8 libpython3.8-dev libquadmath0 libstdc++-9-dev libtsan0 libubsan1 linux-libc-dev make
  manpages manpages-dev patch python-pip-whl python3-dev python3-distutils python3-lib2to3 python3-pip
  python3-pkg-resources python3-setuptools python3-wheel python3.8-dev zlib1g-dev
0 upgraded, 59 newly installed, 0 to remove and 1 not upgraded.
Need to get 56.2 MB of archives.
After this operation, 241 MB of additional disk space will be used.
Do you want to continue? [Y/n] Y
```

Verify that pip was installed succesfully:

```bash
root@e0303ca291b2:/# pip --version
pip 20.0.2 from /usr/lib/python3/dist-packages/pip (python 3.8)
```

Install iac-validate python tool:

`pip install iac-validate`

```bash
root@e0303ca291b2:/# pip install iac-validate
Collecting iac-validate
  Downloading iac_validate-0.2.3-py3-none-any.whl (14 kB)
Collecting click<9.0.0,>=8.0.4
  Downloading click-8.1.7-py3-none-any.whl (97 kB)
     |████████████████████████████████| 97 kB 1.4 MB/s
Collecting errorhandler<3.0.0,>=2.0.1
  Downloading errorhandler-2.0.1-py2.py3-none-any.whl (5.5 kB)
Collecting ruamel-yaml>0.16.10
  Downloading ruamel.yaml-0.17.32-py3-none-any.whl (112 kB)
     |████████████████████████████████| 112 kB 3.0 MB/s
Collecting yamale<5.0.0,>=4.0.3
  Downloading yamale-4.0.4-py3-none-any.whl (55 kB)
     |████████████████████████████████| 55 kB 1.2 MB/s
Collecting ruamel.yaml.clib>=0.2.7; platform_python_implementation == "CPython" and python_version < "3.12"
  Downloading ruamel.yaml.clib-0.2.7-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_24_x86_64.whl (555 kB)
     |████████████████████████████████| 555 kB 3.3 MB/s
Collecting pyyaml
  Downloading PyYAML-6.0.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (736 kB)
     |████████████████████████████████| 736 kB 4.8 MB/s
Installing collected packages: click, errorhandler, ruamel.yaml.clib, ruamel-yaml, pyyaml, yamale, iac-validate
Successfully installed click-8.1.7 errorhandler-2.0.1 iac-validate-0.2.3 pyyaml-6.0.1 ruamel-yaml ruamel.yaml.clib-0.2.7 yamale-4.0.4

```

Vefify that iac-validate was installed succesfully:

```bash
root@e0303ca291b2:/# iac-validate --version
iac-validate, version 0.2.3
```

Finally, install pyats using command:

`pip install pyats["full"]`

```bash
root@48a41e2605e9:/# pip install "pyats[full]"
```
<br>

## 5. Create your first project

To create a new project navigate to `https://198.18.133.252` and click <b>Create a project</b>

![gitlab_2](images/gitlab_2.png)

<b>Create blank project</b>

![gitlab_9](images/gitlab_9.png)

Assign project name: `terraform-iac` and pick a group or namespace (Users -> root) then click <b>Create project button</b>

![gitlab_10](images/gitlab_10.png)

You should see terrraform-iac project created successfully:

![gitlab_11](images/gitlab_11.png)

<br>

## 6. Clone and modify repository

Navigate to your terraform-iac project, click and expand Clone button and copy <b>Clone with HTTP</b> URL:

![gitlab_12](images/gitlab_12.png)

```http://198.18.133.252/root/terraform-iac.git```

Click on `Windows CMD prompt` icon on Workstation Desktop

![terraform_1](images/terraform_1.png)

and clone terraform-iac empty repo using git clone command:

`git clone http://198.18.133.252/root/terraform-iac.git`

You wil be asked to enter credentials for your Gitlab instance. Use root as username and password you set up in section (2. Configure and Run Gitlab)

![gitlab_15_1](images/gitlab_15_1.png)

```
C:\Users\Administrator\Desktop>git clone http://198.18.133.252/root/terraform-iac.git
Cloning into 'terraform-iac'...
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
Receiving objects: 100% (3/3), done.

```

After cloning the repository, open the repository folder on your desktop. 

![gitlab_15](images/gitlab_15.png)

Next, open `terraform-bootcamp` repository folder cloned in [lab1](../lab1#2-clone-terraform-bootcamp-repository-to-workstation)

![gitlab_16](images/gitlab_16.png)

and copy following files and folders from `terraform-bootcamp`:

- labs/lab2/evpn/data 
- labs/lab2/evpn/modules
- labs/lab2/evpn/main.tf

- labs/lab3/files/schema.yaml
- labs/lab3/files/.gitlab-ci.yml
- labs/lab3/files/rules/
- labs/lab3/files/tests/
- labs/lab3/files/init.sh


to `terraform-iac` folder:

![gitlab_17](images/gitlab_17.png)


`Note` If you didn't work on lab2 make sure to execute script `remove_isis.py` from lab2/evpn/scripts [lab2 - remove_isis.py](../lab2/README.md#2-remove-legacy-routing-configuration-from-leafs-and-spine)

Next, open the `terraform-iac` repository folder on your desktop. Right-click on the `terraform-iac` folder and select `Open with Code`

![gitlab_18](images/gitlab_18.png)

Open Terminal in Visual Studio Code Editor by selecting `Terminal -> New Terminal`

![gitlab_19](images/gitlab_19.png)

![gitlab_20](images/gitlab_20.png)

<br>

## 7. Create Gitlab CICD pipeline

We will be building gitlab CI pipeline using evpn terraform code from [lab2](../lab2/evpn).

The pipeline itself is defined in a file called `.gitlab-ci.yml`.

The initial section of the `.gitlab-ci.yml` file includes the global configurations for the pipeline, such as variables and the definition of pipeline stages.

In a GitLab CI pipeline, stages represent the primary phases required in the build process. Each stage encompasses multiple individual jobs. Initially, all stages will be in a commented-out state, and we will gradually activate them as we advance through the lab exercises.

File `schema.yaml` is used for syntax pre-change validation of data model from `data` directory. Syntax validation ensures that the input data is syntactically correct, which is verified by Yamale and a corresponding schema. The [schema](../files/schema.yaml) specifies the expected structure, input value types (String, Enum, IP, etc.) and additional constraints (eg. value ranges, regexes, etc.).

For syntatic and sementic validation of YAML files in data folder we will be using [iac-validate](https://github.com/netascode/iac-validate) python tool.

Semantic validation is done by providing a set of rules (implemented in Python) which are then validated against the YAML data. Every rule is implemented as a Python class and should be placed in a .py file located in the --rules [path](../files/rules).

<br>

## 8. Configure Gitlab variables

In lab 2 credentials to access spines and leaves were provided to terraform in main.tf file. In Gitlab we can use Variables.

Let's remove username and password from provider configuration in main.tf:

```sh
provider "iosxe" {
  devices  = local.devices
}
```

keep only `devices = local.devices` under provider.


Next, navigate to `terraform-iac` repository on Gitlab and go to `Settings` and select `CI/CD`. We will add IOSXE_PASSWORD and IOSXE_USERNAME variables.

![gitlab_21](images/gitlab_21.png)

Add the following variables:

- IOSXE_PASSWORD: set this to `C1sco12345`. Click on `Mask variable`.
- IOSXE_USERNAME: set this to `developer`.

![gitlab_23](images/gitlab_23.png)

![gitlab_22](images/gitlab_22.png)


When finished you should see the following secrets added to your repository:

![gitlab_24](images/gitlab_24.png)

<br>

## 9. Gitlab CI Pipeline - Init Stage

The `Init` stage initializes a working directory and downloads the necessary provider plugins and modules and setting up the GitLab server as http backend for storing state file.

To configure Gitlab as backend first create Access Token. Go to terraform-iac project and select `Settings -> Access Tokens`:

![gitlab_24_1](images/gitlab_24_1.png)

Add new token:

```
Token name: terraform
Role: Maintainer
Scope: api
```

![gitlab_24_2](images/gitlab_24_2.png)

Copy the token and save it in a temp file.

`Note` The token can not be viewed again and you need it later!

![gitlab_24_3](images/gitlab_24_3.png)

Next, create TF_USERNAME and TF_PASSWORD variables in `Settings -> CI/CD -> Variables`:

```
TF_USERNAME: root

TF_PASSWORD: (use your token that you copied, and select Mask Variable)
```

![gitlab_24_4](images/gitlab_24_4.png)

![gitlab_24_5](images/gitlab_24_5.png)

File called `init.sh` contains commands to initialize the Terraform environment to use your GitLab server with all the required credentials (user / token).

Before starting pipeline add terraform backend http configuration terraform section in main.tf file:

```hcl
terraform {
  backend "http" {
  }
}
```

![gitlab_42](images/gitlab_42.png)


Next uncomment the init stage in the `stages` section of the pipeline definition in `.gitlab-ci.yml` file:

```yaml
stages:
  - init
```

and `init` section:

```yaml
init:
  stage: init
  script:
    - chmod +x init.sh
    - ./init.sh  |& tee init_output.txt
  artifacts:
    paths:
      - init_output.txt
    expire_in: 30 min
    when: always
```

Add files to git and push to Gitlab. To do this run following commands:

```ps
git config --global user.email "admin@lab"
git config --global user.name "admin"
git add .
git commit -m "added init stage"
git push
```

Once you have pushed the file to Gitlab, access Gitlab in your browser and navigate to the CI/CD section on the left. Gitlab will automatically trigger a pipeline execution when it notices a .gitlab-ci.yml file. Hence, in Gitlab you should see that a pipeline is being executed.

Navigate to your project:

`http://198.18.133.252/terraform-iac`

and check pipeline status (red rectangle)

![gitlab_27](images/gitlab_27.png)

Green icon indicates that terraform backend was initialized successfully and terraform state is not using Gitlab server.

<br>

## 10. Gitlab CI Pipeline - Validate Stage
 
The `Validate` stage performs syntactic and semantic validations on your inventory.

Start by uncommenting the validate stage in the `stages` section of the pipeline definition in `.gitlab-ci.yml` file:

```yaml
stages:
  - init
  - validate
```

and `validate` and `fmt` sections:

```yaml
validate:
  stage: validate
  script:
    - iac-validate --schema schema.yaml --rules ./rules/ ./data/ |& tee validate_output.txt
  artifacts:
    paths:
      - validate_output.txt
    expire_in: 30 min
    when: always

fmt:
  stage: validate
  script:
    - terraform fmt -check -recursive -diff |& tee fmt_output.txt
  artifacts:
    paths:
      - fmt_output.txt
    expire_in: 30 min
    when: always
  needs:
    - validate
```

Add files to git and push to Gitlab:

```ps
git add .
git commit -m "added validate stage"
git push
```

Navigate to your project:

`http://198.18.133.252/terraform-iac`

and check pipeline status:

![gitlab_26](images/gitlab_26.png)

Green icon indicates that all jobs in pipeline were executed succesfully. Click on green icon to check details:

![gitlab_28](images/gitlab_28.png)


<br>

## 11. Gitlab CI Pipeline - Plan Stage

Next up is the plan stage, similar to validate stage enable plan stage in the `stages` section of the pipeline definition.

```yaml
stages:
  - init
  - validate
  - plan
```

and `plan` section:

```yaml
plan:
  stage: plan
  script:
    - terraform plan -out=plan.tfplan -input=false
    - terraform show -no-color plan.tfplan > plan.txt
    - terraform show -json plan.tfplan > plan.json
  artifacts:
    paths:
      - plan.tfplan
      - plan.txt
      - plan.json
    expire_in: 30 min
    when: always
  needs:
    - validate
    - fmt
  only:
    - merge_requests
    - main
```

The Terraform plan is exported as files which are saved as artifacts. This plan will be used in the next stage as input into the `terraform apply` command.

With these modifications, go ahead and commit the `.gitlab-ci.yml` file to gitlab, and verify if the corresponding pipeline run was successful.

```ps
git add .
git commit -m "added plan stage"
git push
```

Navigate to your project:

`http://198.18.133.252/root/terraform-iac`

and check new pipeline status:

![gitlab_29](images/gitlab_29.png)

Terraform plan is saved as artifacts (plan.json, plan.tfplan, plan.txt), you can download it clicking on `plan` job icon and then Download

![gitlab_31](images/gitlab_31.png)

![gitlab_30](images/gitlab_30.png)

<br>

## 12. Gitlab CI Pipeline - Deploy Stage

As with the other stages, start by enabling this stage in the pipeline file.

```yaml
stages:
  - init
  - validate
  - plan
  - deploy
```

and `deploy` section:

```yaml
deploy:
  stage: deploy
  script:
    - terraform apply -input=false -auto-approve plan.tfplan  |& tee deploy_output.txt
  artifacts:
    paths:
      - deploy_output.txt
    expire_in: 30 min
    when: always
  dependencies:
    - plan
  needs:
    - plan
  only:
    - main
```

Trigger pipeline by pushing changes to Gitlab:
```ps
git add .
git commit -m "added deploy stage"
git push
```

To deploy configuration click on "play" button on deploy icon:

![gitlab_32_1](images/gitlab_32_1.png)

After deploy click deploy icon and inspec job logs. You should see similar terraform apply output you saw in lab2:

![gitlab_32](images/gitlab_32.png)

![gitlab_33](images/gitlab_33.png)

You can now check if BGP EVPN VXLAN was deployed following section 8 in [lab2](../lab2/README.md#8-verify-bgp-evpn-vxlan-configuration)
<br>

## 13. Gitlab CI Pipeline - Test Stage

The test stage is responsible for running pyats tests that performs post-deployment validation. As with the other stages we will start by enabling it in the pipeline.

```yaml
stages:
  - init
  - validate
  - plan
  - deploy
  - test
```

and `test` section:

```yaml
test-pyats:
  stage: test
  script:
    - set -o pipefail && pyats run job ./tests/evpn_pyats/evpn_pyats_job.py --testbed ./tests/testbed.yml |& tee test_output.txt
  artifacts:
    when: always
    paths:
      - test_output.txt
  cache: []
  dependencies:
    - deploy
  needs:
    - deploy
  only:
    - main
```

Trigger pipeline by pushing changes to Gitlab:
```ps
git add .
git commit -m "added test stage"
git push
```

Click deploy and wait for test stage to finish:

![gitlab_34](images/gitlab_34.png)

Click test-pyats job icon and inspec job logs. You should see following output:

![gitlab_35](images/gitlab_35.png)


There are 3 tests in pyats:

- `ospf_connectivity` - Check if all OSPF neigbhor relationships are in FULL state

- `bgp_connectivity` - Check if BGP neighbors are in Established state

- `nve_peers_connectivity` - Check if NVE peer is in UP state

<br>

## 14. Testing Pipeline Failures 


### Break validate stage

Let's break validate stage by modifing underlay.yaml file in data folder:

1. Change device in line nr 7 from LEAF-1 to LEAF-3:

![gitlab_36](images/gitlab_36.png)

and push changes to gitlab:

```ps
git add .
git commit -m "validate break" 
git push
```

![gitlab_38](images/gitlab_38.png)

Click on validate icon to inspect why validate stage failed:

![gitlab_37](images/gitlab_37.png)

You can see semantic error message for rule [101](./files/rules/101_inventory_references.py):

```sh
ERROR - Semantic error, rule 101: Verify Inventory references in underlay.yaml (['device LEAF-3 not found in inventory.yaml'])
```

Let's revert the change, by changing LEAF-3 to LEAF-1 again in underlay.yaml file. Don't push the changes.

### Break test stage

Let's break test stage by shutting down bgp neighbor on LEAF-1.

1. Connect via SSH to LEAF-1 device (198.18.1.31 - developer/C1sco12345)  and run following command:

```sh
conf t
router bgp 65000
neighbor 100.65.0.1 shutdown
```

![gitlab_39](images/gitlab_39.png)

In previous section, we modified underlay.yaml file, so we can trigger pipeline by pushing changes to gitlab:

```ps
git add .
git commit -m "test break" 
git push
```

Click on deploy button:

![gitlab_40_1](images/gitlab_40_1.png)

Click on pyats_test icon to inspect why test stage failed:

![gitlab_41](images/gitlab_41.png)

You can see that bgp_connectivity test failed. This is expected behaviour, because we manually shutdown bgp neighbor on LEAF-1.

<br></br>

---

### Great job! You've successfully implemented Terraform IAC using GitLab CI. You're now equipped to tackle more advanced coding tasks with confidence. Keep up the excellent work and keep exploring new horizons. Well done!
