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
            'question': 'Which dung beetle was worshipped by the ancient Egyptians?',
            'answer': 'Scarab',
            'category': 4,
            'difficulty': 4
        }

        self.quiz = {
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': 3}
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

    # GET QUESTION TEST sucess and failure

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000', json={'category': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # GET CATEGORY TEST sucess and failure

    def test_get_paginated_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['Categories'])

    def test_404_sent_requesting_category_fail(self):
        res = self.client().get('/categories/111')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # DELETE TEST sucess and failure

    def test_delete_question(self):
        res = self.client().delete('/questions/23')
        data = json.loads(res.data)

        deletedQuestions = Question.query.filter(
            Question.id == 23).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['Questions']))
        self.assertEqual(data['The deleted question id is'], 23)
        self.assertTrue(data['Number of questions'])
        self.assertEqual(deletedQuestions, None)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # GET QUESTION BY CATEGORY ID TEST sucess and failure

    def test_get_paginated_questions_by_category(self):
        res = self.client().get('/categories/6/questions')
        data = json.loads(res.data)
        allQuestions = Question.query.filter(
            Question.category == 6).all()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data['questions']))

    def test_404_sent_requesting_question_by_category_fail(self):
        res = self.client().get('/categories/7/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # POST NEW QUESTION TEST sucess and failure

    def test_create_new_question(self):
        res = self.client().post('/newquestions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertTrue(data['answer'])
        self.assertTrue(data['category'])
        self.assertTrue(data['difficulty'])

    def test_405_sent_create_new_question(self):
        res = self.client().post('/categories', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method Not Allowed')

    # SEARCH QUESTION TEST sucess and failure

    def test_get_question_search(self):
        res = self.client().post('/questions',
                                 json={'searchTerm': 'what'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 8)

    def test_get_question_search_without_results(self):
        res = self.client().post('/questions',
                                 json={'searchTerm': 'HELOO'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)

    # QUIZ TEST sucess and failure

    def test_post_quiz(self):
        res = self.client().post('/quizzes',
                                 json=self.quiz)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_404_sent_requesting_quiz(self):
        res = self.client().post('/quizzes/1',
                                 json=self.quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
