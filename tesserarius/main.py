import pkg_resources
from invoke import Argument, Collection, Program

import tesserarius


class MainProgram(Program):
    def core_args(self):
        core_args = super(MainProgram, self).core_args()
        extra_args = [
            Argument(names=('project', 'n'), help="The project/package name being build"),
        ]
        return core_args + extra_args

namespace = Collection()
namespace.add_collection(tesserarius.extensions.collection)

version = pkg_resources.get_distribution("tesserarius").version
program = MainProgram(namespace=namespace, version=version)
