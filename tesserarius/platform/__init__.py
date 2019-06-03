from tesserarius import Collection
from tesserarius.platform.serviceaccount import collection as sa_collection

collection = Collection("platform")
collection.add_collection(sa_collection, "serviceaccount")
