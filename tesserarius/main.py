import pkg_resources

from invoke import Argument, Collection, Program
from tesserarius.tasks import collection
from tesserarius.extensions import collection as extensions_collection
from tesserarius.platform import collection as platform_collection


namespace = Collection()
namespace.add_collection(extensions_collection)
namespace.add_collection(platform_collection)
namespace.add_collection(collection)

class MainProgram(Program):
    def core_args(self):
        core_args = super(MainProgram, self).core_args()
        extra_args = [
            Argument(names=('project', 'n'), help="The project/package name being build"),
        ]
        return core_args + extra_args

version = pkg_resources.get_distribution("tesserarius").version
program = MainProgram(namespace=namespace, version=version)
