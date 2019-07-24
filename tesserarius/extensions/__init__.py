from invoke import Collection
from tesserarius.extensions.serviceaccount import collection as sa_collection
from tesserarius.extensions.roles import collection as roles_collection

collection = Collection("extensions")
collection.add_collection(sa_collection, "serviceaccount")
collection.add_collection(roles_collection, "roles")
