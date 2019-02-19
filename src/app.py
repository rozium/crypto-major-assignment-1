from flask import Flask, render_template, request
from audio_main import *
import lsb
import time
import os, json

app = Flask(__name__)
app.config['ROOT_PATH'] = app.root_path

output_path = '/static/output/'

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/audio", methods=['GET'])
def audioGET():
    return render_template('audio_option.html')

@app.route("/audio/extract", methods=['GET'])
def audioExtractGET():
    return render_template('audio_extract.html')

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

    # check file and msg_file
    if 'file' not in request.files or 'msg_file' not in request.files:
        return json.dumps({
            'error': True,
            'data': 'Cover Audio atau Pesan tidak ditemukan',
        })

    # check file extension
    file = request.files['file']
    msg_file = request.files['msg_file']
    if os.path.splitext(file.filename)[1] != '.wav':
        return json.dumps({
            'error': True,
            'data': 'Cover Audio harus berformat avi!',
        })

    # check file size
    filepath = app.root_path + output_path
    file.save(filepath + file.filename)
    msg_file.save(filepath + msg_file.filename)
    if os.stat(filepath + msg_file.filename).st_size > os.stat(filepath + file.filename).st_size:
        return json.dumps({
            'error': True,
            'data': 'Panjang pesan tidak boleh melibihi panjang cover audio!',
        })

    # embed file

    # config stego info
    # audio_file = filepath + file.filename
    # message_file = filepath + msg_file.filename

    # stego_file = filepath + 'out_' + file.filename
    # ext_message_file = filepath + 'ex_out_' + file.filename

    # key = request.form.get('kunci') or 'secretkey'

    # if not insert_message(audio_file, message_file, stego_file, True if int(request.form.get('enkripsi')) else False, True if int(request.form.get('method')) else False, key):
    #     return json.dumps({
    #         'error': True,
    #         'data': 'Panjang pesan tidak boleh melibihi panjang cover video!',
    #     })

    return json.dumps({
        'error': False,
        'cover_audio': output_path + file.filename + '?' + str(time.time()),
        'stego_audio': output_path + file.filename + '?' + str(time.time()),
        # 'stego_audio': output_path + 'out_' + file.filename + '?' + str(time.time()),
        'psnr': 90,
    })

@app.route("/video", methods=['GET'])
def videoGET():
    return render_template('video_option.html')

@app.route("/video/extract", methods=['GET'])
def videoExtractGET():
    return render_template('video_extract.html')

@app.route("/video/extract", methods=['POST'])
def videoExtractPOST():
    
    # check file
    if 'file' not in request.files:
        return json.dumps({
            'error': True,
            'data': 'Stego Video tidak ditemukan',
        })

    # save file
    file = request.files['file']
    filepath = app.root_path + output_path
    file.save(filepath + file.filename)

    # extract file
    lsb_stego = lsb.LSB()
    lsb_stego.stego_object_path = filepath + file.filename

    # config stego info
    lsb_stego.key = request.form.get('kunci') or 'secretkey'
    lsb_stego.generate_stego_key()
    
    # load stego object
    lsb_stego.load_object("stego")

    # get hidden message and save it
    lsb_stego.message_output_path = filepath
    lsb_stego.message_output_filename = 'output'
    msg_file, msg_ext = lsb_stego.get_message()

    return json.dumps({
        'error': False,
        'msg_file': output_path + msg_file + '?' + str(time.time()),
        'msg_ext': msg_ext
    })

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
    filepath = app.root_path + output_path
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
        # convert cover object
        cover_mp4 = filepath + file.filename + '.mp4'
        lsb_stego.convert_to_mp4("cover", cover_mp4)
        # convert stego object
        stego_mp4 = filepath + msg_file.filename + '.mp4'
        lsb_stego.convert_to_mp4("stego", stego_mp4)
    else:
        return json.dumps({
            'error': True,
            'data': 'Panjang pesan tidak boleh melibihi panjang cover video!',
        })

    return json.dumps({
        'error': False,
        'cover_video_mp4': output_path + file.filename + '.mp4?' + str(time.time()),
        'stego_video_mp4': output_path + msg_file.filename + '.mp4?' + str(time.time()),
        'stego_video': output_path + 'out_' + file.filename + '?' + str(time.time()),
        'psnr': lsb_stego.calculate_psnr(),
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1111, debug=True)
