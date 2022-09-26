import boto3

def cleanup_glue_resources():
    glue_client = boto3.client('glue')

    # Trying to remove any existing database, crawler and job with the same name.

    crawler_found = True
    try:
        glue_client.get_crawler(Name = 'endtoendml-crawler')
    except glue_client.exceptions.EntityNotFoundException:
        crawler_found = False

    db_found = True
    try:
        glue_client.get_database(Name = 'endtoendml-db')
    except glue_client.exceptions.EntityNotFoundException:
        db_found = False

    job_found = True
    try:
        glue_client.get_job(JobName = 'endtoendml-job')
    except glue_client.exceptions.EntityNotFoundException:
        job_found = False

    if crawler_found:
        glue_client.delete_crawler(Name = 'endtoendml-crawler')
    if db_found:
         glue_client.delete_database(Name = 'endtoendml-db')
    if job_found:
         glue_client.delete_job(JobName = 'endtoendml-job')

    print("Cleanup completed.")

def check_dependencies():

    import sagemaker
    import numpy
    import pandas
    
    import sys
    import os
    import IPython

    def versiontuple(v):
        return tuple(map(int, (v.split("."))))
    
    kernel_restart_required = False
    
    required_version = '2.90.0'
    if (versiontuple(sagemaker.__version__) < versiontuple(required_version)): 
        print('This workshop was tested with sagemaker version {} but you are using {}. Installing required version...'.format(required_version, sagemaker.__version__) )
        stream = os.popen('{} -m pip install -U sagemaker=={}'.format(sys.executable, required_version))
        output = stream.read()
        print(output)
        kernel_restart_required = True
    
    required_version = '1.3.4'
    if (versiontuple(pandas.__version__) < versiontuple(required_version) ):
        print('This workshop was tested with pandas version {} but you are using {}. Installing required version...'.format(required_version, pandas.__version__))
        stream = os.popen('{} -m pip install -U pandas=={}'.format(sys.executable, required_version))
        output = stream.read()
        print(output)
        kernel_restart_required = True

    required_version = '1.21.6' 
    if (versiontuple(numpy.__version__) < versiontuple(required_version)):
        print('This workshop was tested with numpy version {} but you are using {}. Installing required version...'.format(required_version, numpy.__version__ ) )
        stream = os.popen('{} -m pip install -U numpy=={}'.format(sys.executable, required_version))
        output = stream.read()
        print(output)
        kernel_restart_required = True
         
    if kernel_restart_required:
        print("Restarting kernel after installing new dependencies...")
        IPython.Application.instance().kernel.do_shutdown(True)     
        print('WARNING: Kernel restarting...please wait 30 seconds before moving to the next cell!')