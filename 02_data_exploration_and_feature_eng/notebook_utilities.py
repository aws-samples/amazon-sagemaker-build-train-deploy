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