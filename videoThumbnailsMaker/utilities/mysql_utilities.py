# module containing utilities to access to mysql database, starting from a mysql connection that has been already established

from ..models.video_job import VideoJob
from ..models.thumbnail_job import ThumbnailJob


# add a video job to the database, return the id of the newly added video job if the query is successfully completed, -1 otherwise
def add_video_job_db(connection, new_video):
    cursor = connection.connection.cursor()
    query = "INSERT INTO video_job (filename, status) VALUES (%s, %s)"
    try:
        cursor.execute(query, (new_video.filename, new_video.status))
        connection.connection.commit()
        new_id = cursor.lastrowid
    except Exception as e:
        print(f"MySQL Exception: {e}")
        return -1
    cursor.close()
    return new_id


# add a thumbnail job to the database, return the id of the newly added thumbnail job if the query is successfully completed, -1 otherwise
def add_thumbnail_job_db(connection, new_thumbnail):
    cursor = connection.connection.cursor()
    query = "INSERT INTO thumbnail_job (video_id, width, height, status) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(query, (new_thumbnail.video_id, new_thumbnail.width, new_thumbnail.height, new_thumbnail.status))
        connection.connection.commit()
        new_id = cursor.lastrowid
    except Exception as e:
        print(f"MySQL Exception: {e}")
        return -1
    cursor.close()
    return new_id


# return a list containing all the information about succesfully loaded videos. It returns -1 in case of error
def get_all_videos_db(connection):
    cursor = connection.connection.cursor()
    # only when status is COMPLETED we know that the video is present in the filesystem
    query = "SELECT * FROM video_job WHERE status = 'COMPLETED'"
    try:
        cursor.execute(query)
        query_result = cursor.fetchall()
    except Exception as e:
        print(f"MySQL Exception: {e}")
        return -1
    video_list = []
    for v in query_result:
        video_list.append(VideoJob(v[1], v[2], v[0]))  # the db returns the information in the order [id | filename | status] 
    return video_list


# return information about a job in charge of uploading a video. It returns -1 in case of error
def get_video_job_db(connection, video_id):
    cursor = connection.connection.cursor()
    query = "SELECT * FROM video_job WHERE id = %s"
    try:
        cursor.execute(query, (video_id, ))
        query_result = cursor.fetchone()
    except Exception as e:
        print(f"MySQL Exception: {e}")
        return -1
    if not query_result:    # searched job doesn't exist
        return None
    else:
        return VideoJob(query_result[1], query_result[2], query_result[0])  # the db returns the information in the order [id | filename | status] 


# return information about a job in charge of generating a thumbnail. It returns -1 in case of error
def get_thumbnail_job_db(connection, id):
    cursor = connection.connection.cursor()
    query = "SELECT * FROM thumbnail_job WHERE id = %s"
    try:
        cursor.execute(query, (id, ))
        query_result = cursor.fetchone()
    except Exception as e:
        print(f"MySQL Exception: {e}")
        return -1
    if not query_result:    # thumbnail information don't exist
        return None
    else:
        # the db returns the information in the order [id | video_id | width | height | status]
        return ThumbnailJob(query_result[1], query_result[2], query_result[3], query_result[4], query_result[0])  


# return one thumbnail succesfully created object related to the video passed as a parameter, if it exists
def get_thumbnail_of_video_db(connection, video_id):
    cursor = connection.connection.cursor()
    # only when status is COMPLETED we know that the thumbnail is present in the filesystem
    query = "SELECT j.* FROM video_job v INNER JOIN thumbnail_job j ON v.id = j.video_id WHERE v.id = %s AND j.status = 'COMPLETED';"
    try:
        cursor.execute(query, (video_id, ))
        query_result = cursor.fetchone()
    except Exception as e:
        print(f"MySQL Exception: {e}")
        return -1
    if not query_result:    # thumbnail information don't exist
        return None
    else:
        # the db returns the information in the order [id | video_id | width | height | status]
        return ThumbnailJob(query_result[1], query_result[2], query_result[3], query_result[4], query_result[0]) 