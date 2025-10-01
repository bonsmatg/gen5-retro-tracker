from flask import Flask, request, jsonify
import os
import requests
import logging
import json
from datetime import datetime
from pathlib import Path

try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except Exception:
    FIRESTORE_AVAILABLE = False

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Config from env
JARVIS_TOKEN = os.getenv('JARVIS_TOKEN', 'changeme')
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL', '')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
CHAINLINK_URL = os.getenv('CHAINLINK_URL', '')  # e.g. http://chainlink:6688
CHAINLINK_API_TOKEN = os.getenv('CHAINLINK_API_TOKEN', '')
SPARK_SUBMIT_URL = os.getenv('SPARK_SUBMIT_URL', 'http://spark:8080')
DATA_DIR = Path(os.getenv('JARVIS_DATA_DIR', './data'))
DATA_DIR.mkdir(parents=True, exist_ok=True)

if FIRESTORE_AVAILABLE:
    db = firestore.Client()

# Helpers
def check_auth(req):
    auth = req.headers.get('Authorization','')
    if auth.startswith('Bearer '):
        token = auth.split(' ',1)[1]
        return token == JARVIS_TOKEN
    return False

def write_log(collection, doc):
    doc['timestamp'] = datetime.utcnow().isoformat()
    if FIRESTORE_AVAILABLE:
        try:
            db.collection(collection).add(doc)
            logging.info('Wrote to Firestore: %s/%s', collection, doc.get('task',''))
            return True
        except Exception as e:
            logging.warning('Firestore write failed: %s', e)
    # fallback to local file
    try:
        p = DATA_DIR / f"{collection}.json"
        arr = []
        if p.exists():
            arr = json.loads(p.read_text())
        arr.append(doc)
        p.write_text(json.dumps(arr, indent=2))
        logging.info('Wrote to local file: %s', p)
        return True
    except Exception as e:
        logging.error('Local write failed: %s', e)
        return False

def enqueue_spark_job(job_payload):
    try:
        url = os.getenv('SPARK_JOB_API', SPARK_SUBMIT_URL + '/submit')
        r = requests.post(url, json=job_payload, timeout=10)
        logging.info('Spark job submitted, status=%s', r.status_code)
        return r.status_code == 200
    except Exception as e:
        logging.warning('Failed to submit Spark job: %s', e)
        return False

def trigger_chainlink_job(spec):
    if not CHAINLINK_URL or not CHAINLINK_API_TOKEN:
        logging.info('Chainlink not configured, skipping')
        return False
    try:
        url = CHAINLINK_URL.rstrip('/') + '/v2/specs'
        headers = {'Content-Type':'application/json', 'Authorization': f'Bearer {CHAINLINK_API_TOKEN}'}
        r = requests.post(url, json=spec, headers=headers)
        logging.info('Chainlink spec POST status=%s', r.status_code)
        return r.status_code in (200,201)
    except Exception as e:
        logging.warning('Chainlink trigger failed: %s', e)
        return False

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'time': datetime.utcnow().isoformat()}), 200

@app.route('/api/v1/command', methods=['POST'])
def command():
    if not check_auth(request):
        return jsonify({'error':'unauthorized'}), 401
    data = request.get_json() or {}
    name = data.get('name')
    args = data.get('args', {})

    # Routine: Finance Summary
    if name == 'routine:finance:summary':
        account = args.get('account','main')
        period = args.get('period','today')
        doc = {'task':'finance_summary','account':account,'period':period}
        write_log('routine_logs', doc)
        # queue analytics job to Spark
        job = {'type':'finance_summary','account':account,'period':period}
        enqueue_spark_job(job)
        # optionally trigger an on-chain verification via Chainlink job spec
        if args.get('chainlink_verify'):
            spec = {
                'initiators':[{'type':'web'}],
                'tasks':[{'type':'httpget','params':{'get': args.get('verify_url','https://api.example.com/verify')}}, {'type':'jsonparse','params':{'query':'$.ok'}}]
            }
            trigger_chainlink_job(spec)
        return jsonify({'status':'ok','detail':'finance summary queued/written'}), 200

    # Routine: Physical Log
    if name == 'routine:physical:log':
        ptype = args.get('type','workout')
        duration = args.get('duration_min')
        calories = args.get('calories')
        doc = {'task':'physical_log','type':ptype,'duration_min':duration,'calories':calories}
        write_log('routine_logs', doc)
        # small analytics task
        enqueue_spark_job({'type':'physical_aggregate','payload':doc})
        return jsonify({'status':'ok'}), 200

    # Routine: Mental Checkin
    if name == 'routine:mental:checkin':
        mood = args.get('mood')
        notes = args.get('notes','')
        doc = {'task':'mental_checkin','mood':mood,'notes':notes}
        write_log('routine_logs', doc)
        # could trigger recommendations
        return jsonify({'status':'ok'}), 200

    # Routine: Emotional Journal
    if name == 'routine:emotional:journal':
        entry = args.get('entry','')
        private = args.get('private', True)
        collection = 'private_journal' if private else 'routine_logs'
        doc = {'task':'emotional_journal','entry':entry}
        write_log(collection, doc)
        return jsonify({'status':'ok'}), 200

    # Fallback examples from earlier
    if name == 'repo:pull':
        owner = args.get('owner')
        repo = args.get('repo')
        if owner and repo and GITHUB_TOKEN:
            url = f'https://api.github.com/repos/{owner}/{repo}/dispatches'
            headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
            payload = {'event_type': 'jarvis_repo_pull', 'client_payload': args}
            r = requests.post(url, json=payload, headers=headers)
            return jsonify({'status': 'dispatched', 'github_status': r.status_code}), 200
        return jsonify({'error':'missing owner/repo or GITHUB_TOKEN'}), 400

    if name == 'notify:slack':
        text = args.get('text','Jarvis notification')
        if not SLACK_WEBHOOK:
            return jsonify({'error': 'no slack webhook configured'}), 400
        r = requests.post(SLACK_WEBHOOK, json={'text': text})
        return jsonify({'status':'sent','slack_status': r.status_code}), 200

    return jsonify({'error':'unknown command'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8000')))