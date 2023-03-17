
## file_uploader module
### About

file_uploader is a Python module that reads files from a directory and its subdirectories and uploads them to cloud storage services. It currently supports uploading media files (images and videos) to AWS S3 and documents (PDFs and Word documents) to Google Cloud Storage. The module is configurable and allows customizing the types of files to be uploaded to each cloud service.

### Installation
##### Always _Keep the required files in the same directory_
### How to Use
There are two ways to use the module:
1. Download the source code 'file_uploader.py' and install the required dependencies using pip:

    ```sh
    pip install -r requirements.txt
    ```
2. Install the module from the wheel file 'file_uploader-0.1-py3-none-any.whl':

    ```sh
    pip install file_uploader-0.1-py3-none-any.whl
    ```
    After the whl file is installed,the module can be imported directly in python scripts with
    ```sh
    import file_uploader
    ```
### Usage
To use the FileUploader class, you need to create an instance of it by passing the following parameters:

- directory_path: the path to the directory containing the files to upload in raw string.
- config_file: the name of the JSON configuration file that contains the cloud storage service and file type information.
- upload_file_types (optional): a dictionary that overrides the default file types to upload to each cloud service.
    - 'upload_file_types' accepts, where the tuples accept str of 'image','media' or 'document'
        ```sh
        {'s3': ('image', 'media'), 'gcs': ('document',)}
        ```
    
### Configuring the JSON file
The configuration file must have the following structure:
```sh
{
    "file_types": {
        "image": ["jpg", "png", "svg", "webp"],
        "media": ["mp3", "mp4", "mpeg4", "wmv", "3gp", "webm", "avi"],
        "document": ["doc", "docx", "csv", "pdf"]
    },

    "cloud_services": {
        "s3": {
            "bucket_name": "my-aws-bucket",
            "credentials_file": "key.csv"
        },
        "gcs": {
            "bucket_name": "my-gcs-bucket",
            "credentials_file": "key.json"
        }
    }
}
```
The contents of the 'config.json' file should contain a dictionary containing various types of files with their extensions and a dictionary containing cloud service information for AWS S3 or Google Cloud Storage. For each cloud storage account, the 'bucket_name' and 'credentials_file' must be specified. Credentials file can be downloaded from cloud storage account (csv for S3, json for GCS).
- refer to files provided
    - s3_key.csv
    - gcs_key.json

All the Credentials file should be kept in same directory as the script or file path of these should be entered in the 'config.json' file in raw string

Once an object of the FileUploader class is initialized, all files can be uploaded to their respective cloud storage by calling the upload_files() method:
```sh
uploader = FileUploader(r'c:\abc\directory_path', config_file='config.json')
uploader.upload_files()
```
##### GCSUploader and S3Uploader Classes

The GCSUploader and S3Uploader classes inherit from the CloudUploader abstract base class, which defines the interface for uploading files to cloud services. Both classes implement the abstract methods defined in the CloudUploader class:

```sh
class CloudUploader(ABC):
    @abstractmethod
    def __init__(self, bucket_name, credentials_file):
        pass

    @abstractmethod
    def upload_file(self, file_path):
        pass
```
The GCSUploader class is responsible for uploading files to Google Cloud Storage, and it takes two arguments:

- bucket_name: The name of the Google Cloud Storage bucket to which the files will be uploaded.
- credentials_path: The path to the Google Cloud Storage credentials file, in JSON format.

The S3Uploader class is responsible for uploading files to Amazon S3, and it takes two arguments:

- bucket_name: The name of the Amazon S3 bucket to which the files will be uploaded.
- credentials_path: The path to the Amazon S3 credentials file, in CSV format.
