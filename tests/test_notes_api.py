import unittest
from unittest.mock import patch

with patch.dict('os.environ', {'DATABASE_URL': 'sqlite:///:memory:'}):
    from app import app, db


class NotesApiTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        with app.app_context():
            self.assertEqual(db.engine.url.drivername, 'sqlite')
            self.assertEqual(db.engine.url.database, ':memory:')
            self.addCleanup(self.reset_database)
            db.create_all()

    def reset_database(self):
        with app.app_context():
            db.engine.dispose()

    def create_note(self):
        response = self.client.post('/api/notes', json={
            'subject': '數學',
            'content': '複習分數',
        })
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def test_note_lifecycle(self):
        note = self.create_note()
        url = f"/api/notes/{note['id']}"
        self.assertEqual(self.client.get('/api/notes').get_json(), [note])

        response = self.client.put(url, json={'content': '複習小數'})
        updated_note = {**note, 'content': '複習小數'}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), updated_note)
        self.assertEqual(self.client.get('/api/notes').get_json(), [updated_note])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, b'')
        self.assertEqual(self.client.get('/api/notes').get_json(), [])
        self.assertEqual(self.client.put(url, json={'subject': '物理'}).status_code, 404)

    def test_create_rejects_invalid_payloads(self):
        for payload in (
            ['subject', 'content'],
            'subject content',
            42,
            {'subject': '數學'},
            {'subject': None, 'content': '複習分數'},
            {'subject': '數學', 'content': ['複習分數']},
            {'subject': '數' * 101, 'content': '複習分數'},
        ):
            with self.subTest(payload=payload):
                response = self.client.post('/api/notes', json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.get_json())

        self.assertEqual(self.client.get('/api/notes').get_json(), [])

    def test_update_rejects_invalid_payloads_without_changing_note(self):
        note = self.create_note()
        url = f"/api/notes/{note['id']}"
        for payload in (
            ['subject', 'content'],
            'subject content',
            42,
            {},
            {'subject': '物理', 'content': None},
            {'subject': 42},
            {'subject': '數' * 101},
        ):
            with self.subTest(payload=payload):
                response = self.client.put(url, json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.get_json())
                self.assertEqual(self.client.get('/api/notes').get_json(), [note])

    def test_write_endpoints_reject_malformed_json(self):
        note = self.create_note()
        for method, url in (
            ('POST', '/api/notes'),
            ('PUT', f"/api/notes/{note['id']}"),
        ):
            with self.subTest(method=method):
                response = self.client.open(
                    url, method=method, data='{', content_type='application/json',
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.get_json())

    def test_accepts_subject_at_length_limit(self):
        subject = '數' * 100
        response = self.client.post('/api/notes', json={'subject': subject, 'content': ''})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()['subject'], subject)
