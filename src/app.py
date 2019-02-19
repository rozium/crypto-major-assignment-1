from flask import Flask, render_template, request
import time
import os, json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ROOT_PATH'] = app.root_path

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/audio", methods=['GET'])
def audioGET():
    return render_template('audio_option.html')

@app.route("/audio/extract", methods=['GET'])
def audioExtractGET():
    return render_template('audio_embed.html')

@app.route("/audio/extract", methods=['POST'])
def audioExtractPOST():
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})
    return json.dumps({'status':'success'})

@app.route("/audio/embed", methods=['GET'])
def audioEmbedGET():
    return render_template('audio_embed.html')

@app.route("/audio/embed", methods=['POST'])
def audioEmbedPOST():
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})

@app.route("/video", methods=['GET'])
def videoGET():
    return render_template('video_option.html')

@app.route("/video/extract", methods=['GET'])
def videoExtractGET():
    return render_template('video_embed.html')

@app.route("/video/extract", methods=['POST'])
def videoExtractPOST():
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})
    return json.dumps({'status':'success'})

@app.route("/video/embed", methods=['GET'])
def videoEmbedGET():
    return render_template('video_embed.html')

@app.route("/video/embed", methods=['POST'])
def videoEmbedPOST():
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})
    file = request.files['imgFile']
    print file
    if file.filename == '':
        return json.dumps({'status':'Error2'})
    image = request.files['imgFile']
    # color = request.form.get('color')
    # image.save(app.root_path + '/' + os.path.join(app.config['UPLOAD_FOLDER'], 'image.png'))
    # plt.clf()
    # if(color == 'a'):
    #     colorname = 'Picture'
    #     hist = build_hist(UPLOAD_FOLDER + '/image.png', 'a', app.root_path)
    #     plt.plot(hist[0], color=(1, 0, 0))
    #     plt.plot(hist[1], color=(0, 1, 0))
    #     plt.plot(hist[2], color=(0, 0, 1))
    #     plt.plot(hist[3], color=(0.66, 0.66, 0.66))
    # else :
    #     if(color == 'r'):
    #         colorname = 'Red'
    #         plotcolor = (1, 0, 0)
    #     elif(color == 'g'):
    #         plotcolor = (0, 1, 0)
    #         colorname = 'Green'
    #     elif(color == 'b'):
    #         colorname = 'Blue'
    #         plotcolor = (0, 0, 1)
    #     else:
    #         colorname = 'Grayscale'
    #         plotcolor = (0.5, 0.5, 0.5)
    #     plt.plot(build_hist(UPLOAD_FOLDER + '/image.png', color, app.root_path), color=plotcolor)

    # plt.savefig(app.root_path + '/' + 'static/images/plot.png')
    # return json.dumps({'url_after': 'static/images/plot.png?' + str(time.time()) })
    return json.dumps({'status':'success'})

@app.route("/audio", methods=['POST'])
def audioPOST():
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})
    file = request.files['imgFile']
    if file.filename == '':
        return json.dumps({'status':'Error2'})
        image = request.files['imgFile']
    # method = request.form.get('method')
    # img_path = 'static/images/image.png'
    # image.save(app.root_path + '/' + img_path)
    # if method == 'k':
    #     # kumulatif
    #     title = 'Cumulative'
    #     imagee = Image.open(app.root_path + '/' + img_path)
    #     new_image = normalize(imagee, app.root_path)
    #     norm_img_path = 'static/images/normalized_image.png'
    #     new_image.save(app.root_path + '/' + norm_img_path)
    # else:
    #     # scaling
    #     title = 'Scaling'
    #     base_image = Image.open(app.root_path + '/' + img_path)
    #     width, height = base_image.size
    #     normalized_img = scaling(base_image, width, height, app.root_path)
    #     norm_img_path = 'static/images/normalized_image.png'
    #     normalized_img.save(app.root_path + '/' + norm_img_path)
    # return json.dumps({'url_after': norm_img_path + '?' + str(time.time()) })
    return json.dumps({'status':'success'})

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=1111,debug=True)
