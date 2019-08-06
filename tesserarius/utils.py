import os
from distutils.util import strtobool
from invoke.exceptions import ParseError

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

def get_path():
    """
    Get the full path name
    """
    file_path = os.path.dirname(os.path.realpath(__file__))
    root_path = os.path.dirname(os.path.dirname(file_path))
    return root_path


def task_template(cls, method, args, **kwargs):
    """
    Task template for generic tasks
    """
    for sa in cls.create_objs():
        for attrib, value in kwargs.items():
            if value is None:
                getattr(sa, method)(*args)
            elif getattr(sa, attrib) == value:
                getattr(sa, method)(*args)


def format_yaml(template, config):
    """
    Replace in ${ENV_VAR} in template with value
    """
    formatted = template
    for k, v in config.items():
        formatted = formatted.replace('${%s}' % k, v)
    return formatted


def get_error_stream():
    path = 'var/tesserarius/error.log'
    return open(path, 'a+')


def get_out_stream():
    path = 'var/tesserarius/out.log'
    return open(path, 'a+')


def get_settings(path='etc/tesserarius/tesserarius.yaml'):
    """
    Import project settings
    """
    with open(path, 'r') as stream:
        settings_dict = yaml.load(stream, Loader=Loader)

    return settings_dict


def get_gcloud_wide_flags(config_dict, allow_type=True):
    """
    Fetches the project information
    """
    cluster_type = ""
    if allow_type:
        try:
            cluster_type = '--zone {}'.format(config_dict['gcloud']['zone'])
        except KeyError:
            try:
                cluster_type = '--region {}'.format(config_dict['gcloud']['region'])
            except KeyError:
                raise ParseError("Couldn't load zonal or regional cluster info")

    return " --project {project} {cluster_type}".format(
        project=config_dict['gcloud']['project'],
        cluster_type=cluster_type)


def confirm(prompt='Continue?\n', failure_prompt='User cancelled task'):
    """
    Prompt the user to continue. Repeat on unknown response.
    Raise ParseError on negative response
    """
    response = input(prompt)
    response_bool = False

    try:
        response_bool = strtobool(response)
    except ValueError:
        print('Unkown Response. Confirm with y, yes, t, true, on or 1; cancel with n, no, f, false, off or 0.')
        return confirm(prompt, failure_prompt)

    if not response_bool:
        raise ParseError(failure_prompt)

    return response_bool
