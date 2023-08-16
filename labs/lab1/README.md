# LAB 1 - Introduction to Terraform

## Lab Overview

Welcome to the Terraform Introduction Lab! In this hands-on learning experience, you will dive into the world of Infrastructure as Code (IaC) using Terraform. Throughout this lab, you will gain practical skills and foundational knowledge that will empower you to create, modify, and manage resources in a declarative and efficient manner.

## Lab Sections:

1. <b>Introduction to IaC and Terraform Basics:</b> Understand the concept of Infrastructure as Code and explore the fundamental concepts of Terraform, setting the stage for the hands-on exercises.

2. <b>Environment Setup:</b> Learn how to set up your local development environment to start using Terraform effectively, including installing the necessary tools and configuring providers.

3. <b>Declaring Infrastructure:</b> Dive into writing Terraform configuration files to define various cloud resources such as virtual machines, networks, and storage.

4. <b>Applying Infrastructure Changes:</b> Discover the process of using Terraform to apply your configurations and create or modify resources in your cloud environment.

5. <b>Managing Configuration Flexibility:</b> Explore the use of variables to make your configurations more dynamic and reusable, and learn how to structure your code using modules.

6. <b>Planning and Previewing Changes:</b> Learn how to use terraform plan to preview changes before applying them, minimizing risks and ensuring desired outcomes.

7. <b>State Management:</b> Understand the importance of managing Terraform state and explore best practices for maintaining its integrity.

8. <b>Hands-on Exercises:</b> Put your knowledge into practice by working through a series of guided exercises, creating infrastructure step by step.

9. <b>Troubleshooting and Best Practices:</b> Learn strategies for troubleshooting common issues and gain insights into best practices for maintaining Terraform projects over time.

10. <b>Wrap-up and Next Steps:</b> Recap what you've learned, receive pointers for further exploration, and understand how to continue your Terraform journey.

By the end of this lab, you will have the skills and confidence to leverage Terraform to orchestrate infrastructure in a scalable, efficient, and reproducible way. Let's embark on this exciting journey to transform your understanding of infrastructure provisioning!



## Prerequisites

- Docker installed [Get Docker](https://docs.docker.com/get-docker/)

- Access to Internet

<br>

## Time Estimates

2 hours

<br>

<br></br>
---

## 1. Upgrade/Install Terraform to latest version

To upgrade Terraform to latest version (v1.5.5) open Windows Command prompt and run following command: `hoco install terraform --version=1.5.5 --force`

```C:\Users\Administrator>choco install terraform --version=1.5.5 --force
Chocolatey v1.1.0
Chocolatey detected you are not running from an elevated command shell
 (cmd/powershell).

 You may experience errors - many functions/packages
 require admin rights. Only advanced users should run choco w/out an
 elevated shell. When you open the command shell, you should ensure
 that you do so with "Run as Administrator" selected. If you are
 attempting to use Chocolatey in a non-administrator setting, you
 must select a different location other than the default install
 location. See
 https://docs.chocolatey.org/en-us/choco/setup#non-administrative-install
 for details.


 Do you want to continue?([Y]es/[N]o): Y

Installing the following packages:
terraform
By installing, you accept licenses for the packages.
terraform v1.5.5 already installed. Forcing reinstall of version '1.5.5'.
 Please use upgrade if you meant to upgrade to a new version.

terraform v1.5.5 (forced) [Approved]
terraform package files install completed. Performing other installation steps.
The package terraform wants to run 'chocolateyInstall.ps1'.
Note: If you don't run this script, the installation will fail.
Note: To confirm automatically next time, use '-y' or consider:
choco feature enable -n allowGlobalConfirmation
Do you want to run the script?([Y]es/[A]ll - yes to all/[N]o/[P]rint): A

Removing old terraform plugins
Downloading terraform 64 bit
  from 'https://releases.hashicorp.com/terraform/1.5.5/terraform_1.5.5_windows_amd64.zip'
Progress: 100% - Completed download of C:\Users\Administrator\AppData\Local\Temp\chocolatey\terraform\1.5.5\terraform_1.5.5_windows_amd64.zip (19.99 MB).
Download of terraform_1.5.5_windows_amd64.zip (19.99 MB) completed.
Hashes match.
Extracting C:\Users\Administrator\AppData\Local\Temp\chocolatey\terraform\1.5.5\terraform_1.5.5_windows_amd64.zip to C:\ProgramData\chocoportable\lib\terraform\tools...
C:\ProgramData\chocoportable\lib\terraform\tools
 ShimGen has successfully created a shim for terraform.exe
 The install of terraform was successful.
  Software installed to 'C:\ProgramData\chocoportable\lib\terraform\tools'

Chocolatey installed 1/1 packages.
 See the log for details (C:\ProgramData\chocoportable\logs\chocolatey.log).
```

Verify if terraform was updated successfully by running `terraform version` command:

```
C:\Users\Administrator>terraform version
Terraform v1.5.5
on windows_amd64
```

1. Open a terminal or command prompt.

2. Type the following command and press Enter:


<br></br>

---

### Congratulations on completing the Docker Introduction lab! You have taken an important step in learning how to use Docker to build, ship, and run applications in a containerized environment.