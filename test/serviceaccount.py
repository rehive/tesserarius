from tesserarius.extensions.serviceaccount import ExtensionsServiceAccount as esa
from tesserarius.platform.serviceaccount import PlatformServiceAccount as psa


def extensions_create_obj():
    sa = esa.create_obj()


def platform_create_obj():
    sa = psa.create_obj()


def main():
    extensions_create_obj()
    platform_create_obj()


if __name__ == "__main__":
    main()

