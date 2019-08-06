from invoke import Collection, task
from invoke.exceptions import ParseError
from tesserarius.utils import get_gcloud_wide_flags, get_settings


@task
def set_cluster(ctx, config):
    """Sets the active cluster"""
    settings_dict = get_settings()
    config_dict = settings_dict[config]
    command = "gcloud container clusters get-credentials {cluster}"\
        + get_gcloud_wide_flags(config_dict)

    ctx.run(command.format(
        cluster=config_dict['kubernetes']['cluster']),
        echo=True)

collection = Collection("cluster")
collection.add_task(set_cluster, "set")
