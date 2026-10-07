import uuid
import os
from fastapi import UploadFile, HTTPException

from app.core.backBlaz_b2 import bucket, B2_BUCKET_NAME


async def upload_file(file: UploadFile, folder: str):

    try:
        file_ext = file.filename.split(".")[-1]

        file_name = f"{folder}/{uuid.uuid4()}.{file_ext}"

        # save temporarily
        temp_path = f"/tmp/{uuid.uuid4()}.{file_ext}"

        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        # upload to Backblaze B2
        uploaded_file = bucket.upload_local_file(
            local_file=temp_path,
            file_name=file_name
        )

        # public URL (bucket must be public OR use signed URL)
        file_url = f"https://f000.backblazeb2.com/file/{B2_BUCKET_NAME}/{file_name}"

        # cleanup temp file
        os.remove(temp_path)

        return file_url

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )