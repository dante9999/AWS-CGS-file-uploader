
# Contents of the module

The code consists of three classes:  **CloudUploader** , **S3Uploader**, and **GCSUploader**. There is also a **FileUploader class** that acts as a wrapper and manages the upload process using the CloudUploader subclasses.


## CloudUploader (Abstract Base Class)
An abstract base class that defines the interface for uploading files to a cloud service. It has two abstract methods:

- **__init__(self, bucket_name, credentials_file)**: Initializes the uploader with the name of the cloud storage bucket and the path to the credentials file needed to access the cloud service.
- **upload_file(self, file_path)**: Uploads the file at the specified path to the cloud storage bucket.

## S3Uploader (Concrete CloudUploader subclass)
A concrete subclass of CloudUploader that implements the upload_file method for Amazon S3 cloud storage. It has the following methods:

- **__init__(self, bucket_name, credentials_file)**: Initializes the S3Uploader with the name of the S3 bucket and the path to the credentials file.
- **read_credentials(self, credentials_file)**: Reads the AWS access key ID and secret access key from the specified credentials file.
- **upload_file(self, file_path)**: Uploads the file at the specified path to the S3 bucket.
- **upload_files_single_call(self, file_path_list)**: An experimental method that attempts to upload multiple files to the S3 bucket in a single API call. This method is not yet ready to be used.
## GCSUploader (Concrete CloudUploader subclass)
A concrete subclass of CloudUploader that implements the upload_file method for Google Cloud Storage. It has the following methods:

- **__init__(self, bucket_name, credentials_file)**: Initializes the GCSUploader with the name of the GCS bucket and the path to the credentials file.
- **upload_file(self, file_path)**: Uploads the file at the specified path to the GCS bucket.
## FileUploader
A class that uploads files to cloud storage using S3Uploader and GCSUploader objects. It has the following methods:

- **__init__(self, directory_path, config_file, upload_file_types)**: Initializes the FileUploader with the path to the local directory containing the files to upload, the path to the JSON configuration file specifying the cloud storage settings, and a dictionary mapping cloud storage keys to lists of supported file extensions for each cloud storage service.
- **get_file_ext(self, cloud_service_key)**: Retrieves the list of file extensions supported for a given cloud storage service from the upload_file_types dictionary.
-**upload_files(self)**: Uploads all files in the local directory to the specified cloud storage services using the appropriate uploaders based on the file type and supported file extensions.

Note that the upload_files_single_call method of the S3Uploader class is still in progress and not yet ready to be used.
