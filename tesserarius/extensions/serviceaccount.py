from tesserarius import task, Collection
from tesserarius.serviceaccount import BaseServiceAccount
from tesserarius.utils import get_gcloud_wide_flags, get_settings


class ExtensionsServiceAccount(BaseServiceAccount):
    project_id = None

    def __init__(self, name, display_name):
        self.name = name


@task
def create_serviceaccount(ctx, config):
    '''
    Creates an IAM GCloud Service Account
    '''
    settings_dict = get_settings()
    config_dict = settings_dict[config]
    command = "gcloud iam service-accounts create {name}"

    try:
        command += " --display-name {display_name}".format(
            display_name=config_dict['serviceAccount']['displayName'])
    except KeyError:
        pass

    ctx.run(command.format(
        name=config_dict['serviceAccount']['name']),
        echo=True)

collection = Collection("serviceaccount")
collection.add_task(create_serviceaccount, "create")
# collection.add_task(authorize_serviceaccount, "auth")
