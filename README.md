# Video-Thumbnails-Maker Project of Matteo Guidotti

This repository contains code for the backend solution of the "Video Thumbnails Maker" project.
The project has been entirely developed in Python, thanks to the Flask package. 
I decided to use such framework because thanks to its minimalism it is simple developing and reading code related to it. 
Flask was also able to be customized with all the functionalities I wanted for this project. 

## Structure of the project

The folder Video-Thumbnails-Maker contains metadata to be able to start the application by means of start.sh and the application database dump.<br>
The folder Video-Thumbnails-Maker/videoThumbnailsMaker contains:
    <ul>
        <li><b>index.py</b>: The application server that exposes the service</li>
        <li><b>data</b>: Folder in which thumbnails and videos will be saved</li>
        <li><b>templates</b>: Folder in which HTML templates are stored</li>
        <li><b>models</b>: Package containing declaration for the classes used in the project: VideoJob, VideoJobSchema, ThumbnailJob and ThumbnailJobSchema</li>
        <li><b>utilities</b>: Package containing python utilities to access to the application database and to create and save new thumbnails</li>
    </ul>

## Running the application

In addition to flask, the other dependencies for this project are: mysqlclient, flask-mysqldb, flask_sse, marshmallow, moviepy.<br>
They can be installed locally thanks to pip, but I decided to handle the project with pipenv, so to obtain an application easier to start for every user.

In order to run properly the application, active mysql and redis local servers are necessary. MySQL is necessary for the connection to the database
used for the application data, while redis is necessary to establish and maintain the SSE connection enabled by flask_sse module.

In order to set the MySQL environment properly, it is necessary to add a new user called "admin", with password equal to "admin".
You can issue the following commands:

```bash
    $ sudo mysql

    # in mysql shell
    CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin';
    GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost';
    FLUSH PRIVILEGES;
    EXIT;
```

Then, you can restore the application database starting from the dump file with the following commands:

```bash
    # from the Video-Thumbnail-Maker directory
    $ mysql -u admin -p < videoThumbnailsMaker_DB_dump.sql
```

To run this application, it is important to have Python 3.10+ and [Pipenv](https://pipenv.readthedocs.io/en/latest/) installed locally. 
If you have them, when configuring the application you can issue the following command to set the Python virtual environment, 
so to obtain an environment in which all the required dependencies are satisified:

```bash
    # from the Video-Thumbnail-Maker directory
    $ pipenv install
```
Then, whenever you want to start the application, you can issue just the following command:

```bash
    # from the Video-Thumbnail-Maker directory
    $ ./start.sh 
```

Now the application is working at localhost:5000.

## Description of the application

Considered the fact that in my academic studies I developed only single-threaded API services without real-time updates, I preferred to spend more time
for studying a solution to enable Server-Sent Events at the expense of studying how concurrence between threads could be handled. So, I decided to
use the default configuration of Flask servers, that is single-threaded. I know that it is not the best solution in terms of performance, but I didn't find the time
to study a solution to handle concurrence among threads. This choice will have some consequences that I will analyze later on.

### MySQL application database and filesystem organization

I decided to store the files (videos and images) in a filesystem instead of in the database as row bytes in order to not waste additional time converting files
when they need to be stored. After the conversion of the file to row bytes, the system should still perform the INSERT query, that would become much more heavier. <br>
The application database is composed by 2 tables: video_job and thumbnail_job.

#### video_job

Its fields are: id, filename, status. Each record of this table identify a job in charge of uploading a video named "filename".
        It is possible to retrieve which are the videos that are present in the filesystem because they are the ones related to a video_job record
        that has status equal to "COMPLETED". All the successfully uploaded videos are contained in "data/uploaded_videos".

#### thumbnail_job

Its fields are: id, video_id, width, height, status. Each record of this table identify a job in charge of extracting a thumbnail.
        It is possible to retrieve which are the thumbnails that are present in the filesystem because they are the ones related to a thumbnail_job record
        that has status equal to "COMPLETED". The filename of such thumbnail will be "thumbnail_\[video_id\]\_\[width\]_\[height\].jpg". All the thumbnails are
        contained in "data/thumbnails".


### Real-time updates

The real-time updates are achieved using Server-Sent Events technology. I chose to use such technology because the only updates to be made are sent from the backend
and received by the frontend. Given that it is easier to implement and handle than websockets and that the connection is mono-directional, I chose SSE.<br>
In Flask servers, a SSE connection can be achieved exploiting the module flask_sse. It requires a connection with a local redis database server. Since 
my application is single-threaded, sometimes the SSE connection is lost. In order to solve such problem, the frontend needs to handle the loss of
connection by reconnecting to the SSE service. I tested this functionality with the "templates/job_queue_page.html" file. In this file, the javascript script
consents to connect to the SSE service and, whenever an error is received, it reconnects to the server. In this way, the connection is quite stable. If a multi-worker
solution had been implemented, this connection problem would have been presented more rarely during the execution of the system.<br>
The real-time updates are related to jobs that are in charge of uploading a new video or extracting a thumbnail. Whenever the status of a job changes, the
server publish to the SSE connection the new status.

### API endpoints

#### GET localhost:5000/jobs
Endpoint that renders the html page showing real-time updates using the request method GET.

#### GET localhost:5000/jobs/videos/\[id\]
Endpoint that returns the JSON object representing the job in charge of uploading a video indentified by id, that is
        an integer. It accepts requests using the method GET. An example of the returned JSON object is:


        {
            "filename": "video.mp4",
            "id": 3,
            "status": "QUEUED"
        }


#### GET localhost:5000/jobs/thumbnails/\[id\]
Endpoint that returns the JSON object representing the job in charge of extracting a thumbnail indentified by id, 
        that is an integer. It accepts requests using the method GET. An example of the returned JSON object is:


        {
            "height": 500,
            "id": 7,
            "status": "COMPLETED",
            "video_id": 9,
            "width": 500
        }


#### POST localhost:5000/videos
Endpoint that consents to upload a new video using the request method POST. The new video has to be sent as a form-data uploaded 
        file with the key = 'video'. It returns error if the uploaded file has empty filename or if a file with the same name already exists in the filesystem. 
        It is responsible for storing the uploaded video in the folder "data/uploaded_videos" and to insert a new record for the job responsible for such upload operation.
        Due to the fact that the application is single-threaded, it doesn't make sense to insert the record with status "QUEUED", because it will be certainly changed
        before every other request can access to it. So, I decided to insert the new record only at the end of the operations, so the possible statuses are "FAILED" and
        "COMPLETED". However, the application simulates the multi-threaded behaviour by firstly generating the new video_job object with status equal to "QUEUED".

#### GET localhost:5000/videos
Endpoint that consents to retrieve the list of videos that are stored in the filesystem using the request method GET.
        It returns a JSON object containing the information about the jobs in charge of uploading videos characterized by status equal to "COMPLETED". It is important to 
        remind that the videos that are actually stored in the filesystem are the only ones related to jobs that have status equal to "COMPLETED".


#### POST localhost:5000/thumbnails/\[video_id\]/\[width\]/\[height\]
Endpoint that consents to request the extraction of a new thumbnail for a video identified by
        video_id, that is an integer, using the request method POST. The other two integers are width and height and represent the size of the requested thumbnail. It returns error if the requested
        video is not in the filesystem. The generation of the thumbnail is made possible by the moviepy and PIL modules, that are exploited in the utility made available
        by "utilities/thumbnails_file_utilities.py", that generates and stores the new file. For simplicity, I decided to generate the thumbnail by using the first frame of the video. The newly created thumbnails are saved in the folder "data/thumbnails" and their name will be "thumbnail_\[video_id\]\_\[width\]_\[height\].jpg". The method is also responsible for updating the application database with the record related to the job in charge of extracting the thumbnail. As for the
        upload of videos, due to the fact that the application is single-threaded, it doesn't make sense to insert the record with status "QUEUED", because it will be certainly changed before every other request can access to it. So, I decided to insert the new record only at the end of the operations, so the possible statuses are "FAILED" and "COMPLETED". However, the application simulates the multi-threaded behaviour by firstly generating the new thumbnail_job object with status equal to "QUEUED".

#### GET localhost:5000/t/\[video_id\]?w=\[width\]&h=\[height\]
Endpoint that sends to the client the thumbnail file for the video identified by video_id, with the 
        requested width and height using the request method GET. It returns error if the requested thumbnail is not in the filesystem.


## Possible improvements

As I already said in the introduction, the application could be made into a multi-threaded application in order to increase performance. In particular, when heavier operations
like the upload of a video or the creation of a thumbnail are requested, the server could delegate a thread to perform such operations and immediately inform the client
that it is performing the requested operation asynchronously. In this way, the client won't be forced to wait for the end of all the operations required to complete the task.
