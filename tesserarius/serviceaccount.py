from os.path import abspath
from re import match

from tesserarius.utils import get_gcloud_wide_flags, get_settings
from invoke.exceptions import Failure, UnexpectedExit, ParseError
from tesserarius.utils import get_error_stream as terr, \
    get_out_stream as tout, confirm

BASE_NAME_PATTERN = r'([a-z]{3,10}(-staging)?)'


class ServiceAccountValidationError(Exception):
    pass


class ServiceAccountCreateError(Exception):
    pass


class BaseServiceAccount:
    project_id = None
    name = None
    emailaddress = None
    display_name = ""
    description = ""
    name_pattern = None
    role = None
    environment = None
    environment_settings = None

    created = False

    def __init__(self,
                 name=None,
                 display_name=None,
                 role=None,
                 description=None,
                 name_pattern=None,
                 environment=None,
                 environment_settings=None):
        self.name_pattern = name_pattern
        self.name = name
        self.display_name = display_name
        self.description = description
        self.role = role
        self.environment = environment
        self.environment_settings = environment_settings

        if name_pattern is None:
            self.name_pattern = BASE_NAME_PATTERN

    def __str__(self):
        return f"account_name: {self.name}, "\
            f"display_name: {self.display_name}, "\
            f"project_id: {self.project_id}, "\
            f"role: {self.role}, "\
            f"description: {self.description}"

    def _check_name(self):
        """
        Checks if self.name has the correct naming convention

        <role_name>

        short name for the service account describing its purpose.
        Example: staging, media-staging, pgbackup, pgbackup-staging
        """
        if not match(rf"^{self.name_pattern}$", self.name):
            raise ServiceAccountValidationError(
                f"Invalid account name. {self.name} "
                f"doesn't fit standard '{self.name_pattern}'")
        if len(self.name) >= 30:
            raise ServiceAccountValidationError(
                f"Account name '{self.name}' is too long (max length: 30).")

    def get_emailaddress(self):
        self.emailaddress = f"{self.name}@{self.project_id}.iam.gserviceaccount.com"
        return self.emailaddress

    def create(self, ctx):
        """
        Creates an IAM GCloud Service Account
        """
        print(f"\nCreating service account '{self.name}' ... ", end="")
        command = f"gcloud alpha iam service-accounts create {self.name}" \
            f" --display-name \"{self.display_name}\"" \
            f" --description \"{self.description}\"" \
            f" --verbosity debug " \
            f" --project {self.project_id}"

        if not self.created:
            try:
                result = ctx.run(command,
                                 echo=False, out_stream=tout(), err_stream=terr())
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
        print(f"\nUpdating service account '{self.name}' ... ", end="")
        self.get_emailaddress()
        command = f"gcloud alpha iam service-accounts update {self.emailaddress}" \
            f" --display-name \"{self.display_name}\"" \
            f" --description \"{self.description}\"" \
            f" --verbosity debug " \
            f" --project {self.project_id}"

        try:
            result = ctx.run(command, echo=False,out_stream=tout(), err_stream=terr())
            self.get_emailaddress()
            print("SUCCESS!")
        except (Failure, UnexpectedExit,):
            self.emailaddress = None
            print("FAILED! [Operation Failed]")

    def delete(self, ctx):
        """
        Deletes an IAM GCloud Service Account
        """
        print(f"\nDeleting service account '{self.name}' ... ", end="")
        self.get_emailaddress()
        command = f"gcloud alpha iam service-accounts delete {self.emailaddress}" \
            f" --verbosity debug " \
            f" --project {self.project_id}"

        try:
            confirm(f"\nAre you sure you want to delete SA '{self.emailaddress}'? (y/n) ")
            result = ctx.run(command, echo=False,out_stream=tout(), err_stream=terr())
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
        print(f"\nBinding service account '{self.name}' ... ", end="")
        self.get_emailaddress()
        commands = [
            {
                "cmd": f"gcloud iam service-accounts describe {self.emailaddress}"
                       f" --project {self.project_id}",
            },
            {
                "cmd": f"gcloud iam roles describe {self.role}"
                       f" --project {self.project_id}",
            },
            {
                "cmd": f"gcloud projects add-iam-policy-binding {self.project_id}"
                       f" --member=serviceAccount:{self.emailaddress}"
                       f" --role=projects/{self.project_id}/roles/{self.role}"
                       f" --project {self.project_id}",
            },
        ]
        try:
            for op in commands:
                result = ctx.run(op["cmd"], echo=False, out_stream=tout(), err_stream=terr())
            print("SUCCESS!")
        except (Failure, UnexpectedExit,):
            print("FAILED! [Operation Failed]")
        except ParseError:
            print("FAILED! [Operation cancelled by user]")

    def chown(self, ctx, bucket):
        """
        Upload key file to Kubernetes Cluster as a secrets
        """
        print(f"\nChanging ownership of '{bucket}' to '{self.name}' ... ",
              end="")
        self.get_emailaddress()
        key_file = "var/tesserarius/" + self.name + ".json"
        key_file = abspath(key_file)

        commands = [
            {
                "cmd": f"gcloud iam service-accounts describe {self.emailaddress} "
                       f" --project {self.project_id}",
            },
            {
                "cmd": f"gsutil ls gs://{bucket}",
            },
            {
                "cmd": f"gsutil defacl set private gs://{bucket}",
            },
            {
                "cmd": f"gsutil defacl ch -u {self.emailaddress}:owner "
                       f" gs://{bucket}",
            },
        ]
        try:
            for op in commands:
                result = ctx.run(op["cmd"], echo=False,
                                 out_stream=tout(), err_stream=terr())
            print("SUCCESS!")
        except (Failure, UnexpectedExit,):
            print("FAILED! [Operation Failed]")
        except ParseError:
            print("FAILED! [Operation cancelled by user]")

    def upload(self, ctx, secret):
        """
        Upload key file to Kubernetes Cluster as a secrets
        """
        print(f"\nUploading private key for '{self.name}' ... ", end="")
        self.get_emailaddress()
        key_file = "var/tesserarius/" + self.name + ".json"
        key_file = abspath(key_file)
        namespace = self.environment_settings["kubernetes"]["namespace"]

        commands = [
            {
                "cmd": f"gcloud iam service-accounts describe "
                    f"{self.emailaddress} "
                    f"--project {self.project_id}",
            },
            {
                "cmd": f"kubectl get namespace {namespace} -o name",
            },
            {
                "cmd": f"gcloud iam service-accounts keys create {key_file} "
                    f" --iam-account={self.emailaddress}"
                    f" --key-file-type=\"json\""
                    f" --project {self.project_id}",
            },
            {
                "cmd": f"kubectl delete secret {secret} "
                    f" --namespace {namespace} || touch {key_file}",
            },
            {
                "cmd": f"kubectl create secret generic {secret} "
                    f" --from-file={secret}.json={key_file}"
                    f" --namespace {namespace}",
            },
            {
                "cmd": f"rm -rf {key_file}",
            },
        ]

        try:
            for op in commands:
                ctx.run(op["cmd"], echo=False, out_stream=tout(), err_stream=terr())
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
            environment_settings = settings_dict["environment"][project]
        except KeyError:
            raise ServiceAccountCreateError(f"Config '{project}' not found.")

        service_accounts = project_dict['serviceAccount']
        objs = list()
        for i in range(len(service_accounts)):
            try:
                obj = BaseServiceAccount(
                    name=service_accounts[i]['name'],
                    description=service_accounts[i]['description'],
                    role=service_accounts[i]['role'],
                    display_name=service_accounts[i]['displayName'],
                    environment=service_accounts[i]['environment'])
                obj.environment_settings = environment_settings[obj.environment]
                objs.append(obj)
            except KeyError:
                raise ServiceAccountCreateError(f"Config '{project}' has invalid keys.")
        return objs
