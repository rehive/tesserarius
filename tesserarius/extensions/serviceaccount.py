from invoke import task, Collection
from tesserarius.serviceaccount import \
    BaseServiceAccount, ServiceAccountCreateError, BASE_NAME_PATTERN
from tesserarius.utils import get_gcloud_wide_flags, \
    get_settings, task_template


class ExtensionsServiceAccount(BaseServiceAccount):
    project_id = "rehive-services"

    def __init__(self,
                 name=None,
                 display_name=None,
                 description=None,
                 role=None,
                 base=None):
        """
        Checks if self.name has the correct naming convention

        <service-name>(-<role_name>)?

        short name for the service account describing its purpose.
        <role_name> pattern is defined in the tesserarius.serviceaccount

        Example: service-product-media, service-product-staging-pgbackup
        """
        service_name = r'[a-z]{3,10}(_[a-z]{3,10}){,2}'
        name_pattern = rf"({BASE_NAME_PATTERN})?-{service_name}$"
        if name is not None and display_name is not None:
            super().__init__(name=name,
                  display_name=display_name,
                  description=description,
                  role=role,
                  name_pattern=name_pattern)
            # discard base object
            base = None

        if base is not None and isinstance(base, BaseServiceAccount):
            super().__init__(name=base.name,
                  display_name=base.display_name,
                  description=base.description,
                  role=base.role,
                  name_pattern=name_pattern,
                  environment=base.environment,
                  environment_settings=base.environment_settings)
        else:
            raise ServiceAccountCreateError(
                "Invalid arguments provided to create obj.")

        self._check_name()


    @staticmethod
    def create_objs(project="extensions"):
        base_objs = BaseServiceAccount.create_objs(project)
        return [ExtensionsServiceAccount(base=b) for b in base_objs]


@task(help={
    "name" : "The name of the service account to handle",
})
def create(ctx, name=None):
    '''
    Creates a Google Cloud IAM Service Account on rehive-services
    '''
    task_template(ExtensionsServiceAccount, "create", [ctx,], name=name)


@task(help={
    "name" : "The name of the service account to handle",
})
def delete(ctx, name=None):
    '''
    Deletes a Google Cloud IAM Service Account on rehive-services
    '''
    task_template(ExtensionsServiceAccount, "delete", [ctx,], name=name)


@task(help={
    "name": "The name of the service account to handle",
})
def update(ctx, name=None):
    '''
    Updates a Google Cloud IAM Service Account on rehive-services
    '''
    task_template(ExtensionsServiceAccount, "update", [ctx,], name=name)


@task(help={
    "name": "The name of the service account to upload",
    "secret": "The kubernetes secret name to upload the private key",
})
def upload(ctx, name=None, secret="google-credentials"):
    '''
    Uploads a Google Cloud IAM Service Account private key to
    k8s namespace as a generic secret on rehive-services
    '''
    task_template(ExtensionsServiceAccount, "upload",
                  [ctx, secret,], name=name)


@task(help={
    "name" : "The name of the service account to handle",
})
def bind(ctx, name=None):
    '''
    Binds a Google Cloud IAM Service Account on rehive-services
    '''
    task_template(ExtensionsServiceAccount, "bind", [ctx,], name=name)


@task(help={
    "name" : "The name of the service account to handle",
    "bucket" : "The GCS bucket the service account should own",
})
def chown(ctx, name, bucket):
    '''
    Changes ownership of a GCS bucket to an IAM service account on rehive-services
    '''
    task_template(ExtensionsServiceAccount, "chown", [ctx, bucket,], name=name)


collection = Collection("serviceaccount")
collection.add_task(bind, "bind")
collection.add_task(chown, "chown")
collection.add_task(create, "create")
collection.add_task(delete, "delete")
collection.add_task(update, "update")
collection.add_task(upload, "upload")
# collection.add_task(authorize_serviceaccount, "auth")
