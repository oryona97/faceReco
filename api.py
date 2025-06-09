from flask import Flask, request, jsonify
import os
import face_recognition
from recognize_faces import load_known_faces

app = Flask(__name__)

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    image = request.files.get('image')

    if not name or not image:
        return jsonify({'error': 'Missing name or image'}), 400

    user_dir = os.path.join("known_faces", name)
    os.makedirs(user_dir, exist_ok=True)

    image_path = os.path.join(user_dir, image.filename)
    image.save(image_path)

    load_known_faces()

    return jsonify({'message': f'User {name} added successfully.'}), 200

@app.route('/list_users', methods=['GET'])
def list_users():
    users = [name for name in os.listdir("known_faces") if os.path.isdir(os.path.join("known_faces", name))]
    return jsonify({'users': users}), 200

@app.route('/remove_user/<username>', methods=['DELETE'])
def remove_user(username):
    user_dir = os.path.join("known_faces", username)
    if not os.path.exists(user_dir):
        return jsonify({'error': 'User not found'}), 404

    for root, dirs, files in os.walk(user_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        os.rmdir(root)

    load_known_faces()
    return jsonify({'message': f'User {username} removed successfully.'}), 200

@app.route('/update_user/<username>', methods=['POST'])
def update_user(username):
    image = request.files.get('image')
    if not image:
        return jsonify({'error': 'Missing image'}), 400

    user_dir = os.path.join("known_faces", username)
    if not os.path.exists(user_dir):
        return jsonify({'error': 'User not found'}), 404

    image_path = os.path.join(user_dir, image.filename)
    image.save(image_path)

    load_known_faces()
    return jsonify({'message': f'User {username} updated successfully.'}), 200

if __name__ == '__main__':
    app.run(port=5000)