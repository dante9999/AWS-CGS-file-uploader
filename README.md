# AWS-CGS-file-uploader

About this project:
There are couple of files in a directory like images (jpg, png, svg, and webp), media (mp3, mp4, mpeg4, wmv, 3gp, and webm), and documents (doc, docx, csv, and pdf).
The module should read all the files from the directory and its subdirectory, upload all the images and media files to AWS S3, and all the documents to Google cloud storage.
file_uploader.py is a generic python module which can be utilized as per need.The types of files to transfer to S3 and google cloud storage are configurable.

How to use the module:
There are 2 ways of using this module.Recommended to run in virtual enviornment
1.	downloading the source 'file_uploader.py' file.
a.	open cmd on project folder install the dependencies in requirement file using.
•	-pip install -r requirements.txt

2.	Installing the whl file ‘file_uploader-0.1-py3-none-any.whl’
a.	open cmd on project folder install the dependencies in requirement file using.
•	pip install file-uploader-0.1-py3-none-any.whl
b.	after the whl file is installed,the module can be imported directly in python scripts with
•	import file_uploader


To use the classes and methods inside the file_uploader module, please refer below.
‘FileUploader’ class:

(method) def __init__(
self: Self@FileUploader,directory_path: directory_path as raw string,config_file: json config file name with ext,upload_file_types: Any = UPLOAD_FILE_TYPES
) -> None

UPLOAD_FILE_TYPES = {'s3': ('image', 'media'), 'gcs': ('document',)}
(constant) UPLOAD_FILE_TYPES: dict[str:tuple(str), Any]

upload_file_types can be customized by passing a dict of tuples in the format mentioned in UPLOAD_FILE_TYPES class var.

•	the config file is a json and contains the configuration info of the file uploads,that can be customised and should be present in the same dir. as the project
•	format of the config.json file
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
•	contents of config.json
o	"file_types": dict containing various types of files with extenston
o	"cloud_services": dict containing cloud services info
	S3/gcs(for aws s3/google cloud storage)
•	 "bucket_name": respective bucket names for cloud storage account
•	"credentials_file": can be downloaded from cloud storage account(.csv for s3,.json for gcs/refer to s3_key.csv,gcs_key.json)



Object of ‘FileUploader’ class can be initialized as follows:
•	uploader = FileUploader(r'directory_path',config_file='config.json')
o	directory path contains the files inside various sub_dirs to be uploaded
once the object in initialized,all files can be uploaded in respective cloud storage using:
•	uploader.upload_files()








