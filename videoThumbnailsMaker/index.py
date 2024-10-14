# API RESTful server

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sse import sse
from flask_mysqldb import MySQL
import os
from .db_utilities import add_video, update_video_status
from .models.video import Video, VideoSchema

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'videoThumbnailsMaker_DB'

#Configuration for SSE connection
app.config["REDIS_URL"] = "redis://localhost"	#A connection with a redis db is necessary for flask-sse
app.register_blueprint(sse, url_prefix='/stream')

#Folder containing uploaded videos
app.config["UPLOAD_FOLDER"] = "videoThumbnailsMaker/data/uploaded_videos/"

#Folder containing the created thumbnails
THUMBNAILS_FOLDER = "data/thumbnails/"

mysql_connection = MySQL(app)

@app.route('/job', methods=['GET'])
def job_queue_page():
	return render_template("job_queue_page.html")

@app.route('/video', methods=['POST'])
def upload_video():
	if "video" not in request.files:
		return "No file part", 400
	
	file = request.files["video"]
	if file.filename == '':
		return "Empty file name", 400
	
	# the new video is initially stored with status equal to LOADED, eventually it will be changed later if errors occur
	new_video = Video(file.filename, "LOADED")

	#writing to sse connection that the file has been received and must be stored yet
	sse.publish({"message": f"upload of file named {new_video.filename} is queued"}, type='job_status')

	if os.path.exists(f"{app.config['UPLOAD_FOLDER']}{new_video.filename}"):
		sse.publish({"message": f"upload of file named {file.filename} is failed"}, type='job_status')
		return "A file with the same name already exists", 409

	if add_video(mysql_connection, new_video) < 0:
		sse.publish({"message": f"upload of file named {file.filename} is failed"}, type='job_status')
		return "Error saving the file", 500
	
	try:
		file.save(f"{app.config['UPLOAD_FOLDER']}{file.filename}")
	except:
		sse.publish({"message": f"upload of file named {file.filename} is failed"}, type='job_status')
		new_video.status = "FAILED"
		update_video_status(mysql_connection, new_video)
		return "Upload of the file failed", 500

	sse.publish({"message": f"upload of file named {file.filename} is completed"}, type='job_status')
	return "Upload completed successfully", 201
		

if __name__ == '__main__':
	app.run()