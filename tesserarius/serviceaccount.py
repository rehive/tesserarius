from re import match

from tesserarius.utils import get_gcloud_wide_flags, get_settings
from invoke.exceptions import Failure, UnexpectedExit
from tesserarius.utils import get_error_stream as terr, get_out_stream as tout

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

    created = False

    def __init__(self,
                 name=None,
                 display_name=None,
                 description=None,
                 name_pattern=None):
        self.name_pattern = name_pattern
        self.name = name
        self.display_name = display_name
        self.description = description

        if name_pattern is None:
            self.name_pattern = BASE_NAME_PATTERN


    def __str__(self):
        return "account_name: {name}, \
                display_name: {display_name},  \
                project_id: {project_id},  \
                description: {description}".format(
                    name=self.name,
                    display_name=self.display_name,
                    project_id=self.project_id,
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
        '''
        Creates an IAM GCloud Service Account
        '''
        print("Creating service account '{name}' ... ".format(name=self.name),
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
                print("FAILED! [serviceaccount can't be created]'")

        elif self.created:
            print("FAILED! [serviceaccount has already been created]'")


    def update(self, ctx):
        '''
        Updates an IAM GCloud Service Account
        '''
        print("Updating service account '{name}' ... ".format(name=self.name),
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
            print("FAILED! [serviceaccount can't be updated]'")


    def delete(self, ctx):
        '''
        Deletes an IAM GCloud Service Account
        '''
        print("Deleting service account '{name}' ... ".format(name=self.name),
              end="")
        self.get_emailaddress()
        command = "gcloud alpha iam service-accounts delete {emailaddress}" \
                    " --verbosity debug " \
                    " --project {project_id}"

        try:
            result = ctx.run(command.format(
                emailaddress=self.emailaddress,
                project_id=self.project_id),
            echo=False,out_stream=tout(), err_stream=terr())
            self.get_emailaddress()
            print("SUCCESS!")
        except (Failure, UnexpectedExit,):
            self.emailaddress = None
            print("FAILED! [serviceaccount can't be deleted]'")


    @staticmethod
    def create_obj(project):
        settings_dict = get_settings()
        try:
            project_dict = settings_dict[project]
        except KeyError:
            raise ServiceAccountCreateError(
                "Config '{project}' not found.".format(project=project))

        try:
            return BaseServiceAccount(
                name=project_dict['serviceAccount']['name'],
                description=project_dict['serviceAccount']['description'],
                display_name=project_dict['serviceAccount']['displayName'])

        except KeyError:
            raise ServiceAccountCreateError(
                "Config '{project}' has invalid keys.".format(project=project))

