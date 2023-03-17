# Import necessary libraries and modules
import json
import os
import tempfile
from unittest.mock import MagicMock, patch
import pytest

from file_uploader import CloudUploader, S3Uploader, GCSUploader, FileUploader

# Test if CloudUploader is an abstract base class
def test_clouduploader_abstract_methods():
    # Check if instantiating CloudUploader directly raises a TypeError
    with pytest.raises(TypeError):
        cloud_uploader = CloudUploader('bucket_name', 'credentials_file')

# Test S3Uploader initialization
def test_s3uploader_init():
    # Mock the boto3 library
    with patch('file_uploader.boto3') as mock_boto3:
        # Create an S3Uploader instance and check if the bucket name is set correctly
        s3_uploader = S3Uploader('test_bucket', 'test_credentials.csv')
        assert s3_uploader.bucket_name == 'test_bucket'
        # Check if the S3 client is created using the boto3 library
        mock_boto3.client.assert_called_once()

# Test S3Uploader reading AWS credentials from a CSV file
def test_s3uploader_read_credentials():
    # Create a temporary file to store the test CSV data
    with tempfile.NamedTemporaryFile('w', newline='', delete=False) as f:
        f.write('Access key ID,Secret access key\n')
        f.write('test_access_key,test_secret_key\n')
        f.flush()

        # Mock the boto3 library
        with patch('file_uploader.boto3') as mock_boto3:
            # Create an S3Uploader instance and check if the access_key_id and secret_access_key are set correctly
            s3_uploader = S3Uploader('test_bucket', f.name)
            assert s3_uploader.access_key_id == 'test_access_key'
            assert s3_uploader.secret_access_key == 'test_secret_key'

    # Clean up the temporary file
    os.remove(f.name)

# Test S3Uploader uploading a file to an S3 bucket
def test_s3uploader_upload_file():
    # Mock the boto3 library
    with patch('file_uploader.boto3') as mock_boto3:
        # Create an S3Uploader instance
        s3_uploader = S3Uploader('test_bucket', 'test_credentials.csv')
        # Mock the os library
        with patch('file_uploader.os') as mock_os:
            # Set the return value of os.path.basename()
            mock_os.path.basename.return_value = 'test_file'
            # Call the upload_file method and check if the upload_file method from boto3 is called with the correct arguments
            s3_uploader.upload_file('test_file_path')
            mock_boto3.client().upload_file.assert_called_once_with('test_file_path', 'test_bucket', 'test_file')

# Test GCSUploader initialization
def test_gcsuploader_init():
    # Create a temporary file to store the test JSON data
    with tempfile.NamedTemporaryFile('w', newline='', delete=False) as f:
        f.write('{"test_key": "test_value"}\n')
        f.flush()

        # Mock the google-cloud-storage library
        with patch('file_uploader.storage') as mock_storage:
            # Create a GCSUploader instance and check if the bucket name is set correctly
            gcs_uploader = GCSUploader('test_bucket', f.name)
            assert gcs_uploader.bucket_name == 'test_bucket'
            # Check if the GCS client is created using the google-cloud-storage library
            mock_storage.Client.from_service_account_json.assert_called_once_with(f.name)

    # Clean up the temporary file
    os.remove(f.name)

# Test GCSUploader uploading a file to a GCS bucket
def test_gcsuploader_upload_file():
    # Create a temporary file to store the test JSON data
    with tempfile.NamedTemporaryFile('w', newline='', delete=False) as f:
        f.write('{"test_key": "test_value"}\n')
        f.flush()

        # Mock the google-cloud-storage library
        with patch('file_uploader.storage') as mock_storage:
            # Create a GCSUploader instance
            gcs_uploader = GCSUploader('test_bucket', f.name)
            # Mock the os library
            with patch('file_uploader.os') as mock_os:
                # Set the return value of os.path.basename()
                mock_os.path.basename.return_value = 'test_file'
                # Mock the Blob object
                mock_blob = MagicMock()
                # Set the return value of the bucket().blob() method from the google-cloud-storage library
                mock_storage.Client().bucket().blob.return_value = mock_blob
                # Call the upload_file method and check if the upload_from_filename method from the google-cloud-storage library is called
                gcs_uploader.upload_file('test_file_path')
                mock_blob.upload_from_filename.assert_called_once_with('test_file_path')

    # Clean up the temporary file
    os.remove(f.name)

# Test FileUploader initialization
def test_fileuploader_init():
    # Mock the S3Uploader and GCSUploader classes
    with patch('file_uploader.S3Uploader'), patch('file_uploader.GCSUploader'):
        # Create a temporary file to store the test JSON data for FileUploader configuration
        with tempfile.NamedTemporaryFile('w', newline='', delete=False) as f:
            f.write('{"cloud_services": {"s3": {"bucket_name": "test_s3_bucket", "credentials_file": "test_s3_credentials.csv"}, "gcs": {"bucket_name": "test_gcs_bucket", "credentials_file": "test_gcs_credentials.json"}}, "file_types": {"image": ["jpg", "png"], "media": ["mp4"], "document": ["pdf"]}}')
            f.flush()

            # Create a FileUploader instance and check if the directory_path, config_file, and upload_file_types are set correctly
            file_uploader = FileUploader('test_directory', f.name)
            assert file_uploader.directory_path == 'test_directory'
            assert file_uploader.config_file == f.name
            assert file_uploader.upload_file_types == FileUploader.UPLOAD_FILE_TYPES
            # Check if the FileUploader instance has the s3_uploader and gcs_uploader attributes
            assert hasattr(file_uploader, 's3_uploader')
            assert hasattr(file_uploader, 'gcs_uploader')

    # Clean up the temporary file
    os.remove(f.name)

# Test FileUploader's get_file_ext() method
def test_fileuploader_get_file_ext():
    # Mock the S3Uploader and GCSUploader classes
    with patch('file_uploader.S3Uploader'), patch('file_uploader.GCSUploader'):
        # Create a temporary file to store the test JSON data for FileUploader configuration
        with tempfile.NamedTemporaryFile('w', newline='', delete=False) as f:
            f.write('{"cloud_services": {"s3": {"bucket_name": "test_s3_bucket", "credentials_file": "test_s3_credentials.csv"}, "gcs": {"bucket_name": "test_gcs_bucket", "credentials_file": "test_gcs_credentials.json"}}, "file_types": {"image": ["jpg", "png"], "media": ["mp4"], "document": ["pdf"]}}')
            f.flush()

            # Create a FileUploader instance
            file_uploader = FileUploader('test_directory', f.name)
            # Call the get_file_ext method for 's3' and check if the returned file extensions are correct
            s3_file_ext_list = file_uploader.get_file_ext('s3')
            assert set(s3_file_ext_list) == {'jpg', 'png', 'mp4'}

            # Call the get_file_ext method for 'gcs' and check if the returned file extensions are correct
            gcs_file_ext_list = file_uploader.get_file_ext('gcs')
            assert set(gcs_file_ext_list) == {'pdf'}

    # Clean up the temporary file
    os.remove(f.name)

# Test FileUploader's upload_files() method
def test_fileuploader_upload_files():
    # Create a temporary file to store the test JSON data for FileUploader configuration
    with tempfile.NamedTemporaryFile('w', newline='', delete=False) as f:
        f.write('{"cloud_services": {"s3": {"bucket_name": "test_s3_bucket", "credentials_file": "test_s3_credentials.csv"}, "gcs": {"bucket_name": "test_gcs_bucket", "credentials_file": "test_gcs_credentials.json"}}, "file_types": {"image": ["jpg", "png"], "media": ["mp4"], "document": ["pdf"]}}')
        f.flush()

        # Mock the S3Uploader and GCSUploader classes
        with patch('file_uploader.S3Uploader') as mock_s3_uploader, patch('file_uploader.GCSUploader') as mock_gcs_uploader, patch('file_uploader.os.walk') as mock_os_walk:
            # Set the return value of os.walk() to mimic a directory with three files
            mock_os_walk.return_value = [('test_directory', [], ['test_image.jpg', 'test_video.mp4', 'test_document.pdf'])]
            # Create a FileUploader instance
            file_uploader = FileUploader('test_directory', f.name)
            # Call the upload_files() method and check if the upload_file() method is called for each file with the correct file paths
            file_uploader.upload_files()
            mock_s3_uploader.return_value.upload_file.assert_any_call('test_directory/test_image.jpg')
            mock_s3_uploader.return_value.upload_file.assert_any_call('test_directory/test_video.mp4')
            mock_gcs_uploader.return_value.upload_file.assert_any_call('test_directory/test_document.pdf')

    # Clean up the temporary file
    os.remove(f.name)
