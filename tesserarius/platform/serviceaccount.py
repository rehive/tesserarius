from tesserarius import task, Collection
from tesserarius.serviceaccount import BaseServiceAccount, BASE_NAME_PATTERN
from tesserarius.utils import get_gcloud_wide_flags, get_settings


class PlatformServiceAccount(BaseServiceAccount):
    project_id = "rehive-core"


    def __init__(self,
                 name=None,
                 display_name=None,
                 description=None,
                 base=None):
        """
        Checks if self.name has the correct naming convention

        platform-<role_name>

        short name for the service account describing its purpose.
        <role_name> pattern is defined in the tesserarius.serviceaccount

        Example: platform-staging, platform-media, platform-media-staging
        """
        name_pattern = r"platform({base})?".format(base=BASE_NAME_PATTERN)
        if name is not None and display_name is not None:
            super().__init__(name=name,
                  display_name=display_name,
                  description=description,
                  name_pattern=name_pattern)
            # discard base object
            base = None

        if base is not None and isinstance(base, BaseServiceAccount):
            super().__init__(name=base.name,
                  display_name=base.display_name,
                  description=base.description,
                  name_pattern=name_pattern)
        else:
            raise ServiceAccountCreateError(
                "Invalid arguments provided to create obj.")

        self._check_name()


    @staticmethod
    def create_objs(project="platform"):
        base_objs = BaseServiceAccount.create_objs(project)
        return [PlatformServiceAccount(base=b) for b in base_objs]


@task
def create(ctx):
    '''
    Creates an IAM GCloud Service Account on rehive-core
    '''
    for sa in PlatformServiceAccount.create_objs():
        sa.create(ctx)


@task
def update(ctx):
    '''
    Updates an IAM GCloud Service Account on rehive-core
    '''
    for sa in PlatformServiceAccount.create_objs():
        sa.update(ctx)


@task
def delete(ctx):
    '''
    an IAM GCloud Service Account on rehive-core
    '''
    for sa in PlatformServiceAccount.create_objs():
        sa.delete(ctx)

collection = Collection("serviceaccount")
collection.add_task(create, "create")
collection.add_task(update, "update")
collection.add_task(delete, "delete")
# collection.add_task(authorize_serviceaccount, "auth")
