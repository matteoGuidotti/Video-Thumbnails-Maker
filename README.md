# Video-Thumbnails-Maker Project

This repository contains code for the backend solution of the "Video Thumbnails Maker" project.
The project has been entirely developed in Python, thanks to the Flask package. 
I decided to use such framework because thanks to its minimalism it is simple developing and reading code related to it. 
Flask was also able to be customized with all the functionalities I wanted for this project. 

## Structure of the project

The folder Video-Thumbnails-Maker contains metadata to be able to start the application by means of start.sh and the application database dump.<br>
The folder Video-Thumbnails-Maker/videoThumbnailsMaker contains:
    <ul>
        <li>index.py: The application server that exposes the service</li>
        <li>data: Folder in which thumbnails and videos will be saved</li>
        <li>templates: Folder in which HTML templates are stored</li>
        <li>models: Package containing declaration for the classes used in the project: VideoJob, VideoJobSchema, ThumbnailJob and ThumbnailJobSchema </li>
        <li>utilities: Package containing python utilities to access to the application database and filesystem</li>
    </ul>

## Running the application

In addition to flask, the other dependencies for this project are: mysqlclient, flask-mysqldb, flask_sse, marshmallow, moviepy.<br>
They can be installed locally thanks to pip, but I decided to handle the project with pipenv, so to obtain an application easier to start for every user.

In order to run properly the application, active mysql and redis local servers are necessary. MySQL is necessary for the connection to the database
used for the application data, while redis is necessary to establish and maintain the SSE connection enabled by flask_sse module.

In order to set the MySQL environment properly, it is necessary to add a new user called "admin". You can issue the following commands:

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
If you have then, you can issue the following commands:

```bash
    # from the Video-Thumbnail-Maker directory
    $ ./start.sh 
```

Now the application is working at localhost:5000