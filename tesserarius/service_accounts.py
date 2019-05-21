from tesserarius.utils import get_gcloud_wide_flags, get_settings
from invoke import task, Collection
from invoke.exceptions import ParseError


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

    command += get_gcloud_wide_flags(config_dict, allow_type=False)
    ctx.run(command.format(
        name=config_dict['serviceAccount']['name']),
        echo=True)


@task
def authorize_serviceaccount(ctx, config):
    '''
    Creates an IAM GCloud Service Account
    '''
    sa = ctx["serviceAccount"]
    settings_dict = get_settings()
    config_dict = settings_dict[config]
    command = "gcloud auth activate-service-account"\
        " {name}@{project}.iam.gserviceaccount.com"\
        " --key-file={keyfile}"

    command += get_gcloud_wide_flags(config_dict, allow_type=False)

    ctx.run(command.format(
        name=config_dict['serviceAccount']['name'],
        project=config_dict['gcloud']['project'],
        key_file=config_dict['serviceAccount']['keyFile']),
        echo=True)

collection = Collection("serviceaccount")
collection.add_task(create_serviceaccount, "create")
# collection.add_task(authorize_serviceaccount, "auth")
