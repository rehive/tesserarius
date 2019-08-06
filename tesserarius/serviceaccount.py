from os.path import abspath
from re import match

from tesserarius.utils import get_gcloud_wide_flags, get_settings
from invoke.exceptions import Failure, UnexpectedExit, ParseError
from tesserarius.utils import get_error_stream as terr, \
    get_out_stream as tout, confirm

BASE_NAME_PATTERN = r'((-staging)?$)|(-[a-z]{3,10}(-staging)?$)'

class ServiceAccountValidationError(Exception):
    pass


class ServiceAccountCreateError(Exception):
    pass


class BaseServiceAccount():
    project_id = None
    name = None
    emailaddress = None
    display_name = ""
    description = ""
    name_pattern = None
    role = None

    created = False

    def __init__(self,
                 name=None,
                 display_name=None,
                 role=None,
                 description=None,
                 name_pattern=None):
        self.name_pattern = name_pattern
        self.name = name
        self.display_name = display_name
        self.description = description
        self.role = role

        if name_pattern is None:
            self.name_pattern = BASE_NAME_PATTERN


    def __str__(self):
        return "account_name: {name}, " \
                "display_name: {display_name}, "\
                "project_id: {project_id}, "\
                "role: {role}, "\
                "description: {description}".format(
                    name=self.name,
                    display_name=self.display_name,
                    project_id=self.project_id,
                    role=self.role,
                    description=self.description
                )


    def _check_name(self):
        """
        Checks if self.name has the correct naming convention

        <role_name>

        short name for the service account describing its purpose.
        Example: staging, media-staging, pgbackup, pgbackup-staging
        """
        if not match(r"^{}$".format(self.name_pattern), self.name):
            raise ServiceAccountValidationError("Invalid account name.")


    def get_emailaddress(self):
        self.emailaddress = "{name}@{project_id}" \
            ".iam.gserviceaccount.com".format(
                name=self.name, project_id=self.project_id)
        return self.emailaddress


    def create(self, ctx):
        """
        Creates an IAM GCloud Service Account
        """
        print("\nCreating service account '{name}' ... ".format(name=self.name),
              end="")
        command = "gcloud alpha iam service-accounts create {name}" \
                    " --display-name \"{display_name}\"" \
                    " --description \"{description}\"" \
                    " --verbosity debug " \
                    " --project {project_id}"

        if not self.created:
            try:
                result = ctx.run(command.format(
                    name=self.name,
                    display_name=self.display_name,
                    description=self.description,
                    project_id=self.project_id),
                echo=False,out_stream=tout(), err_stream=terr())
                self.get_emailaddress()
                self.created = True
                print("SUCCESS!")
            except (Failure, UnexpectedExit,):
                self.emailaddress = None
                print("FAILED! [Operation Failed]")

        elif self.created:
            print("FAILED! [SA already created]")


    def update(self, ctx):
        """
        Updates an IAM GCloud Service Account
        """
        print("\nUpdating service account '{name}' ... ".format(name=self.name),
              end="")
        self.get_emailaddress()
        command = "gcloud alpha iam service-accounts update {emailaddress}" \
                    " --display-name \"{display_name}\"" \
                    " --description \"{description}\"" \
                    " --verbosity debug " \
                    " --project {project_id}"

        try:
            result = ctx.run(command.format(
                emailaddress=self.emailaddress,
                display_name=self.display_name,
                description=self.description,
                project_id=self.project_id),
            echo=False,out_stream=tout(), err_stream=terr())
            self.get_emailaddress()
            print("SUCCESS!")
        except (Failure, UnexpectedExit,):
            self.emailaddress = None
            print("FAILED! [Operation Failed]")


    def delete(self, ctx):
        """
        Deletes an IAM GCloud Service Account
        """
        print("\nDeleting service account '{name}' ... ".format(name=self.name),
              end="")
        self.get_emailaddress()
        command = "gcloud alpha iam service-accounts delete {emailaddress}" \
                    " --verbosity debug " \
                    " --project {project_id}"

        try:
            confirm("\nAre you sure you want to delete SA '{email}'? (y/n) "
                    .format(email=self.emailaddress))
            result = ctx.run(command.format(
                emailaddress=self.emailaddress,
                project_id=self.project_id),
            echo=False,out_stream=tout(), err_stream=terr())
            print("SUCCESS!")
        except (Failure, UnexpectedExit,):
            self.emailaddress = None
            print("FAILED! [Operation Failed]")
        except ParseError:
            self.emailaddress = None
            print("FAILED! [Operation cancelled by user]")


    def bind(self, ctx):
        """
        Bind an IAM GCloud Service Account
        """
        print("\nBinding service account '{name}' ... ".format(name=self.name),
              end="")
        self.get_emailaddress()
        command = "gcloud projects add-iam-policy-binding {project_id}" \
                    " --member=serviceAccount:{emailaddress}" \
                    " --role=projects/{project_id}/roles/{role}"
        try:
            result = ctx.run(command.format(
                emailaddress=self.emailaddress,
                role=self.role,
                project_id=self.project_id),
            echo=False,out_stream=tout(), err_stream=terr())
            print("SUCCESS!")
        except (Failure, UnexpectedExit,):
            self.emailaddress = None
            print("FAILED! [Operation Failed]")
        except ParseError:
            self.emailaddress = None
            print("FAILED! [Operation cancelled by user]")


    def upload(self, ctx, namespace, secret):
        """
        Upload key file to Kubernetes Cluster as a secrets
        """
        print("\nUploading private key for '{name}' ... ".format(name=self.name),
              end="")
        self.get_emailaddress()
        key_file = "var/tesserarius/" + self.name + ".json"
        key_file = abspath(key_file)

        commands = [
            {
                "cmd" : "gcloud iam service-accounts describe {emailaddress} " \
                    " --project {project_id}",
                "format" : {
                    "emailaddress" : self.emailaddress,
                    "project_id" : self.project_id,
                },
            },
            {
                "cmd" : "kubectl get namespace {namespace} -o name",
                "format" : {
                    "namespace" : namespace,
                },
            },
            {
                "cmd" : "gcloud iam service-accounts keys create {key_file} " \
                    " --iam-account={emailaddress}" \
                    " --key-file-type=\"json\"" \
                    " --project {project_id}",
                "format" : {
                    "key_file" : key_file,
                    "emailaddress" : self.emailaddress,
                    "project_id" : self.project_id,
                },
            },
            {
                "cmd" : "kubectl delete secret {secret} " \
                    " --namespace {namespace} || touch {key_file}",
                "format" : {
                    "secret" : secret,
                    "key_file" : key_file,
                    "namespace" : namespace,
                },
            },
            {
                "cmd" : "kubectl create secret generic {secret} " \
                    " --from-file={secret}.json={key_file}"
                    " --namespace {namespace}",
                "format" : {
                    "key_file" : key_file,
                    "secret" : secret,
                    "namespace" : namespace,
                },
            },
            {
                "cmd" : "rm -rf {key_file}",
                "format" : {
                    "key_file" : key_file,
                },
            },
        ]
        try:
            for op in commands:
                result = ctx.run(op["cmd"].format(**op["format"]),
                    echo=False, out_stream=tout(), err_stream=terr())
            print("SUCCESS!")
        except (Failure, UnexpectedExit,):
            print("FAILED! [Operation Failed]")
        except ParseError:
            print("FAILED! [Operation cancelled by user]")


    @staticmethod
    def create_objs(project):
        settings_dict = get_settings()
        try:
            project_dict = settings_dict[project]
        except KeyError:
            raise ServiceAccountCreateError(
                "Config '{project}' not found.".format(project=project))

        serviceAccounts = project_dict['serviceAccount']
        objs = list()
        for i in range (len(serviceAccounts)):
            try:
                objs.append(BaseServiceAccount(
                    name=serviceAccounts[i]['name'],
                    description=serviceAccounts[i]['description'],
                    role=serviceAccounts[i]['role'],
                    display_name=serviceAccounts[i]['displayName']))

            except KeyError:
                raise ServiceAccountCreateError(
                    "Config '{project}' has invalid keys.".format(project=project))
        return objs
