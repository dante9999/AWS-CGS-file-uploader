
# Running unittests

Unittest module is in  **test_file_uploader.py**.

Make sure to install the required dependencies for testing using pip:

```sh
pip install pytest
```

To run the tests, execute the following command in the terminal from the directory containing both **file_uploader.py** and **test_file_uploader.py**:

```sh
pytest test_file_uploader.py
```

# Documentation of **test_file_uploader.py**

This code defines a series of unit tests for a **FileUploader** module using the pytest framework. The module has a class hierarchy with a base class **CloudUploader** and its subclasses **S3Uploader** and **GCSUploader**. The FileUploader class manages these cloud uploader instances and uploads files based on their extensions.

### Test functions 
1.	**test_clouduploader_abstract_methods()**: This test checks if the CloudUploader base class raises a TypeError when trying to instantiate it directly, ensuring that it is an abstract base class.
2.	**test_s3uploader_init()**: This test checks if the S3Uploader class initializes properly, setting the bucket name and creating an S3 client using the boto3 library.
3.	**test_s3uploader_read_credentials()**: This test checks if the S3Uploader class correctly reads AWS access key ID and secret access key from a given CSV file.
4.	**test_s3uploader_upload_file()**: This test checks if the S3Uploader class uploads a file to the specified S3 bucket using the upload_file method from the boto3 library.
5.	**test_gcsuploader_init()**: This test checks if the GCSUploader class initializes properly, setting the bucket name and creating a GCS client using the google-cloud-storage library.
6.	**test_gcsuploader_upload_file()**: This test checks if the GCSUploader class uploads a file to the specified GCS bucket using the upload_from_filename method from the google-cloud-storage library.
7.	**test_fileuploader_init()**: This test checks if the FileUploader class initializes properly, setting the directory path, config file, and creating instances of S3Uploader and GCSUploader.
8.	**test_fileuploader_get_file_ext()**: This test checks if the FileUploader class returns the correct file extensions for each cloud service based on the configuration.
9.	**test_fileuploader_upload_files()**: This test checks if the FileUploader class uploads files to the correct cloud service based on their file extensions.
