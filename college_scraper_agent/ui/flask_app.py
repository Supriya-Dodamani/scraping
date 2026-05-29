import sys
from pathlib import Path
import json
from io import StringIO

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flask import Flask, render_template, request, jsonify
import pandas as pd

from agents.college_agent import CollegeScraperAgent
from utils.exporter import export_data

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/scrape', methods=['POST'])
def scrape():
    try:
        data = request.json
        scope = data.get('scope', 'country')
        city = data.get('city', '')
        state = data.get('state', '')
        courses = data.get('courses', 'MBA,MCA,BCA,BE,BTech,Diploma')
        max_colleges = int(data.get('max_colleges', 50))
        delay = float(data.get('delay', 2.0))

        courses_list = [c.strip() for c in courses.split(',') if c.strip()]

        agent = CollegeScraperAgent()
        colleges = agent.run(
            scope=scope,
            city=city,
            state=state,
            courses=courses_list,
            max_colleges=max_colleges,
            delay=delay
        )

        if not colleges:
            return jsonify({'success': False, 'message': 'No colleges found'}), 400

        records = [c.to_flat_dict() for c in colleges]
        df = pd.DataFrame(records)

        return jsonify({
            'success': True,
            'count': len(colleges),
            'data': df.to_dict('records'),
            'csv': df.to_csv(index=False),
            'json': [c.model_dump() for c in colleges]
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/download/<format_type>', methods=['POST'])
def download(format_type):
    try:
        data = request.json
        records = data.get('data', [])
        df = pd.DataFrame(records)

        if format_type == 'csv':
            return df.to_csv(index=False), 200, {'Content-Disposition': 'attachment; filename=colleges.csv'}
        elif format_type == 'json':
            return json.dumps(records, indent=2), 200, {'Content-Disposition': 'attachment; filename=colleges.json'}
        else:
            return jsonify({'error': 'Invalid format'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
