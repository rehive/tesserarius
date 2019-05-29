from invoke import Collection
from .serviceaccount import collection as sa_collection

collection = Collection("extensions")
collection.add_collection(sa_collection, "serviceaccount")
# collection.add_task(authorize_serviceaccount, "auth")

