# Dropzone Action Info
# Name: Qiniu
# Description: Upload images to qiniu.com
# Handles: Files
# Creator: Su Yan
# URL: http://yansu.org
# OptionsNIB: ExtendedLogin
# Events: Clicked, Dragged
# KeyModifiers: Command, Option, Control, Shift
# SkipConfig: No
# RunsSandboxed: No
# Version: 1.2.1
# UniqueID: 0830
# MinDropzoneVersion: 3.5
# Modify: Mush Mo <mush@pandorica.io>

import os
import sys
import commands
import shutil
import hashlib
import imghdr
import webbrowser
from qiniu import Auth
from qiniu import put_file
from qiniu import BucketManager

reload(sys)
sys.setdefaultencoding('utf8')
query = None


def getAuth():
    global query
    if query is not None:
        return query
    access_key = os.environ['username']
    secret_key = os.environ['password']
    query = Auth(access_key, secret_key)
    return query


def isFileExist(file_name):
    # check if file already exist
    bucket_name = os.environ['server']
    bucket = BucketManager(getAuth())
    ret, info = bucket.stat(bucket_name, file_name)
    if ret is not None:
        return True
    else:
        return False


def uploadFile(file_path, file_name):
    qiniu_auth = getAuth()
    bucket_name = os.environ['server']

    if isFileExist(file_name):
        dz.fail("Filename already exist")
    if 'remote_path' in os.environ:
        file_name = '{}/{}'.format(os.environ['remote_path'], file_name)

    token = qiniu_auth.upload_token(bucket_name, file_name)
    ret, info = put_file(token, file_name, file_path)

    if info.status_code == 200:
        root_url = os.environ.get('root_url', '')
        base_url = '{}/{}'.format(root_url, file_name)
        return base_url
    else:
        return False


def dragged():
    dz.begin("Starting uploading...")
    dz.determinate(True)
    dz.percent(10)

    # keep origin name
    file_path = items[0]  # noqa
    file_name = os.path.basename(file_path)
    base_url = uploadFile(file_path, file_name)

    if base_url:
        dz.finish("Upload Completed")
        dz.percent(100)
        dz.url(base_url)
    else:
        dz.fail("Upload Failed")
        dz.percent(100)
        dz.url(False)


def clicked():
    dz.percent(10)

    file_path = dz.temp_folder() + '/qiniu_img_cache'
    current_path = os.path.dirname(os.path.realpath(__file__))
    command = '"%s/pngpaste" "%s"' % (current_path, file_path)
    status, output = commands.getstatusoutput(command)
    if (status != 0):
        webbrowser.open("https://portal.qiniu.com/bucket/" +
                        os.environ['server'] + "/resource")
        dz.fail(output)

    with open(file_path) as f_img:
        file_name = hashlib.md5(f_img.read()).hexdigest()
    file_name = file_name + '.' + imghdr.what(file_path)

    while True:
        if isFileExist(file_name):
            file_name = dz.inputbox(
                "Filename already exist", "Enter filename without suffix:")
            file_name = file_name + '.' + imghdr.what(file_path)
        else:
            break

    dest_path = '%s/%s' % (os.path.dirname(file_path), file_name)
    shutil.move(file_path, dest_path)

    dz.begin("Starting uploading...")
    dz.determinate(True)

    base_url = uploadFile(dest_path, file_name)
    if (base_url):
        dz.finish("Upload Completed")
        dz.percent(100)
        dz.url(base_url)
    else:
        dz.fail("Upload Failed")
        dz.percent(100)
        dz.url(False)
