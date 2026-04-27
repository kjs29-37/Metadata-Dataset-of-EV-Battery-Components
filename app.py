from flask import (Flask, render_template, request, redirect,
                   url_for, flash, send_file, Response, session)
import sqlite3, json, os, io, csv, hashlib
from datetime import date
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'cellbase_secret_key_2026'

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DB_PATH       = os.path.join(BASE_DIR, 'battery_data.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ── Vehicle registry ──────────────────────────────────────────
VEHICLES = [
    {'slug':'tesla',      'name':'Tesla',               'desc':'Model S · Model 3 · Model Y · Cybertruck','tags':['Cells','BMS','Connectors','Busbars'], 'banner':'tesla_banner.jpeg',               'filter':'%tesla%'},
    {'slug':'nissan',     'name':'Nissan Leaf',          'desc':'Gen 1 · 24kWh Platform',                 'tags':['Cells','BMS','Cables','Hardware'],    'banner':'NissanLeaf_banner.webp',          'filter':'%nissan%'},
    {'slug':'chevrolet',  'name':'Chevrolet Bolt',       'desc':'EV · EUV · 60kWh LG Platform',           'tags':['Cells','BMS','Casings','Hardware'],   'banner':'Chevrolet_Bolt_banner.jpg',       'filter':'chevy_bolt%'},
    {'slug':'volkswagen', 'name':'Volkswagen ID.4',      'desc':'MEB Platform · 77kWh',                   'tags':['Cells','BMS','Connectors','Cables'],  'banner':'Volkswagen_ID.4_banner.jpg',      'filter':'%volkswagen%'},
    {'slug':'renault',    'name':'Renault Zoe',          'desc':'Z.E. 50 · 52kWh Platform',               'tags':['Cells','BMS','Cables','Hardware'],    'banner':'RENAULT_ZOE_banner.jpg',          'filter':'%renault%'},
    {'slug':'hyundai',    'name':'Hyundai Ioniq 5',      'desc':'E-GMP Platform · 77.4kWh',               'tags':['Cells','BMS','Connectors','Busbars'], 'banner':'Hyundai_Ioniq_5_banner.webp',     'filter':'%hyundai%'},
    {'slug':'ford',       'name':'Ford Mustang Mach-E',  'desc':'Extended Range · 98.7kWh',               'tags':['Cells','BMS','Cables','Casings'],     'banner':'ford_mustang_mach-e_banner.jpg',  'filter':'%ford%'},
]

# ── Helpers ───────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(f):
    return '.' in f and f.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_component_types():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT type FROM components ORDER BY type").fetchall()
    conn.close()
    return [r['type'] for r in rows]

def get_type_counts():
    conn = get_db()
    rows = conn.execute("SELECT type, COUNT(*) as cnt FROM components WHERE hidden=0 GROUP BY type").fetchall()
    conn.close()
    return {r['type']: r['cnt'] for r in rows}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            flash('Please sign in to access the admin panel.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def init_admin_db():
    """Ensure admin tables and columns exist."""
    conn = get_db()
    # Add hidden column if missing
    try:
        conn.execute("ALTER TABLE components ADD COLUMN hidden INTEGER DEFAULT 0")
    except: pass
    # Add source_url column if missing
    try:
        conn.execute("ALTER TABLE components ADD COLUMN source_url TEXT")
    except: pass
    # Add model column if missing
    try:
        conn.execute("ALTER TABLE components ADD COLUMN model TEXT")
    except: pass
    # Create admin_users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role     TEXT DEFAULT 'admin'
        )
    """)
    # Create default admin if none exists
    existing = conn.execute("SELECT COUNT(*) FROM admin_users").fetchone()[0]
    if existing == 0:
        conn.execute(
            "INSERT INTO admin_users (username, password, role) VALUES (?, ?, ?)",
            ('admin', hash_password('cellbase2026'), 'Super Admin')
        )
        print("Default admin created — username: admin  password: cellbase2026")
    conn.commit()
    conn.close()

# Run on startup
init_admin_db()

# ── Auth routes ───────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM admin_users WHERE username=? AND password=?",
            (username, hash_password(password))
        ).fetchone()
        conn.close()
        if user:
            session['username'] = user['username']
            session['role']     = user['role']
            flash(f'Welcome back, {username}!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out.')
    return redirect(url_for('landing'))

# ── Admin routes ──────────────────────────────────────────────
@app.route('/admin')
@app.route('/admin/')
@login_required
def admin_dashboard():
    conn = get_db()
    total       = conn.execute("SELECT COUNT(*) FROM components").fetchone()[0]
    with_images = conn.execute("SELECT COUNT(*) FROM components WHERE image_path IS NOT NULL AND image_path != ''").fetchone()[0]
    hidden      = conn.execute("SELECT COUNT(*) FROM components WHERE hidden=1").fetchone()[0]
    image_pct   = round((with_images / total * 100)) if total > 0 else 0

    # Type breakdown
    type_rows = conn.execute("""
        SELECT type,
               COUNT(*) as total,
               SUM(CASE WHEN image_path IS NOT NULL AND image_path != '' THEN 1 ELSE 0 END) as with_images,
               SUM(CASE WHEN hidden=1 THEN 1 ELSE 0 END) as hidden
        FROM components GROUP BY type ORDER BY type
    """).fetchall()

    # Vehicle breakdown
    vehicle_breakdown = []
    for v in VEHICLES:
        if v['slug'] == 'chevrolet':
            row = conn.execute("SELECT COUNT(*) as total, SUM(CASE WHEN image_path IS NOT NULL AND image_path != '' THEN 1 ELSE 0 END) as with_images FROM components WHERE id LIKE ?", (v['filter'],)).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) as total, SUM(CASE WHEN image_path IS NOT NULL AND image_path != '' THEN 1 ELSE 0 END) as with_images FROM components WHERE LOWER(manufacturer) LIKE ?", (v['filter'],)).fetchone()
        vehicle_breakdown.append({'name': v['name'], 'total': row['total'] or 0, 'with_images': row['with_images'] or 0})

    # Recent 10 components
    recent = conn.execute("SELECT id, type, manufacturer, model, image_path, hidden FROM components ORDER BY rowid DESC LIMIT 10").fetchall()
    conn.close()

    stats = {
        'total': total, 'with_images': with_images,
        'hidden': hidden, 'image_pct': image_pct,
        'vehicles': len(VEHICLES), 'component_types': len(type_rows)
    }
    return render_template('admin_dashboard.html',
                           stats=stats, type_breakdown=type_rows,
                           vehicle_breakdown=vehicle_breakdown, recent=recent)

@app.route('/admin/components')
@login_required
def admin_components():
    conn    = get_db()
    query   = request.args.get('q','').strip()
    cat     = request.args.get('type','all')
    sql     = "SELECT * FROM components WHERE 1=1"
    params  = []
    if cat and cat != 'all':
        sql += " AND type=?"; params.append(cat)
    if query:
        sql += " AND (id LIKE ? OR manufacturer LIKE ? OR model LIKE ?)"; params.extend([f'%{query}%']*3)
    sql += " ORDER BY type, manufacturer"
    components = conn.execute(sql, params).fetchall()
    conn.close()
    return render_template('admin_components.html',
                           components=components,
                           component_types=get_component_types())

@app.route('/admin/hidden')
@login_required
def admin_hidden():
    conn = get_db()
    components = conn.execute("SELECT * FROM components WHERE hidden=1 ORDER BY type, manufacturer").fetchall()
    conn.close()
    return render_template('admin_hidden.html', components=components)

@app.route('/admin/toggle/<id>', methods=['POST'])
@login_required
def admin_toggle_hide(id):
    conn = get_db()
    current = conn.execute("SELECT hidden FROM components WHERE id=?", (id,)).fetchone()
    if current:
        new_val = 0 if current['hidden'] else 1
        conn.execute("UPDATE components SET hidden=? WHERE id=?", (new_val, id))
        conn.commit()
        action = 'hidden' if new_val else 'made visible'
        flash(f'Component {id} {action} successfully.')
    conn.close()
    return redirect(request.referrer or url_for('admin_components'))

@app.route('/admin/delete/<id>', methods=['POST'])
@login_required
def admin_delete(id):
    conn = get_db()
    conn.execute("DELETE FROM components WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash(f'Component {id} deleted.')
    return redirect(url_for('admin_components'))

# ── Public routes ─────────────────────────────────────────────
@app.route('/')
def landing():
    conn  = get_db()
    total = conn.execute("SELECT COUNT(*) FROM components WHERE hidden=0").fetchone()[0]
    vlist = []
    for v in VEHICLES:
        if v['slug'] == 'chevrolet':
            count = conn.execute("SELECT COUNT(*) FROM components WHERE id LIKE ? AND hidden=0", (v['filter'],)).fetchone()[0]
        else:
            count = conn.execute("SELECT COUNT(*) FROM components WHERE LOWER(manufacturer) LIKE ? AND hidden=0", (v['filter'],)).fetchone()[0]
        vlist.append({**v, 'count': count})
    conn.close()
    return render_template('landing.html', total_components=total, total_vehicles=len(VEHICLES), vehicles=vlist)

@app.route('/browse')
def index():
    conn     = get_db()
    query    = request.args.get('q','').strip()
    category = request.args.get('type','all')
    sql      = "SELECT * FROM components WHERE hidden=0"
    params   = []
    if category and category != 'all':
        sql += " AND type=?"; params.append(category)
    if query:
        sql += " AND (manufacturer LIKE ? OR model LIKE ? OR id LIKE ?)"; params.extend([f'%{query}%']*3)
    sql += " ORDER BY manufacturer, type"
    components  = conn.execute(sql, params).fetchall()
    total_count = conn.execute("SELECT COUNT(*) FROM components WHERE hidden=0").fetchone()[0]
    conn.close()
    return render_template('index.html', components=components,
                           component_types=get_component_types(),
                           type_counts=get_type_counts(), total_count=total_count)

@app.route('/vehicle/<brand>')
def vehicle(brand):
    v = next((x for x in VEHICLES if x['slug'] == brand), None)
    if not v: return "Vehicle not found", 404
    conn     = get_db()
    query    = request.args.get('q','').strip()
    category = request.args.get('type','all')
    if v['slug'] == 'chevrolet':
        sql = "SELECT * FROM components WHERE id LIKE ? AND hidden=0"
        params = [v['filter']]
    else:
        sql = "SELECT * FROM components WHERE LOWER(manufacturer) LIKE ? AND hidden=0"
        params = [v['filter']]
    if category and category != 'all':
        sql += " AND type=?"; params.append(category)
    if query:
        sql += " AND (manufacturer LIKE ? OR model LIKE ? OR id LIKE ?)"; params.extend([f'%{query}%']*3)
    sql += " ORDER BY type, manufacturer"
    components = conn.execute(sql, params).fetchall()
    conn.close()
    return render_template('vehicle.html', components=components,
                           brand=brand, brand_display=v['name'],
                           component_types=get_component_types())

@app.route('/about')
def about():
    return render_template('about.html', title='About — CellBase')

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_component():
    if request.method == 'POST':
        try:
            comp_id      = request.form['id'].strip()
            comp_type    = request.form['type']
            manufacturer = request.form['manufacturer'].strip()
            model        = request.form.get('model','').strip()
            db_image_path = None
            file = request.files.get('image')
            if file and file.filename and allowed_file(file.filename):
                filename  = secure_filename(file.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], comp_type, filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                file.save(save_path)
                db_image_path = f"images/{comp_type}/{filename}"
            default_specs = json.dumps({"note":"Uploaded via CellBase GUI","date_added":date.today().isoformat()})
            conn = get_db()
            conn.execute("INSERT INTO components (id,type,manufacturer,model,specs,image_path,hidden) VALUES (?,?,?,?,?,?,0)",
                         (comp_id,comp_type,manufacturer,model or None,default_specs,db_image_path))
            conn.commit(); conn.close()
            flash('Component added successfully!')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('Error: Component ID already exists.','error')
        except Exception as e:
            flash(f'An error occurred: {e}','error')
    return render_template('add_component.html')

@app.route('/component/<id>')
def view_detail(id):
    conn      = get_db()
    component = conn.execute("SELECT * FROM components WHERE id=?", (id,)).fetchone()
    conn.close()
    if component is None: return "Component not found", 404
    try:    specs_dict = json.loads(component['specs'])
    except: specs_dict = {}
    return render_template('detail.html', component=component, specs=specs_dict)

@app.route('/export/<id>')
def export_json(id):
    conn = get_db()
    c    = conn.execute("SELECT * FROM components WHERE id=?", (id,)).fetchone()
    conn.close()
    if c is None: return "Not found", 404
    data = {"id":c['id'],"type":c['type'],"manufacturer":c['manufacturer'],
            "model":c['model'],"specs":json.loads(c['specs'] or '{}'),
            "image_path":c['image_path'],
            "source_url":c['source_url'] if 'source_url' in c.keys() else None}
    return send_file(io.BytesIO(json.dumps(data,indent=2).encode()),
                     mimetype='application/json', as_attachment=True, download_name=f"{id}.json")

@app.route('/export/all/json')
def export_all_json():
    conn = get_db()
    components = conn.execute("SELECT * FROM components WHERE hidden=0 ORDER BY type, manufacturer").fetchall()
    conn.close()
    dataset = []
    for c in components:
        try:    specs = json.loads(c['specs'] or '{}')
        except: specs = {}
        dataset.append({"id":c['id'],"type":c['type'],"manufacturer":c['manufacturer'],
                        "model":c['model'],"specs":specs,"image_path":c['image_path'],
                        "source_url":c['source_url'] if 'source_url' in c.keys() else None})
    payload = json.dumps({"dataset":"CellBase EV Battery Component Dataset","version":"1.0",
                          "exported":date.today().isoformat(),"total":len(dataset),"components":dataset},indent=2)
    return send_file(io.BytesIO(payload.encode()), mimetype='application/json',
                     as_attachment=True, download_name=f"cellbase_dataset_{date.today().isoformat()}.json")

@app.route('/export/all/csv')
def export_all_csv():
    conn = get_db()
    components = conn.execute("SELECT * FROM components WHERE hidden=0 ORDER BY type, manufacturer").fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id','type','manufacturer','model','image_path','source_url','specs_json'])
    for c in components:
        src = c['source_url'] if 'source_url' in c.keys() else ''
        writer.writerow([c['id'],c['type'],c['manufacturer'],c['model'] or '',
                         c['image_path'] or '',src or '',c['specs'] or ''])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={"Content-Disposition":f"attachment;filename=cellbase_dataset_{date.today().isoformat()}.csv"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)