from invoke import task, Collection
from tesserarius.roles import BaseRole, RoleCreateError
from tesserarius.utils import get_gcloud_wide_flags, get_settings


class PlatformRole(BaseRole):
    project_id = "rehive-core"


    def __init__(self, name=None, title="", stage=None,
                 description=None, permissions=None,
                 add_permissions=None, remove_permissions=None, base=None):
        """
        Example: service-product-media, service-product-pgbackup-staging
        """
        if name is not None:
            super().__init__(name=name,
                    stage=stage,
                    permissions=permissions,
                    title=title,
                    add_permissions=add_permissions,
                    remove_permissions=remove_permissions,
                    description=description)
            # discard base object
            base = None

        if base is not None and isinstance(base, BaseRole):
            super().__init__(name=base.name,
                    stage=base.stage,
                    permissions=base.permissions,
                    title=base.title,
                    add_permissions=base.add_permissions,
                    remove_permissions=base.remove_permissions,
                    description=base.description)
        else:
            raise RoleCreateError("Invalid arguments provided to create obj.")


    @staticmethod
    def create_objs(project="extensions"):
        base_objs = BaseRole.create_objs(project)
        return [PlatformRole(base=b) for b in base_objs]


@task
def create(ctx):
    '''
    Creates an Google Cloud IAM Role on rehive-core
    '''
    for sa in PlatformRole.create_objs():
        sa.create(ctx)


@task
def update(ctx):
    '''
    Updates an Google Cloud IAM Role on rehive-core
    '''
    for sa in PlatformRole.create_objs():
        sa.update(ctx)


@task
def delete(ctx):
    '''
    Deletes an Google Cloud IAM Role on rehive-core
    '''
    for sa in PlatformRole.create_objs():
        sa.delete(ctx)

collection = Collection("roles")
collection.add_task(create, "create")
collection.add_task(update, "update")
collection.add_task(delete, "delete")
# collection.add_task(authorize_serviceaccount, "auth")
