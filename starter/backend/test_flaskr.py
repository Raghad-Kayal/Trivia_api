import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        #self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)

        self.database_path = "postgres://{}@{}/{}".format(
            'postgres:111', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'how old are you',
            'answer': '24',
            'category': 1,
            'difficulty': 0
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['Number of questions'])
        self.assertTrue(len(data['Questions']))

    def test_get_paginated_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['Categories'])

    def test_delete_question(self):
        res = self.client().delete('/questions/62')
        data = json.loads(res.data)

        deletedQuestions = Question.query.filter(
            Question.id == 62).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['The deleted question id is'], 62)
        self.assertTrue(data['Number of questions'])
        self.assertTrue(len(data['Questions']))
        self.assertEqual(deletedQuestions, None)

    def test_get_paginated_questions_by_category(self):
        res = self.client().get('/categories/6')
        data = json.loads(res.data)
        allQuestions = Question.query.filter(
            Question.category == 6).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['Category id'], 6)
        self.assertTrue(data['Questions'])

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['Number of questions'])
        self.assertTrue(len(data['Questions']))

    def test_get_question_search(self):
        res = self.client().post('/search_questions',
                                 json={'theQuestion': 'what'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total question'])
        self.assertEqual(len(data['question']), 7)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
