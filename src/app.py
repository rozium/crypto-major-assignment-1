from flask import Flask, render_template, request
import lsb
import time
import os, json

app = Flask(__name__)
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

    # check file and msg_file
    if 'file' not in request.files or 'msg_file' not in request.files:
        return json.dumps({
            'error': True,
            'data': 'Cover Video atau Pesan tidak ditemukan',
        })

    # check file extension
    file = request.files['file']
    msg_file = request.files['msg_file']
    if os.path.splitext(file.filename)[1] != '.avi':
        return json.dumps({
            'error': True,
            'data': 'Cover Video harus berformat avi!',
        })

    # check file size
    filepath = app.root_path + '/static/output/'
    file.save(filepath + file.filename)
    msg_file.save(filepath + msg_file.filename)
    if os.stat(filepath + msg_file.filename).st_size > os.stat(filepath + file.filename).st_size:
        return json.dumps({
            'error': True,
            'data': 'Panjang pesan tidak boleh melibihi panjang cover video!',
        })

    # embed file
    lsb_stego = lsb.LSB()

    # config stego info
    lsb_stego.frame_store_mode = int(request.form.get('frame'))
    lsb_stego.pixel_store_mode = int(request.form.get('pixel'))
    lsb_stego.lsb_bit_size = int(request.form.get('lsbit'))
    lsb_stego.is_message_encrypted = True if int(request.form.get('enkripsi')) else False

    lsb_stego.key = request.form.get('kunci') or 'secretkey'
    lsb_stego.generate_stego_key()

    # load cover object
    lsb_stego.cover_object_path = filepath + file.filename
    lsb_stego.cover_object_audio_path = filepath + file.filename + '.wav'
    lsb_stego.load_object("cover")

    # load message
    lsb_stego.message_path = filepath + msg_file.filename
    lsb_stego.load_message()

    # put message to cover object
    success = lsb_stego.put_message()
    if success:
        # save cover object to video
        output_filepath = filepath + 'out_' + file.filename
        lsb_stego.stego_object_temp_path = filepath + 'temp_out_' + file.filename
        lsb_stego.stego_object_path = output_filepath
        lsb_stego.save_stego_object()

        # TODO: convert video to mp4 for playback
    else:
        return json.dumps({
            'error': True,
            'data': 'Panjang pesan tidak boleh melibihi panjang cover video!',
        })

    return json.dumps({
        'error': False,
        'cover_video_mp4': '/static/example/small.mp4?' + str(time.time()),
        'stego_video_mp4': '/static/example/small.mp4?' + str(time.time()),
        'stego_video': '/static/output/out_' + file.filename + '?' + str(time.time()),
        'psnr': lsb_stego.calculate_psnr(),
    })

@app.route("/audio", methods=['POST'])
def audioPOST():
    return json.dumps({'status':'success'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1111, debug=True)
