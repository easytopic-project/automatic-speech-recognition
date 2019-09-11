from flask import Flask, request, flash, redirect
import pika
import os
from DAO.connection import Connection
app = Flask(__name__)


@app.route('/vad', methods=['POST'])
def vad():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and (file.filename.endswith('.mp3') or file.filename.endswith('.wav')):
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ['QUEUE_SERVER']))
            channel = connection.channel()

            channel.queue_declare(queue='vad')
            db_conn = Connection()
            oid = db_conn.insert_jobs(type='vad', status='new', file=file.read())
            message = {'type': 'vad', 'status': 'new', 'oid': oid}
            channel.basic_publish(exchange='', routing_key='vad', body=str(message))
            connection.close()
            return 'Done'
        else:
            flash('Invalid file')
            return redirect(request.url)


@app.route('/asr', methods=['POST'])
def asr():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and (file.filename.endswith('.mp3') or file.filename.endswith('.wav')):
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()

            channel.queue_declare(queue='asr')
            db_conn = Connection()
            oid = db_conn.insert_jobs(type='asr', status='new', file=file.read())
            message = {'type': 'asr', 'status': 'new', 'oid': oid}
            channel.basic_publish(exchange='', routing_key='asr', body=str(message))
            connection.close()
            return 'Done'
        else:
            flash('Invalid file')
            return redirect(request.url)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')