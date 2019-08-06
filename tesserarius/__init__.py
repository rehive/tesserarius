__version__ = '0.0.2-rc.1'
__url__ = 'https://github.com/rehive/tesserarius',
__author__ = 'Mwangi'
__email__ = 'info@rehive.com'
__license__ = 'MIT License'


from invoke import Collection
from tesserarius.tasks import collection
from tesserarius.extensions import collection as extensions_collection
from tesserarius.platform import collection as platform_collection


namespace = Collection()
namespace.add_collection(extensions_collection)
namespace.add_collection(platform_collection)
namespace.add_collection(collection)
