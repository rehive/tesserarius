from re import match


class ServiceAccountValidationError(Exception):
    pass


class BaseServiceAccount():
    project_id = None
    name = None
    emailaddress = None
    display_name = ""
    description = ""
    _role_name_regex = r"[a-z_]"
    _name_regex = None


    def __init__(self, name, display_name="", description=""):
        # Check name

        self._name_regex = self._role_name_regex
        self.name = name
        self.display_name = display_name
        self.description = description


    def __str__(self):
        return "account_name: {name}, display_name: {display_name}, " \
                "project_id: {project_id}, " \
                "description: {description}".format(
                    name=self.name,
                    display_name=self.display_name,
                    project_id=self.project_id,
                    description=self.description
                )


    def _check_name(self):
        """
        Checks if self.name has the correct naming convention

        <role_name>

        short name for the service account describing its purpose.
        Example: image_store, patroni_wale, walebackups
        """
        if not match(r"^{}*$".format(self._name_regex), self.name):
            raise ServiceAccountValidationError("Invalid account name.")
