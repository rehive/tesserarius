from invoke import Collection, task
from invoke.exceptions import ParseError
from tesserarius.utils import get_gcloud_wide_flags, get_settings


@task
def bind(ctx):
    """Add IAM policy binding in rehive-services"""
    settings_dict = get_settings()
    bindings_list = settings_dict["platform"]["bindings"]

    try:
        for bindings in bindings_list:
            role = "--role=" + bindings["role"]
            members = " ".join(["--member=" + m for m in bindings["members"]])

            command = "gcloud projects add-iam-policy-binding rehive-core "\
                " {members_args} {role_arg}"

            ctx.run(command.format(members_args=members, role_arg=role),
                    echo=True)
    except KeyError:
        raise ParseError("Invalid fields")

