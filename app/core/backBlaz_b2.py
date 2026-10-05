from b2sdk.v2 import InMemoryAccountInfo, B2Api

# BACKBLAZE CREDENTIALS (Native B2 keys)
B2_KEY_ID = "f9f45a6c989e"
B2_APPLICATION_KEY = "005e5fd63c029f6129d55a451b23d74bd5c2357de1"
B2_BUCKET_NAME = "realEstate-Estate"


info = InMemoryAccountInfo()
b2_api = B2Api(info)

# authorize account (NO S3, PURE B2)
b2_api.authorize_account(
    "production",
    B2_KEY_ID,
    B2_APPLICATION_KEY
)

bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
