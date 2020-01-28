from re import match

from tesserarius.utils import get_gcloud_wide_flags, get_settings
from invoke.exceptions import Failure, UnexpectedExit, ParseError
from tesserarius.utils import get_error_stream as terr, \
    get_out_stream as tout, confirm

class RoleValidationError(Exception):
    pass


class RoleCreateError(Exception):
    pass


class BaseRole():
    project_id = None
    name = None
    title = None
    stage = None
    permissions = ""
    description = ""

    created = False

    def __init__(self, name=None, title="", stage=None,
                 description=None, permissions=None,
                 add_permissions=None, remove_permissions=None):
        if stage in ('ALPHA', 'BETA', 'GA', 'DEPRECATED', 'EAP',):
            self.stage = stage
        else:
            raise RoleCreateError("Invalid stage value")

        self.name = name
        self.title = title
        self.permissions = permissions
        self.add_permissions = add_permissions
        self.remove_permissions = remove_permissions
        self.description = description


    def __str__(self):
        return f"name: {self.name}, " \
            f"title: {self.title}, " \
            f"stage: {self.stage}, " \
            f"project_id: {self.project_id}, " \
            f"permissions: {self.permissions!s}, " \
            f"remove_permissions: {self.remove_permissions!s}, " \
            f"add_permissions: {self.add_permissions!s}, " \
            f"description: {self.description}"


    def create(self, ctx):
        """
        Creates an IAM GCloud Service Account
        """
        print(f"\nCreating role '{self.name}' ... ",
              end="")
        permissions_str = ",".join(self.permissions)
        command = f"gcloud iam roles create {self.name}" \
                    f" --title \"{self.title}\"" \
                    f" --permissions \"{permissions_str}\"" \
                    f" --stage \"{self.stage}\"" \
                    f" --description \"{self.description}\"" \
                    f" --verbosity debug " \
                    f" --project {self.project_id}"

        if not self.created:
            try:
                result = ctx.run(command, echo=False,
                                 out_stream=tout(), err_stream=terr())
                self.created = True
                print("SUCCESS!")
            except (Failure, UnexpectedExit,):
                print("FAILED! [Operation Failed]")

        elif self.created:
            print("FAILED! [SA already created]")


    def update(self, ctx):
        """
        Updates an IAM GCloud Service Account
        """
        print(f"\nUpdating role '{self.name}' ... ",
              end="")
        permissions_str = ",".join(self.permissions)
        add_permissions_str = ",".join(self.add_permissions)
        remove_permissions_str = ",".join(self.remove_permissions)
        command = f"gcloud iam roles update {self.name}" \
                    f" --title \"{self.title}\"" \
                    f" --permissions \"{permissions_str}\"" \
                    f" --add-permissions \"{add_permissions_str}\"" \
                    f" --remove-permissions \"{remove_permissions_str}\"" \
                    f" --stage \"{self.stage}\"" \
                    f" --description \"{self.description}\"" \
                    f" --verbosity debug " \
                    f" --project {self.project_id}"

        try:
            result = ctx.run(command, echo=False,
                             out_stream=tout(), err_stream=terr())
            print("SUCCESS!")
        except (Failure, UnexpectedExit,):
            self.emailaddress = None
            print("FAILED! [Operation Failed]")


    def delete(self, ctx):
        """
        Deletes an IAM GCloud IAM Role
        """
        print(f"\nDeleting role '{self.name}' ... ", end="")
        self.get_emailaddress()
        command = f"gcloud iam roles delete {self.name}" \
                    f" --verbosity debug " \
                    f" --project {self.project_id}"

        try:
            confirm(
                f"\nAre you sure you want to delete role '{self.name}'? (y/n) ")
            result = ctx.run(command, echo=False,
                             out_stream=tout(), err_stream=terr())
            print("SUCCESS!")
        except (Failure, UnexpectedExit,):
            self.emailaddress = None
            print("FAILED! [Operation Failed]")
        except ParseError:
            self.emailaddress = None
            print("FAILED! [Operation cancelled by user]")


    @staticmethod
    def create_objs(project):
        settings_dict = get_settings('etc/tesserarius/roles.yaml')
        try:
            project_dict = settings_dict[project]
        except KeyError:
            raise RoleCreateError(
                "Config '{project}' not found.".format(project=project))

        roles = project_dict['roles']
        objs = list()
        for i in range (len(roles)):
            try:
                objs.append(BaseRole(name=roles[i]['name'],
                    stage=roles[i]['stage'],
                    permissions=roles[i]['permissions'],
                    title=roles[i]['title'],
                    add_permissions=roles[i]['addPermissions'],
                    remove_permissions=roles[i]['removePermissions'],
                    description=roles[i]['description']))

            except KeyError:
                raise RoleCreateError(
                    "Config '{project}' has invalid keys.".format(project=project))
        return objs
