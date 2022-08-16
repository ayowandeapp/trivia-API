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
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
        res=self.client().get('/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['total_questions'])
        self.assertEqual(len(data['questions']))
        self.assertEqual(data['categories'])

    def test_404_sent_requesting_beyound_valid_page(self):
        res=self.client().get('/questions?page=1000')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)        
        self.assertEqual(data['message'], 'reource not found')

    def test_get_categories_success(self):
        res=self.client().get('/categories')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
    def test_get_categories_failure(self):
        res=self.client().get('/categories')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'], False)


    def test_delete_question(self):
        res=self.client().delete('/questions/14')
        data=json.loads(res.data)
        question=Question.query.filter(Question.id==14).one_or_none()
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],14)

        self.assertEqual(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question,None)
    def test_422_if_question_does_not_exist(self):
        res=self.client().delete('/questions/1000')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['message'],False)        
        self.assertEqual(data['message'], 'Unprocessable')

    def test_create_new_question(self):
        new_question= {
        'question':'new question',
        'answer':'new answer',
        'difficulty':1,
        'category':1
        }
        previous_total = len(Question.query.all())
        res = self.client().post('/questions',json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['total_questions'],previous_total+1)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
    def test_405_if_book_creation_not_allowed(self):
        new_question= {
        'question':'new question',
        'answer':'new answer',
        'difficulty':1,
        'category':1
        }
        res = self.client().post('/questions',json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,405)
        self.assertEqual(data['message'],False)
        self.assertTrue(data['message'], 'method not allowed')
        self.assertTrue(len(data['questions']))

    def test_get_question_search_with_results(self):
        res = self.client().post('/questions/search',json=('searchTerm':'which'))
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['total_questions'])
        self.assertEqual(data['questions'],9)

    def test_get_question_search_without_results(self):
        res = self.client().post('/questions/search',json=('searchTerm':''))
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['message'],False)
        self.assertEqual(data['total_questions'],0)
        self.assertTrue(len(data['questions']),0)

    def test_get_question_by_category(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
    def test_404_if_unable_get_question_by_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['message'],False)
        self.assertEqual(data['message'],"resource not found")

    def test_get_quiz(self):
        quiz={'quiz_category':{'type':'Science','id':15},'previous_questions':[]}
        res = self.client().get('/quizzes',json=quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
    def test_422_iget_quiz(self):
        #quiz={'quiz_category':{'type':'Science','id':55},'previous_questions':[]}
        res = self.client().get('/quizzes',json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['message'],False)
        self.assertEqual(data['message'],"Unable to Process")

    




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()