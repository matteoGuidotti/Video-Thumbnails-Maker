# Video-Thumbnails-Maker Project

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
        <li><b>utilities</b>: Package containing python utilities to access to the application database and filesystem</li>
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
If you have then, when configuring the application you can issue the following command to set the Python virtual environment, 
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

Now the application is working at localhost:5000

## Description of the application

Considered the fact that in my academic studies I developed only single-threaded API services without real-updates, I preferred to spend more time
for studying a solution to enable Server-Sent Events at the expense of studying how concurrence between threads could be handled. So, I decided to
use the default configuration of Flask severs, that is single-threaded. I know that it is not a great solution in terms of performance, but I didn't find the time
to study a solution to handle concurrence among threads. This choice will have some consequences that I will analyze later on.

### Real-time updates

The real-time updates are achieved using Server-Sent Events technology. I chose to use such technology because the only updates to be made are sent from the backend
and received by the frontend. Given that it is easier to implement than websockets and that the connection is mono-directional, I chose SSE.<br>
In Flask servers, a SSE connection can be achieved exploiting the module flask_sse. It requires a connection with a local redis database server. Due to the fact 
that my application is single-threaded, sometimes the SSE connection is lost. In order to solve such problem, the frontend needs to handle the loss of
connection by reconnecting to the SSE service. I tested this functionality with the templates/job_queue_page.html file. In this file, the javascript script
consent to connect to the SSE service and, whenever an error is received, it reconnects to the server. In this way, the connection is quite stable. If a multi-worker
solution had been implemented, this connection problem would have been presented more rarely during the execution of the system.<br>
The real-time updates are related to jobs that are in charge of uploading a new video or extracting a thumbnail. Whenever the status of a job changes, the
server publish to the SSE connection the new status.