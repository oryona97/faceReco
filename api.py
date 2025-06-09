from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import face_recognition
from recognize_faces import load_known_faces, run_recognition



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'known_faces'






# ---------------------
# HTML Page Routes
# ---------------------

@app.route('/')
def index():
    return redirect(url_for('add_user_form'))

@app.route('/add', methods=['GET'])
def add_user_form():
    return render_template('add.html')

@app.route('/manage', methods=['GET'])
def manage_users():
    users = [name for name in os.listdir("known_faces") if os.path.isdir(os.path.join("known_faces", name))]
    return render_template('manage.html', users=users)

# ---------------------
# API Form Handling
# ---------------------

@app.route('/add', methods=['POST'])
def add_user():
    name = request.form.get('name')
    image = request.files.get('image')

    if not name or not image:
        return jsonify({'error': 'Missing name or image'}), 400

    user_dir = os.path.join(app.config['UPLOAD_FOLDER'], name)
    os.makedirs(user_dir, exist_ok=True)

    image_path = os.path.join(user_dir, image.filename)
    image.save(image_path)

    load_known_faces()
    return redirect(url_for('manage_users'))

@app.route('/update/<username>', methods=['POST'])
def update_user(username):
    image = request.files.get('image')
    if not image:
        return jsonify({'error': 'Missing image'}), 400

    user_dir = os.path.join(app.config['UPLOAD_FOLDER'], username)
    if not os.path.exists(user_dir):
        return jsonify({'error': 'User not found'}), 404

    image_path = os.path.join(user_dir, image.filename)
    image.save(image_path)

    load_known_faces()
    return redirect(url_for('manage_users'))

@app.route('/delete/<username>', methods=['POST'])
def delete_user(username):
    user_dir = os.path.join(app.config['UPLOAD_FOLDER'], username)
    if not os.path.exists(user_dir):
        return jsonify({'error': 'User not found'}), 404

    for root, dirs, files in os.walk(user_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        os.rmdir(root)

    load_known_faces()
    return redirect(url_for('manage_users'))

# ---------------------
# Trigger face recognition process
@app.route('/run', methods=['GET'])
def run_recognition_route():
    run_recognition()
    return "Face recognition process completed."

if __name__ == '__main__':
    app.run(debug=True)