from tesserarius import Collection
from tesserarius.extensions.serviceaccount import collection as sa_collection

collection = Collection("extensions")
collection.add_collection(sa_collection, "serviceaccount")
