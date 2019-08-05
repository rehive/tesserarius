from invoke import Collection
from tesserarius.extensions.serviceaccount import collection as sa_collection
from tesserarius.extensions.roles import collection as roles_collection
from tesserarius.extensions.tasks import bind

collection = Collection("extensions")
collection.add_task(bind, "bind")
collection.add_collection(sa_collection, "serviceaccount")
collection.add_collection(roles_collection, "roles")
