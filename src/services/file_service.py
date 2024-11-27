import boto3
import uuid
from src.config.constants import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
    ALLOWED_EXTENSIONS
)
from src.models.file import File
from src.utils.db import db
from src.utils.exceptions import ValidationError

class FileService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.bucket_name = S3_BUCKET_NAME

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def upload_file(self, file_obj, user_id, chat_id=None):
        if not self.allowed_file(file_obj.filename):
            raise ValidationError(f"File type not allowed. Supported types: {ALLOWED_EXTENSIONS}")

        # Generate unique filename
        file_extension = file_obj.filename.rsplit('.', 1)[1].lower()
        s3_key = f"uploads/{user_id}/{str(uuid.uuid4())}.{file_extension}"

        # Upload to S3
        try:
            self.s3.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': file_obj.content_type}
            )
        except Exception as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")

        # Create file record in database
        file_record = File(
            file_name=file_obj.filename,
            file_type=file_extension,
            file_size=file_obj.content_length,
            s3_key=s3_key,
            user_id=user_id
        )

        db.session.add(file_record)
        db.session.commit()

        return file_record

    def get_file_url(self, file_id, user_id):
        file_record = File.query.filter_by(file_id=file_id, user_id=user_id).first()
        if not file_record:
            raise ValidationError("File not found or access denied")

        # Generate presigned URL
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_record.s3_key
                },
                ExpiresIn=3600  # URL expires in 1 hour
            )
            return url
        except Exception as e:
            raise Exception(f"Failed to generate file URL: {str(e)}")

    def delete_file(self, file_id, user_id):
        file_record = File.query.filter_by(file_id=file_id, user_id=user_id).first()
        if not file_record:
            raise ValidationError("File not found or access denied")

        # Delete from S3
        try:
            self.s3.delete_object(
                Bucket=self.bucket_name,
                Key=file_record.s3_key
            )
        except Exception as e:
            raise Exception(f"Failed to delete file from S3: {str(e)}")

        # Delete database record
        db.session.delete(file_record)
        db.session.commit()