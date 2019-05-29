from invoke import task
from invoke.exceptions import ParseError
from tesserarius.utils import get_gcloud_wide_flags, get_settings



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

