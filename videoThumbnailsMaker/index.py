# API RESTful backend server for Video Thumbnails Maker project

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sse import sse
from flask_mysqldb import MySQL
import os
from .utilities.mysql_utilities import *
from .utilities.thumbnails_file_utilities import generate_thumbnail_file_from_video
from .models.video_job import VideoJob, VideoJobSchema
from .models.thumbnail_job import ThumbnailJob, ThumbnailJobSchema


app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'videoThumbnailsMaker_DB'
mysql_connection = MySQL(app)

# Configuration for SSE connection
app.config["REDIS_URL"] = "redis://localhost"	#A connection with a redis db is necessary for flask-sse
app.register_blueprint(sse, url_prefix='/stream')

# Folder containing uploaded videos
app.config["UPLOAD_FOLDER"] = "videoThumbnailsMaker/data/uploaded_videos/"

# Path to the folder containing the created thumbnails when we need to save a new thumbnail
THUMBNAILS_CREATION_FOLDER = "videoThumbnailsMaker/data/thumbnails/"

# Path to the folder containing the thumbnails when we need to send a thumbnail to the client
THUMBNAILS_DOWNLOAD_FOLDER = "./data/thumbnails/"


# endpoint for visualizing page with real time updates about status of all the jobs
@app.route('/jobs', methods=['GET'])
def get_job_queue_page():
	return render_template("job_queue_page.html")


# endpoint for querying the status of one job in charge of uploading a video , given the id
@app.route('/jobs/videos/<int:id>', methods=['GET'])
def get_video_job(id):
	video_info = get_video_job_db(mysql_connection, id)
	if video_info == -1:
		return jsonify({"error": "Error ckecking db"}), 500
	if video_info == None:
		return jsonify({"error": "The id for the requested video uploading job does not exist"}), 404
	# serialization of the Video object as a json object
	schema = VideoJobSchema()
	serialized_video_info = schema.dump(video_info)
	return jsonify(serialized_video_info)


# endpoint for querying the status of one thumbnail extraction job, given the id
@app.route('/jobs/thumbnails/<int:id>', methods=['GET'])
def get_thumbnail_job(id):
	thumbnail_info = get_thumbnail_job_db(mysql_connection, id)
	if thumbnail_info == -1:
		return jsonify({"error": "Error checking db"}), 500
	if thumbnail_info == None:
		return jsonify({"error": "The id for the requested thumbnail extraction job does not exist"}), 404
	# serialization of the Video object as a json object
	schema = ThumbnailJobSchema()
	serialized_thumbnail_info = schema.dump(thumbnail_info)
	return jsonify(serialized_thumbnail_info)


# endpoint to upload a new video. The new video is sent as a form-data uploaded file with the key = 'video'
@app.route('/videos', methods=['POST'])
def upload_video():
	if "video" not in request.files:
		return jsonify({"error": "No video part in request"}), 400
	file = request.files["video"]
	if file.filename == '':
		return jsonify({"error": "The filename of the uploaded file can't be empty"}), 400

	# the file are stored in the filesystem, so two files can't have the same name
	if os.path.exists(f"{app.config['UPLOAD_FOLDER']}{file.filename}"):
		return jsonify({"error": "A file with the same name already exists, please re-upload the file with another filename"}), 409

	# writing to sse connection that the file has been received and must be stored yet
	sse.publish({"message": f"upload of file named {file.filename} is queued"}, type='job_status')
	new_video = VideoJob(file.filename, "QUEUED")

	try:
		file.save(f"{app.config['UPLOAD_FOLDER']}{file.filename}")
	except Exception as e:
		print(f"Exception during file saving: {e}")
		# if the file saving has raised an exception, we can state that the job is failed
		sse.publish({"message": f"upload of file named {file.filename} is failed"}, type='job_status')
		new_video.status = "FAILED"
		new_id = add_video_job_db(mysql_connection, new_video)
		new_video.id = new_id
		# serialize and return the information added to the db
		schema = VideoJobSchema()
		serialized_video_info = schema.dump(new_video)
		return jsonify(serialized_video_info), 500

	sse.publish({"message": f"upload of file named {file.filename} is completed"}, type='job_status')

	new_video.status = "COMPLETED"
	new_id = add_video_job_db(mysql_connection, new_video)
	new_video.id = new_id
	# serialize and return the information added to the db
	schema = VideoJobSchema()
	serialized_video_info = schema.dump(new_video)
	return jsonify(serialized_video_info), 201


# endpoint to get the list of information about all the videos successfully uploaded
# the video that are in the filesystem are the ones related to job that have status = COMPLETED
@app.route('/videos', methods=['GET'])
def get_all_videos():
	video_list = get_all_videos_db(mysql_connection)
	schema = VideoJobSchema(many=True)
	to_be_returned = schema.dump(video_list)
	return jsonify(to_be_returned), 200


# endpoint to request the generation of a new thumbnail. The thumbnail is characterized by the video through which the thumbnail is obtained and its size
@app.route('/thumbnails/<int:video_id>/<int:width>/<int:height>', methods=['POST'])
def generate_thumbnail(video_id, width, height):
	# check if the video_id is valid
	video_info = get_video_job_db(mysql_connection, video_id)
	if video_info == -1:
		return jsonify({"error": "Error checking db"}), 500
	if video_info == None:
		return jsonify({"error": "The id for the requested video does not exist"}), 404
	# only videos with status = COMPLETED are in the filesystem, so to extract the thumbnail
	if video_info.status != "COMPLETED":
		return jsonify({"error": "The requested video is not present because it has not been succesfully uploaded"}), 400

	# the pattern for the creation of the name of a new thumbnail is: thumbnail_videoID_width_height.jpg
	thumbnail_file_path = f"{THUMBNAILS_CREATION_FOLDER}thumbnail_{video_id}_{width}_{height}.jpg"

	if os.path.exists(thumbnail_file_path):
		return jsonify({"error": "The thumbnail already exists"}), 400

	# if the thumbnail does not already exist, we can continue with its generation
	thumbnail_job = ThumbnailJob(video_id, width, height, "QUEUED")
	sse.publish({"message": f"generation of thumbnail for video {video_id}, size: {width}x{height} is queued"}, type='job_status')

	generate_thumbnail_file_from_video(f"{app.config['UPLOAD_FOLDER']}{video_info.filename}", width, height, thumbnail_file_path)

	thumbnail_job.status = "COMPLETED"
	sse.publish({"message": f"generation of thumbnail for video {video_id}, size: {width}x{height} is completed"}, type='job_status')
	new_id = add_thumbnail_job_db(mysql_connection, thumbnail_job)
	thumbnail_job.id = new_id
	schema = ThumbnailJobSchema()
	serialized_thumbnail_info = schema.dump(thumbnail_job)
	return jsonify(serialized_thumbnail_info), 201


# endpoint for retrieving the requested thumbnail. The thumbnail size is sent from the client with two query-parameters
@app.route('/t/<int:video_id>', methods=['GET'])
def get_image(video_id):
	if 'w' not in request.args or 'h' not in request.args:
		return jsonify({"error": "Wrong arguments. The request needs to contain two query parameters: 'w' and 'h'"}), 400

	width = request.args.get('w')
	height = request.args.get('h')

	# all the thumbnail file names follow this pattern: thumbnail_videoID_width_height.jpg
	filename = f"thumbnail_{video_id}_{width}_{height}.jpg"
	try:
		return send_from_directory(THUMBNAILS_DOWNLOAD_FOLDER, filename, as_attachment=False)
	except FileNotFoundError:
		return jsonify({"error": "File not found"}), 404
	

if __name__ == '__main__':
	app.run()