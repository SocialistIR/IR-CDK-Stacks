
# IR-CDK-Stacks

## Requirements

- Python 3.7
- AWS CLI

##  Getting started

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the .env
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .env/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .env\Scripts\activate.bat
```


## Install dependencies

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

Additionally, you will need to install other dependencies manually in order for the CLI to work.

### AWS CLI v2

```
$ curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && sudo ./aws/install
```

### AWS CDK

```
$ curl -sL https://deb.nodesource.com/setup_13.x | sudo -E bash - && sudo apt-get install -y nodejs && npm install -g aws-cdk
```

### Other testing dependencies

```
$ sudo apt-get install postgresql libpq-dev postgresql-client postgresql-client-common pgdb
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## IR CLI usage

```
python cdk.py
```

## Deployment

Configure your AWS account using the AWS CLI.

Note: You need to setup the correct region to deploy your stacks to.

```
$ aws configure
```

Deploy the stacks.

```
$ cdk deploy
```

## Testing

Unit tests are located in `/tests` directory.

```
$ pytest
```

## Linting

It is good to have clean code.

```
$ flake8 .
```

## Clean up

Destroy the app's resources to avoid incurring any costs from the resources created.

```
$ cdk destroy
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
