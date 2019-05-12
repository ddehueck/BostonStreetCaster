import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from segmentation.segment import segment
from damage_classification.classify import classify

__author__ = 'Neha, Devin, Po-Yu'

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
TO_SEGMENT = os.path.join(APP_ROOT, 'segmentation/to_segment/0/')
SEGMENTED = os.path.join(APP_ROOT, 'segmentation/segmented_images/0/')


@app.route("/")
def index():
    return render_template("upload.html")


@app.route("/upload", methods=['POST'])
def upload():
    """
    Upload image files to infer on - segment then classify
    """

    if not os.path.isdir(TO_SEGMENT):
        os.mkdir(TO_SEGMENT)
    else:
        print("could not create upload directory: {}".format(TO_SEGMENT))
        print(request.files.getlist("file"))

    for upload in request.files.getlist("file"):
        filename = upload.filename
        destination = "/".join([TO_SEGMENT, filename])
        upload.save(destination)

    return redirect(url_for('get_gallery'))


@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory(TO_SEGMENT, filename)


@app.route('/segmented/<filename>')
def send_segmented_image(filename):
    return send_from_directory(SEGMENTED, filename)


@app.route('/clear-uploads')
def clear_uploads():
    """
    Clear the directory that /uploads places images to
    """
    filelist = [f for f in os.listdir(TO_SEGMENT)]
    for f in filelist:
        os.remove(os.path.join(TO_SEGMENT, f))

    filelist = [f for f in os.listdir(SEGMENTED)]
    for f in filelist:
        os.remove(os.path.join(SEGMENTED, f))

    return redirect(url_for('index'))


@app.route('/gallery')
def get_gallery():
    """
    View uploaded images and take next step
    """
    to_segment = os.listdir(TO_SEGMENT)
    print(to_segment)
    return render_template("gallery.html",
                           image_names=to_segment,
                           next_page_text="Segment Images! - (might take a couple mins)",
                           next_page="get_segmented_gallery"
                           )


@app.route('/segmented-gallery')
def get_segmented_gallery():
    """"""

    if len([f for f in os.listdir(SEGMENTED)]) is 0:
        segment()

    return render_template("segmented-gallery.html",
                           image_names=os.listdir(SEGMENTED),
                           next_page_text="Get Predictions!",
                           next_page="get_predictions_gallery")


@app.route('/predictions-gallery')
def get_predictions_gallery():
    predictions = classify()
    return render_template("prediction-gallery.html",
                           image_names=os.listdir(TO_SEGMENT),
                           segmented_image_names=os.listdir(SEGMENTED),
                           predictions=predictions,
                           next_page_text="Clear Uploads and Restart",
                           next_page="clear_uploads")


if __name__ == "__main__":
    app.run(port=4555, debug=True)
