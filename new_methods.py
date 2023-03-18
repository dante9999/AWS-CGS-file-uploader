class S3Uploader(CloudUploader):
    # ... existing code ...

    def upload_large_file(self, file_path):
        s3_key = os.path.basename(file_path)
        try:
            file_size = os.path.getsize(file_path)
            # Use multipart upload for large files
            print(f"Uploading large file '{s3_key}' using multipart upload.")
            response = self.s3.create_multipart_upload(Bucket=self.bucket_name, Key=s3_key)
            upload_id = response['UploadId']
            parts = []
            with open(file_path, 'rb') as file:
                part_number = 1
                num_parts = int(math.ceil(file_size / self.multipart_chunksize))
                for chunk in iter(lambda: file.read(self.multipart_chunksize), b''):
                    response = self.s3.upload_part(
                        Body=chunk,
                        Bucket=self.bucket_name,
                        Key=s3_key,
                        PartNumber=part_number,
                        UploadId=upload_id
                    )
                    parts.append({'ETag': response['ETag'], 'PartNumber': part_number})
                    part_number += 1
            response = self.s3.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=s3_key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            print(f"File '{s3_key}' uploaded successfully to S3 bucket: {self.bucket_name}")
        except Exception as e:
            print(f"Failed to upload large file '{s3_key}' to S3 bucket: {self.bucket_name}. Error: {e}")
        
class GCSUploader(CloudUploader):
    # ... existing code ...

    def upload_large_file(self, file_path):
        file_name = os.path.basename(file_path)
        try:
            blob = self.gcs.bucket(self.bucket_name).blob(file_name)
            print(f"Uploading large file '{file_name}' using resumable upload.")
            with open(file_path, 'rb') as f:
                upload = blob.resumable_upload(f, chunk_size=self.chunk_size)
                upload.consume_next_chunk()  # start the upload
                while not upload.finished:
                    upload.consume_next_chunk()
                    print(f"Uploaded {upload.progress()}% of '{file_name}' to GCS bucket: {self.bucket_name}")
            print(f"File '{file_name}' uploaded successfully to GCS bucket: {self.bucket_name}")
        except google.api_core.exceptions.NotFound as e:
            print(f"Not found error while uploading large file '{file_name}' to GCS bucket: {self.bucket_name}. Stopping upload process.")
        except Exception as e:
            print(f"Failed to upload large file '{file_name}' to GCS bucket: {self.bucket_name}. Error: {e}")


class FileUploader:
    UPLOAD_FILE_TYPES = {'s3': ('image', 'media'), 'gcs': ('document',)}

    def __init__(self, directory_path, config_file, upload_file_types=UPLOAD_FILE_TYPES):
        # ... existing code ...

        # Initialize the uploaders for each cloud provider
        if 's3' in self.config['cloud_services']:
            self.s3_uploader = S3Uploader(self.config['cloud_services']['s3']['bucket_name'],
                                          self.config['cloud_services']['s3']['credentials_file'])
            self.s3_uploader_file_types = self.get_file_ext('s3')
        if 'gcs' in self.config['cloud_services']:
            self.gcs_uploader = GCSUploader(self.config['cloud_services']['gcs']['bucket_name'],
                                            self.config['cloud_services']['gcs']['credentials_file'])
            self.gcs_uploader_file_types = self.get_file_ext('gcs')

    def upload_files(self):
        if not os.path.isdir(self.directory_path):
            print(f"Error: Directory {self.directory_path} does not exist.")
            return

        for subdir, _, files in os.walk(self.directory_path):
            for file in files:
                file_path = os.path.join(subdir, file)

                if not os.path.isfile(file_path):
                    print(f"Skipping {file_path}: not a file.")
                    continue

                file_type = file.split('.')[-1].lower()

                # Upload the file to S3 if the file type is supported and the S3 uploader is initialized
                if hasattr(self, 's3_uploader') and file_type in self.s3_uploader_file_types:
                    if os.path.getsize(file_path) > self.s3_uploader.multipart_threshold:
                        self.s3_uploader.upload_large_file(file_path)
                    else:
                        self.s3_uploader.upload_small_file(file_path)

                # Upload the file to GCS if the file type is supported and the GCS uploader is initialized
                if hasattr(self, 'gcs_uploader') and file_type in self.gcs_uploader_file_types:
                    if os.path.getsize(file_path) > self.gcs_uploader.chunk_size:
                        self.gcs_uploader.upload_large_file(file_path)
                    else:
                        self.gcs_uploader.upload_small_file(file_path)

