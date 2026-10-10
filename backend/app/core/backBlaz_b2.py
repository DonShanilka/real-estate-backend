from b2sdk.v2 import InMemoryAccountInfo, B2Api

from app.core.config import B2_APPLICATION_KEY, B2_BUCKET_NAME, B2_KEY_ID

info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", B2_KEY_ID, B2_APPLICATION_KEY)
bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
