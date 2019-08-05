from flask import Flask, render_template
from base64 import b64encode
import datetime
import pandas as pd
from altair import Chart
from pymongo import MongoClient
from src.ImageProcessing import ImageProcessing

app = Flask(__name__)
client = MongoClient('mongodb://mongo:27017')
db = client.quicksign

image_processor = ImageProcessing(client)


@app.route("/")
def index_page():
    html = """
    <h1>QuickSign</h1>
    <p>Important: run the task "Process Images" first in order to save data in database</p>
        <ul>
          <li><a href="/process/">Process Images (might take few minutes)</a></li>
          <li><a href="/image/">All images</a></li>
          <li><a href="/monitoring/">Monitoring</a></li>
        </ul>
    """
    return html.format()


@app.route('/process/', methods=['GET'])
def process_images():
    image_processor.process_images()
    html = """
        <p>images processed successfully</p>
            <ul>
              <li><a href="../">Go back to main menu</a></li>
            </ul>
        """
    return html.format()


@app.route('/image/', methods=['GET'])
def get_all_images():
    pictures = db.pictures
    output = []
    html_body = "<h1> Choose an image </h1> <ul>"
    collection = pictures.find()
    count = collection.count()
    if count > 0:
        html_body += "<p> Database contains "+str(count)+" images</p>"
        for q in collection:
            html_body += " <li><a href="+q['md5']+">"+q['md5']+"</a></li>"

            output.append({'md5': q['md5'], 'md5': q['md5'], 'height': q['height'], 'width': q['width'],
                           'timestamp': q['timestamp']})
        html_body += "</ul>"
    else:
        html_body = "<p>No images on database, try running Process Images first</p>"
    return html_body.format()


@app.route('/image/<md5>', methods=['GET'])
def get_one_image(md5):
    pictures = db.pictures
    q = pictures.find_one({'md5': md5})
    image_binary = q['gray_scale']
    image = b64encode(image_binary)
    return render_template('image.html', image=image.decode('utf8'))


@app.route('/monitoring/', methods=['GET'])
def get_monitor_stats():
    monitor = db.monitor
    minutes = []
    states = []
    monitor_data = monitor.find()
    if monitor_data.count() > 0:
        for m in monitor.find():
            date_code = datetime.datetime.fromtimestamp(m['timestamp']).isoformat().split('.')[0][:-3]
            minutes.append(date_code)
            states.append(m['state'])

        data_frame = {'Minutes': minutes,
                     'State': states}
        data_frame = pd.DataFrame(data_frame)

        chart = Chart(data_frame).mark_bar(
        ).encode(
            y='Minutes',
            x='count()',
            color='State'
        )

        chart.save('./templates/chart.html')
        return render_template('chart.html')
    else:
        html_body = "<p>No data found on database, try running Process Images first</p>"
        return html_body.format()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')