import csv
import os
import json
from abc import ABC, abstractmethod
import boto3
from google.cloud import storage
import google.api_core.exceptions



class CloudUploader(ABC):

    '''Define an abstract method called __init__ which takes in the arguments bucket_name and credentials_file
    .This method will be overridden in the subclass and will be used to initialize the cloud uploader
    '''
    @abstractmethod
    def __init__(self, bucket_name, credentials_file):
        pass
    
    '''Define an abstract method called upload_file which takes in the argument file_path.
    This method will be overridden in the subclass and will be used to upload the specified file to the cloud
    '''

    @abstractmethod
    def upload_file(self, file_path):
        pass
    
    
    

class S3Uploader(CloudUploader):
    '''Define a subclass of CloudUploader called S3Uploader'''

    
    def __init__(self, bucket_name, credentials_file):
        '''Define the constructor method which takes in the arguments bucket_name and credentials_file'''
        
        # Initialize the instance variables bucket_name and s3
        self.bucket_name = bucket_name
        self.access_key_id, self.secret_access_key = self.read_credentials(credentials_file)
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key
        )

    
    def read_credentials(self, credentials_file):
        '''Define a method called read_credentials which takes in the argument credentials_file'''
        
        try:
            # Open the credentials file and read its contents as a csv.DictReader object
            with open(credentials_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                for row in reader: # Loop through the rows of the csv.DictReader object
                    # Extract the access key id and secret access key from the current row
                    access_key_id = row.get('Access key ID')
                    secret_access_key = row.get('Secret access key')
                    
                    # Check if both the access key id and secret access key are present
                    if access_key_id and secret_access_key:
                        # Return the access key id and secret access key
                        return access_key_id, secret_access_key
                # If no access key id or secret access key is found in the credentials file, raise a ValueError
                raise ValueError("Credentials file is empty or missing access key ID/secret access key.")
        except Exception as e:
            # If there is an error reading the credentials file, raise an Exception
            raise Exception(f"Failed to read credentials from file: {e}")
            
            
    
    def upload_file(self, file_path):
        '''Define a method called upload_file that takes in the argument file_path 
        and uploads the specified file to AWS S3 bucket'''

        # Get the base name of the file from the file path
        s3_key = os.path.basename(file_path)

        try:
            # Use the AWS S3 client to upload the file to the specified bucket with the given s3_key
            self.s3.upload_file(file_path, self.bucket_name, s3_key)
            print(f"File '{s3_key}' uploaded successfully to S3 bucket: {self.bucket_name}")

        except Exception as e:
            # Print error message to console if file fails to upload
            print(f"Failed to upload '{s3_key}' to S3 bucket: {self.bucket_name}. Error: {e}")


        # Catch the boto3 S3UploadFailedError exception if it occurs
        except boto3.exceptions.S3UploadFailedError as e:
            '''if bucket error, credentials errors, raise an exception'''
            pass
        
        
    def upload_files_single_call(self, file_path_list):
        '''still in progress, not to be used'''

        try:
            objects = []
            # iterate through the list of file paths to upload and create a dictionary with the 'Key' and 'SourceFile' values
            for file_path in file_path_list:
                s3_key = file_path.split('/')[-1]
                objects.append({'Key': s3_key, 'SourceFile': file_path})

            # upload each file to the S3 bucket
            for obj in objects:
                self.s3.upload_file(
                    obj['SourceFile'], # file path to upload
                    self.bucket_name, # bucket name to upload to
                    obj['Key'], # key (name) of the uploaded file in the bucket
                    Config=boto3.s3.transfer.TransferConfig(multipart_threshold=1024 * 25, max_concurrency=10,
                                                             multipart_chunksize=1024 * 25, use_threads=True)
                )

            # print success message with the number of files uploaded and the name of the bucket
            print(f"{len(objects)} files uploaded successfully to S3 bucket:", self.bucket_name)

        # handle any exceptions that occur during the file upload process
        except Exception as e:
            print("Failed to upload files to S3 bucket:", self.bucket_name, "Error:", e)



        

class GCSUploader(CloudUploader):
    '''Define a subclass of CloudUploader called GCSUploader'''
    
    # Define the constructor method that initializes the GCSUploader object with the specified bucket_name and credentials_file
    def __init__(self, bucket_name, credentials_file):
        self.bucket_name = bucket_name
        
        # Try to read the Google Cloud Storage credentials from the given credentials_file
        try:
            self.gcs = storage.Client.from_service_account_json(credentials_file)
            # Print success message to console
            print("Successfully read credentials.")
            
        # If there's an error reading the credentials, raise an exception with the error message
        except Exception as e:
            raise Exception(f"Failed to read credentials file: {e}")
            
    # Define a method called upload_file which uploads the specified file to the GCS bucket
    def upload_file(self, file_path):
        
        # Get the GCS bucket from the GCS client
        bucket = self.gcs.bucket(self.bucket_name)
        
        # Get the base name of the file from the file path
        file_name=os.path.basename(file_path)
        
        # Get the GCS blob for the file
        blob = bucket.blob(file_name)
        
        try:
            # Upload the file to GCS using the GCS blob
            blob.upload_from_filename(file_path)
            # Print success message to console
            print(f"File {file_name} uploaded successfully to GCS bucket : {self.bucket_name}")
            
        # If the file is not found, raise an exception with an error message
        except google.api_core.exceptions.NotFound as e:
            raise Exception (f"Not found error.Stopping upload process")
            
        # If there's an error uploading the file, print the error message to console
        except Exception as e:
            print(f"Failed to upload file: {e}")
            
class FileUploader:
    
    # Define a class-level constant dictionary named UPLOAD_FILE_TYPES with some values for different cloud storage services
    UPLOAD_FILE_TYPES = {'s3': ('image', 'media'), 'gcs': ('document',)}
    
    # Define an initializer method that takes in the directory path, config file path, and an optional argument for upload file types, and sets them as instance attributes
    def __init__(self, directory_path, config_file, upload_file_types=UPLOAD_FILE_TYPES):
        self.directory_path = directory_path
        self.config_file = config_file
        self.upload_file_types = upload_file_types
        
        
        # Read the configuration from the file
        try:
            # Open the configuration file and load its content as JSON format
            with open(self.config_file) as f:
                self.config = json.load(f)

        # If the configuration file is not found, raise an exception
        except FileNotFoundError:
            raise Exception(f"Error: Config file '{self.config_file}' not found.")

        # If the configuration file is invalid in JSON format, raise an exception
        except json.JSONDecodeError:
            raise Exception(f"Error: Invalid JSON format in config file '{self.config_file}'.")

        # If the configuration file contains information about the 's3' cloud service
        if 's3' in self.config['cloud_services']:
            # Create an instance of the S3Uploader class using information from the configuration file
            self.s3_uploader = S3Uploader(
                self.config['cloud_services']['s3']['bucket_name'],
                self.config['cloud_services']['s3']['credentials_file']
            )
            # Get file extensions associated with the S3Uploader object
            self.s3_uploader_file_types = self.get_file_ext('s3')

        # If the configuration file contains information about the 'gcs' cloud service
        if 'gcs' in self.config['cloud_services']:
            # Create an instance of the GCSUploader class using information from the configuration file
            self.gcs_uploader = GCSUploader(
                self.config['cloud_services']['gcs']['bucket_name'],
                self.config['cloud_services']['gcs']['credentials_file']
            )
            # Get file extensions associated with the GCSUploader object
            self.gcs_uploader_file_types = self.get_file_ext('gcs')
            

            
    def get_file_ext(self, cloud_service_key):
        # Retrieve the list of file types associated with the specified cloud service key
        cloud_service = self.upload_file_types[cloud_service_key]
        file_ext_list = []

        # For each file type associated with the specified cloud service, check if it is defined in the config file
        for s in cloud_service:
            if s in self.config["file_types"]:
                # If it is defined, add the file extensions to the list
                file_ext_list.extend(self.config["file_types"][s])
            else:
                # If it is not defined, print an error message and skip to the next file type
                print(f"'{s}' is not defined in 'file_types' in config file. Skipping '{s}'")

        return file_ext_list


    def upload_files(self):
        # Check if the directory exists
        if not os.path.isdir(self.directory_path):
            print(f"Error: Directory {self.directory_path} does not exist.")
            return

        # For each file in the directory, check if it is a file and retrieve its file type
        for subdir, _, files in os.walk(self.directory_path):
            for file in files:
                file_path = os.path.join(subdir, file)

                if not os.path.isfile(file_path):
                    # If it is not a file, print an error message and skip to the next file
                    print(f"Skipping {file_path}: not a file.")
                    continue

                file_type = file.split('.')[-1].lower()

                # Upload the file to S3 if the file type is supported and the S3 uploader is initialized
                if hasattr(self, 's3_uploader') and file_type in self.s3_uploader_file_types:
                    self.s3_uploader.upload_file(file_path)

                # Upload the file to GCS if the file type is supported and the GCS uploader is initialized
                if hasattr(self, 'gcs_uploader') and file_type in self.gcs_uploader_file_types:
                    self.gcs_uploader.upload_file(file_path)

