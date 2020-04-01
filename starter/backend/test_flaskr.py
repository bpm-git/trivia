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

        # Question for performing test
        self.new_question = {
            'question': 'Who is the founder of Disney?',
            'answer': 'Walt Disney',
            'difficulty': 3,
            'category': '5'
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

    
    def test_delete_question(self):
        """ Test for deleting a question """

        init_question = Question.query.all()

        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],
                            category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()
        qid = question.id

        response = self.client().delete('/questions/{}'.format(qid))
        body = json.loads(response.data)

        final_question = Question.query.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertEqual(body['deleted'], qid)
        self.assertTrue(len(init_question) == len(final_question))

        
    def test_create_new_question(self):
        """ Test for creating new question """
        response = self.client().post('/questions', json=self.new_question)
        body = json.loads(response.data)

        question = Question.query.filter_by(id=body['created']).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertIsNotNone(question)
    
    def test_create_new_question_fails(self):
        """ Test for new question creation failure """
        
        init_question = Question.query.all()

        response = self.client().post('/questions', json={})
        body = json.loads(response.data)

        final_question = Question.query.all()


        self.assertEqual(response.status_code, 422)
        self.assertEqual(body['success'], False)
        self.assertTrue(len(init_question) == len(final_question))
    
    def test_search_question(self):
        """ Test for searching question """

        response = self.client().post('/questions',json={'searchTerm': 'Tom'})
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertEqual(body['total_questions'], 1)

    def test_search_question_failure(self):
        """ Test for searching question failure"""

        response = self.client().post('/question', json={"searchTerm": "123ABC"})
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['message'], 'resource not found')


    def test_questions_by_category(self):
        """ Test for listing questions by category """

        response = self.client().get('/categories/1/questions')
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertNotEqual(len(body['questions']), 0)
        self.assertNotEqual(len(body['category']), 'Science')

    def test_questions_by_category_failure(self):
        """ Test for listing questions by category """

        response = self.client().get('/categories/10/questions')
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(body['success'], False)
        self.assertNotEqual(len(body['message']), 'resource not found')

    
    def test_quiz(self):
        """ Test for quiz """

        response = self.client().post('/quizzes', json={"previous_questions": "",
                                                         "quiz_category": {"type": "Sports", "id": "6"}})
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertNotEqual(body['question']['id'], 28)
        self.assertNotEqual(body['question']['id'], 29)
        self.assertTrue(body['question'])
        self.assertEqual(body['question']['category'], 6)

    def test_quiz_failure(self):
        """ Test for quiz failure """

        response = self.client().post('/quizzes', json={})
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['message'], 'bad request')
    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()