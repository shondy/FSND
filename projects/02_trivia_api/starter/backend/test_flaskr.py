import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db
from sqlalchemy import func
from sqlalchemy.sql import text as sa_text


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('helen',
                                                               'pop23',
                                                               'localhost:5432',
                                                               self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'what is the largest active volcano in europe',
            'answer': 'Etna ',
            'category': '3',
            'difficulty': '1'

        }

        # binds the app to the current context
        # https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/
        # https://stackoverflow.com/questions/20036520/what-is-the-purpose-of-flasks-context-stacks
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    # Unit Tests

    def test_get_categories(self):
        """Gets the /api/categories endpoint and checks valid results"""
        res = self.client().get('/api/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)

    def test_404_get_categories_from_empty_table(self):
        """Test rising of 404 error if requested all categories from
        empty Category table
        """
        num_rows_deleted = db.session.query(Category).delete()
        #db.session.commit()
        db.session.flush()
        res = self.client().get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

        db.session.rollback()

    def test_get_all_questions(self):
        """Get all questions for first page (default value for a page number), check that we
        received first 10 questions, all categories and total number of questions"""
        res = self.client().get('/api/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['questions'][0]['id'], 5)

    def test_get_questions_paginated(self):
        """Test the pagination of questions, get questions for page 2"""
        res = self.client().get('/api/questions?page=2')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)
        self.assertEqual(data['total_questions'], 19)
        # since total amount of questions is 19, questions per page = 10 =>
        # there are 9 questions on page 2
        self.assertEqual(len(data['questions']), 9)
        self.assertEqual(data['questions'][0]['id'], 15)

    def test_404_get_questions_beyond_valid_page(self):
        """ Test rising of 404 error if requested page of questions doesn't exist """
        res = self.client().get('/api/questions?page=1000')
        # res = self.client().get('/books?page=1', json={'rating': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_new_question(self):
        """Test creating of the question which will be add to the end of the questions table,
        and therefore will appear at the end of the last page of the questions list """
        questions = Question.query.all()
        num_questions_before = len(questions)
        res = self.client().post('/api/questions', json=self.new_question)
        data = json.loads(res.data)
        questions = Question.query.all()
        num_questions_after = len(questions)
        max_id = db.session.query(func.max(Question.id)).scalar()
        self.assertEqual(num_questions_after, num_questions_before + 1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['added'], max_id)

    def test_400_if_question_parameter_is_not_specified(self):
        """Test creating of a question which has some unspecified parameters,
         should return 400 error"""
        self.new_question["answer"] = ""
        res = self.client().post('/api/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bed request')
        self.new_question["answer"] = "Etna"

    def test_get_questions_containing_searchTerm(self):
        """Test searching for a term in questions.question"""
        res = self.client().post('/api/questions', json={'searchTerm': 'What'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(len(data['questions']), 8)
        self.assertEqual(data['questions'][0]['id'], 9)

    def test_400_get_questions_containing_long_searchTerm(self):
        """Test searching for a term longer than 1000 symbols
        in questions.question, should return 400 error"""
        res = self.client().post('/api/questions', json={'searchTerm': 'a'*1001})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bed request')

    def test_delete_question(self):
        """Test deleting of the question with maximum id"""
        max_id = db.session.query(func.max(Question.id)).scalar()
        res = self.client().delete('/api/questions/' + str(max_id))
        data = json.loads(res.data)
        book = Question.query.filter(Question.id == max_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], max_id)
        self.assertEqual(book, None)

    def test_404_if_question_does_not_exist(self):
        """Test deleting of a question that doesn't exist, should return 404 error"""
        res = self.client().delete('/questions/3')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_by_category(self):
        """Test getting questions based on category"""
        res = self.client().get('/api/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['totalQuestions'], 4)
        self.assertEqual(data['currentCategory'], 2)

    def test_404_if_questions_for_category_do_not_exist(self):
        """Test deleting of a question that doesn't exist, should return 404 error"""
        # Get questions for category 100 (doesn't exist, should 404)
        res = self.client().get('/api/categories/100/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_quiz(self):
        """Test finding a random question for a quiz from the given category which
        doesn't belong to the list of given questions  """
        quiz_category = {"type": "History", "id": 4}
        previous_questions = [5, 9, 16, 17]
        res = self.client().post('/api/quizzes', \
                                 json={"previous_questions": previous_questions, \
                                       "quiz_category": quiz_category})

        data = json.loads(res.data)
        #print("data", data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question']['id'] in [12, 23])

    def test_quiz_is_over(self):
        """Test returns only a success status without a question
        if all questions from a given category belong to
        the list of previous questions that can't be used for quiz """
        quiz_category = {"type": "History", "id": 4}
        previous_questions = [5, 9, 12, 23, 16, 17]
        res = self.client().post('/api/quizzes', \
                                 json={"previous_questions": previous_questions, \
                                       "quiz_category": quiz_category})
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertNotIn('question', data)

    def test_create_quiz_without_previous_questions(self):
        """Test finding a random question for quiz from the given category without specifying
        a list of questions that can not be chosen """
        quiz_category = {"type": "History", "id": 4}
        res = self.client().post('/api/quizzes', json={"previous_questions": [], \
                                                       "quiz_category": quiz_category})

        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question']["id"] in [5, 9, 12, 23])

    def test_create_quiz_without_category(self):
        """Test finding a random question for a quiz without specific category (id = 0)
         that doesn't belong to the list of given questions """
        quiz_category = {"id": 0}

        previous_questions = [5, 9, 16, 17]
        res = self.client().post('/api/quizzes', \
                                 json={"previous_questions": previous_questions, \
                                       "quiz_category": quiz_category})

        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['question'])

    def test_400_if_category_id_is_not_specified(self):
        """Test creating of a quiz when category id was not specified """
        quiz_category = {"type": "History"}

        previous_questions = [5, 9, 16, 17]
        res = self.client().post('/api/quizzes', \
                                 json={"previous_questions": previous_questions, \
                                       "quiz_category": quiz_category})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bed request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()


