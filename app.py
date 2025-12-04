"""
Tournament History Management System
トーナメント大会の履歴を管理するWebアプリケーション
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FOLDER'] = 'data'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def load_tournaments():
    """Load all tournaments from data file"""
    data_file = os.path.join(app.config['DATA_FOLDER'], 'tournaments.json')
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_tournaments(tournaments):
    """Save tournaments to data file"""
    data_file = os.path.join(app.config['DATA_FOLDER'], 'tournaments.json')
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(tournaments, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    """Main page - list all tournaments"""
    tournaments = load_tournaments()
    # Sort by date, newest first
    tournaments.sort(key=lambda x: x['date'], reverse=True)
    return render_template('index.html', tournaments=tournaments)


@app.route('/tournament/<tournament_id>')
def view_tournament(tournament_id):
    """View specific tournament details"""
    tournaments = load_tournaments()
    tournament = next((t for t in tournaments if t['id'] == tournament_id), None)
    
    if not tournament:
        return "大会が見つかりません", 404
    
    return render_template('tournament_detail.html', tournament=tournament)


@app.route('/add', methods=['GET', 'POST'])
def add_tournament():
    """Add new tournament"""
    if request.method == 'GET':
        return render_template('add_tournament.html')
    
    # Handle POST request
    try:
        # Get form data
        tournament_name = request.form.get('tournament_name', '').strip()
        date = request.form.get('date', '').strip()
        organizer = request.form.get('organizer', '').strip()
        first_place = request.form.get('first_place', '').strip()
        second_place = request.form.get('second_place', '').strip()
        third_place = request.form.get('third_place', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validate required fields
        if not all([tournament_name, date, organizer, first_place]):
            return jsonify({'error': '必須項目を入力してください'}), 400
        
        # Handle image upload
        bracket_image = None
        if 'bracket_image' in request.files:
            file = request.files['bracket_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add UUID to filename to avoid conflicts
                file_id = str(uuid.uuid4())[:8]
                ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"{file_id}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                file.save(file_path)
                bracket_image = new_filename
        
        # Create tournament object
        tournament = {
            'id': str(uuid.uuid4()),
            'tournament_name': tournament_name,
            'date': date,
            'organizer': organizer,
            'first_place': first_place,
            'second_place': second_place,
            'third_place': third_place,
            'description': description,
            'bracket_image': bracket_image,
            'created_at': datetime.now().isoformat()
        }
        
        # Load existing tournaments and add new one
        tournaments = load_tournaments()
        tournaments.append(tournament)
        save_tournaments(tournaments)
        
        return jsonify({
            'success': True,
            'tournament_id': tournament['id'],
            'redirect_url': url_for('view_tournament', tournament_id=tournament['id'])
        })
    
    except Exception as e:
        return jsonify({'error': f'エラーが発生しました: {str(e)}'}), 500


@app.route('/edit/<tournament_id>', methods=['GET', 'POST'])
def edit_tournament(tournament_id):
    """Edit existing tournament"""
    tournaments = load_tournaments()
    tournament = next((t for t in tournaments if t['id'] == tournament_id), None)
    
    if not tournament:
        return "大会が見つかりません", 404
    
    if request.method == 'GET':
        return render_template('edit_tournament.html', tournament=tournament)
    
    # Handle POST request
    try:
        # Update tournament data
        tournament['tournament_name'] = request.form.get('tournament_name', '').strip()
        tournament['date'] = request.form.get('date', '').strip()
        tournament['organizer'] = request.form.get('organizer', '').strip()
        tournament['first_place'] = request.form.get('first_place', '').strip()
        tournament['second_place'] = request.form.get('second_place', '').strip()
        tournament['third_place'] = request.form.get('third_place', '').strip()
        tournament['description'] = request.form.get('description', '').strip()
        
        # Handle new image upload
        if 'bracket_image' in request.files:
            file = request.files['bracket_image']
            if file and file.filename and allowed_file(file.filename):
                # Delete old image if exists
                if tournament.get('bracket_image'):
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], tournament['bracket_image'])
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                # Save new image
                filename = secure_filename(file.filename)
                file_id = str(uuid.uuid4())[:8]
                ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"{file_id}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                file.save(file_path)
                tournament['bracket_image'] = new_filename
        
        tournament['updated_at'] = datetime.now().isoformat()
        
        # Save updated tournaments
        save_tournaments(tournaments)
        
        return jsonify({
            'success': True,
            'tournament_id': tournament['id'],
            'redirect_url': url_for('view_tournament', tournament_id=tournament['id'])
        })
    
    except Exception as e:
        return jsonify({'error': f'エラーが発生しました: {str(e)}'}), 500


@app.route('/delete/<tournament_id>', methods=['POST'])
def delete_tournament(tournament_id):
    """Delete tournament"""
    tournaments = load_tournaments()
    tournament = next((t for t in tournaments if t['id'] == tournament_id), None)
    
    if not tournament:
        return jsonify({'error': '大会が見つかりません'}), 404
    
    # Delete image file if exists
    if tournament.get('bracket_image'):
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], tournament['bracket_image'])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Remove tournament from list
    tournaments = [t for t in tournaments if t['id'] != tournament_id]
    save_tournaments(tournaments)
    
    return jsonify({'success': True, 'redirect_url': url_for('index')})


if __name__ == '__main__':
    import sys
    
    if '--production' in sys.argv or os.environ.get('FLASK_ENV') == 'production':
        print("Error: For production, use gunicorn instead:")
        print("  gunicorn -w 4 -b 0.0.0.0:5001 app:app")
        sys.exit(1)
    
    print("Starting Tournament History System...")
    print("Open your browser to: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
