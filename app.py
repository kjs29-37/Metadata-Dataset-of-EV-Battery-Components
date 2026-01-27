from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import sqlite3
import json
import os
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flash_messages'  # Required for error messages

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'battery_data.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- HELPER FUNCTIONS ---

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name (e.g., row['id'])
    return conn

def allowed_file(filename):
    """Checks if the uploaded file is a valid image."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ROUTES ---

@app.route('/')
def index():
    conn = get_db()
    
    # Search & Filter Logic
    query = request.args.get('q')
    category = request.args.get('type')
    
    sql = "SELECT * FROM components WHERE 1=1"
    params = []
    
    if category and category != 'all':
        sql += " AND type = ?"
        params.append(category)
        
    if query:
        sql += " AND (manufacturer LIKE ? OR model LIKE ? OR id LIKE ?)"
        params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
        
    components = conn.execute(sql, params).fetchall()
    conn.close()
    
    return render_template('index.html', components=components)

@app.route('/add', methods=['GET', 'POST'])
def add_component():
    if request.method == 'POST':
        try:
            # 1. Get Form Data
            comp_id = request.form['id']
            comp_type = request.form['type']
            manufacturer = request.form['manufacturer']
            
            # 2. Handle Image Upload
            if 'image' not in request.files:
                flash('No file part')
                return redirect(request.url)
            
            file = request.files['image']
            
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
                
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # Save to specific subfolder (e.g., static/images/cells/)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], comp_type, filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True) # Create folder if missing
                file.save(save_path)
                
                # 3. Save to Database
                # Store path relative to 'static' so HTML can find it
                db_image_path = f"images/{comp_type}/{filename}"
                
                # Create a basic JSON structure for specs since this is a quick add
                default_specs = json.dumps({"note": "Uploaded via Web GUI", "date_added": "2026-01-20"})
                
                conn = get_db()
                conn.execute(
                    "INSERT INTO components (id, type, manufacturer, specs, image_path) VALUES (?, ?, ?, ?, ?)",
                    (comp_id, comp_type, manufacturer, default_specs, db_image_path)
                )
                conn.commit()
                conn.close()
                flash('Component added successfully!')
                return redirect(url_for('index'))
            else:
                flash('Invalid file type. Allowed: JPG, PNG')
                return redirect(request.url)
                
        except sqlite3.IntegrityError:
            flash(f'Error: Component ID {comp_id} already exists!')
        except Exception as e:
            flash(f'An error occurred: {e}')
            
    return render_template('add_component.html')

@app.route('/component/<id>')
def view_detail(id):
    conn = get_db()
    component = conn.execute("SELECT * FROM components WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    if component is None:
        return "Component not found", 404
        
    # Parse the JSON specs so the template can loop through them
    try:
        specs_dict = json.loads(component['specs'])
    except:
        specs_dict = {} # Fallback if specs are empty
    
    return render_template('detail.html', component=component, specs=specs_dict)

@app.route('/export/<id>')
def export_json(id):
    """
    (Bonus 80% Feature) 
    Downloads the specific component data as a JSON file.
    """
    conn = get_db()
    component = conn.execute("SELECT * FROM components WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    if component is None:
        return "Component not found", 404

    # Convert database row to a clean dictionary
    data = {
        "id": component['id'],
        "type": component['type'],
        "manufacturer": component['manufacturer'],
        "specs": json.loads(component['specs']),
        "image_path": component['image_path']
    }
    
    # Create a file in memory to send to user
    return send_file(
        io.BytesIO(json.dumps(data, indent=2).encode()),
        mimetype='application/json',
        as_attachment=True,
        download_name=f"{id}.json"
    )

if __name__ == '__main__':
    app.run(debug=True)