from invoke import Collection
from tesserarius.platform.serviceaccount import collection as sa_collection
from tesserarius.platform.roles import collection as roles_collection
from tesserarius.platform.tasks import bind

collection = Collection("platform")
collection.add_task(bind, "bind")
collection.add_collection(sa_collection, "serviceaccount")
collection.add_collection(roles_collection, "roles")
