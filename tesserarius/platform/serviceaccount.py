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

        extensions-<extension_name>-<role_name>

        short name for the service account describing its purpose.
        <role_name> pattern is defined in the tesserarius.serviceaccount

        Example: extensions-product-image_store, extensions-product-patroni_wale
        """
        name_pattern = r"platform-" + BASE_NAME_PATTERN
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
    def create_obj(project="platform"):
        return PlatformServiceAccount(base=BaseServiceAccount.create_obj(project))


@task
def create(ctx):
    '''
    Creates an IAM GCloud Service Account on rehive-core
    '''
    sa = PlatformServiceAccount.create_obj()
    sa.create(ctx)


@task
def update(ctx):
    '''
    Updates an IAM GCloud Service Account on rehive-core
    '''
    sa = PlatformServiceAccount.create_obj()
    sa.update(ctx)


@task
def delete(ctx):
    '''
    an IAM GCloud Service Account on rehive-core
    '''
    sa = PlatformServiceAccount.create_obj()
    sa.delete(ctx)

collection = Collection("serviceaccount")
collection.add_task(create, "create")
collection.add_task(update, "update")
collection.add_task(delete, "delete")
# collection.add_task(authorize_serviceaccount, "auth")
