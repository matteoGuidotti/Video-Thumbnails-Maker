from .models.video import Video

# add a video to the database, return 1 if the query is successfully completed, -1 otherwise
def add_video(connection, new_video):
    cursor = connection.connection.cursor()
    query = "INSERT INTO video (filename, status) VALUES (%s, %s)"
    try:
        cursor.execute(query, (new_video.filename, new_video.status))
        connection.connection.commit()
    except:
        return -1
    cursor.close()
    return 1

def update_video_status(connection, video):
    cursor = connection.connection.cursor()
    query = "UPDATE video SET status = '%s' WHERE filename = '%s'"
    try:
        cursor.execute(query, (video.status, video.filename))
        connection.connection.commit()
    except:
        return -1
    cursor.close()
    return 1