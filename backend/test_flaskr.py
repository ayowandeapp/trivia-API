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
        self.DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin')
        self.DB_NAME = os.getenv('DB_NAME', 'trivia')
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME)
        #self.database_path = "postgresql://{}/{}".format(self.DB_HOST, self.database_name)
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
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])
    def test_404_sent_requesting_beyound_valid_page(self):
        res=self.client().get('/questions?page=1000')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)        
        self.assertTrue(data['message'], 'reource not found')

    def test_get_categories_success(self):
        res=self.client().get('/categories')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
    def test_get_categories_failure(self):
        res=self.client().get('/categories/99999')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)        
        self.assertTrue(data['message'], 'reource not found')

    def test_delete_question(self):
        new_question= {
        'question':'new question',
        'answer':'new answer',
        'difficulty':1,
        'category':1
        }
        question=Question(question='new question',answer= 'new answer',difficulty=1,category=1)
        question.insert()
        q_id=question.id
        res=self.client().delete(f'/questions/{q_id}')
        data=json.loads(res.data)
        question=Question.query.filter(Question.id==q_id).one_or_none()
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],q_id)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question,None)
    def test_422_if_question_does_not_exist(self):
        res=self.client().delete('/questions/1000')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)        
        self.assertTrue(data['message'], 'Unable to Process this Request')

    def test_create_new_question(self):
        new_question= {
        'question':'new question',
        'answer':'new answer',
        'difficulty':3,
        'category':3
        }
        previous_total = len(Question.query.all())
        res = self.client().post('/questions',json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['total_questions'],previous_total+1)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
    def test_422_if_book_creation_not_allowed(self):
        new_question= {
        'question':'new question',
        'answer':'new answer',
        'difficulty':3
        }
        res = self.client().post('/questions',json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertTrue(data['message'], 'Unable to Process this Request')

    def test_get_question_search_with_results(self):
        search= {'searchTerm':'which'}
        res = self.client().post('/questions',json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
    def test_get_question_search_without_results(self):
        res = self.client().post('/questions',json={'searchTerm':'############'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertTrue(data['message'], 'Not Found')

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
        self.assertEqual(data['success'],False)
        self.assertTrue(data['message'],"Not Found")

    def test_get_quiz(self):
        quiz={'quiz_category':{'type':'Entertainment','id':2},'previous_questions':[4,6]}
        res = self.client().post('/quizzes',json=quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])
    def test_422_get_quiz(self):
        #quiz={'quiz_category':{'type':'Science','id':55},'previous_questions':[]}
        res = self.client().post('/quizzes',json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertTrue(data['message'],"Unable to Process")


   




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()