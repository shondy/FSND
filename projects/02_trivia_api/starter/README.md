# Full Stack API Final Project


## Full Stack Trivia

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game, but their API experience is limited and still needs to be built out.

I've completed the trivia app by developing an api for the backend that is called from the frontend. 
The application can:

1. Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer.
2. Delete questions.
3. Add questions and require that they include question and answer text.
4. Search for questions based on a text query string.
5. Play the quiz game, randomizing either all questions or within a specific category.


## Start the trivia app

### Frontend
Install dependencies for the frontend:
```
npm install
npm start
```
Open `http://localhost:3000` to view the Trivia app in the browser.

The `/frontend` directory contains a complete React frontend to consume the data from 
the Flask server. 

### Backend

Install dependencies for the backend:
1. **Virtual Enviornment** 
2. **PIP Dependencies** - install dependencies by naviging to the /backend directory and running:
   ```
   pip install -r requirements.txt
   ```
   
3. **Set up the database**:
   ```
   psql trivia < trivia.psql
   ```
                         
4. **Prepare the flask app to run and run it**
   ```
   set FLASK_APP=flaskr __init__
   flask run
   ```

The `/backend` directory contains a Flask and SQLAlchemy server. 
The endpoints are defined in `/backend/flaskr/__init__.py`, DB models and SQLAlchemy 
setup - in `/backend/models.py`. 

#### Testing
To run the unit tests, run
```
createdb -U postgres trivia_test
psql -U postgres trivia_test < trivia.psql 
python test_flaskr.py
```

### API documentation
#### Restrictions 
The API has next restrictions (imposed by CORS):
- only resources matching `/api/*` can be reached and it can be done by all origins
- only GET, POST, DELETE, and OPTIONS HTTP methods are allowed

#### Endpoint conventions and Error codes
All responses are returned in JSON format and all contain a 
"success" key, which will return either True or False.

The API can return next error codes: 400, 404, 405, 422, and 500. 
The return format has the following structure (example for the 404 code): 
```
{
    "success": False,
    "error": 404,
    "message": "resource not found"
}
```
#### API Objects
The API has two types of objects, Categories and Questions.
1. Categories
   
   Category is a category of a question. It can have one of 6 possible values: 
Science, Art, Geography, History, Entertainment, and Sports
2. Questions
   
   Each Question contains a question itself, a category it belongs to, 
a difficulty (on a scale of 1 to 6), and an answer.

#### Endpoint Library
##### GET /api/categories
Returns a list of category objects and success value

*Sample*: curl http://127.0.0.1:5000/api/categories
```
{
  "categories": [
    {
      "id": 1, 
      "type": "Science"
    }, 
    {
      "id": 2, 
      "type": "Art"
    }, 
    {
      "id": 3, 
      "type": "Geography"
    }, 
    {
      "id": 4, 
      "type": "History"
    }, 
    {
      "id": 5, 
      "type": "Entertainment"
    }, 
    {
      "id": 6, 
      "type": "Sports"
    }
  ], 
  "success": true
}
```
##### GET /api/questions
Returns a list of all category objects, a list of question objects, 
success value, and total number of questions in database.
Results are paginated in groups of 10. 
Append URL parameter ?page=<num> to choose page number (default page number is 1)

*Sample*: curl http://127.0.0.1:5000/api/questions?page=2
```
{
  "categories": [
    {
      "id": 1, 
      "type": "Science"
    }, 
    {
      "id": 2, 
      "type": "Art"
    }, 
    {
      "id": 3, 
      "type": "Geography"
    }, 
    {
      "id": 4, 
      "type": "History"
    }, 
    {
      "id": 5, 
      "type": "Entertainment"
    }, 
    {
      "id": 6, 
      "type": "Sports"
    }
  ], 
  "current_category": null, 
  "questions": [
    {
      "answer": "Agra", 
      "category": 3, 
      "difficulty": 2, 
      "id": 15, 
      "question": "The Taj Mahal is located in which Indian city?"
    }, 
    {
      "answer": "Escher", 
      "category": 2, 
      "difficulty": 1, 
      "id": 16, 
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    }, 
    {
      "answer": "Mona Lisa", 
      "category": 2, 
      "difficulty": 3, 
      "id": 17, 
      "question": "La Giaconda is better known as what?"
    }, 
    {
      "answer": "One", 
      "category": 2, 
      "difficulty": 4, 
      "id": 18, 
      "question": "How many paintings did Van Gogh sell in his lifetime?"
    }, 
    {
      "answer": "Jackson Pollock", 
      "category": 2, 
      "difficulty": 2, 
      "id": 19, 
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }, 
    {
      "answer": "The Liver", 
      "category": 1, 
      "difficulty": 4, 
      "id": 20, 
      "question": "What is the heaviest organ in the human body?"
    }, 
    {
      "answer": "Alexander Fleming", 
      "category": 1, 
      "difficulty": 3, 
      "id": 21, 
      "question": "Who discovered penicillin?"
    }, 
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }, 
    {
      "answer": "Scarab", 
      "category": 4, 
      "difficulty": 4, 
      "id": 23, 
      "question": "Which dung beetle was worshipped by the ancient Egyptians?"
    }
  ], 
  "success": true, 
  "total_questions": 19
}
```
##### DELETE /api/questions/<question_id>
Deletes the question of the given id if it exists. Returns the id of 
the deleted question and a success value.

*Sample*: curl -X DELETE http://127.0.0.1:5000/api/questions/19
```
{
    'deleted': 19,
    'success': true
}
```

##### POST /api/questions
This endpoint performs two functions
- Creates a new question
- Searches questions based on a search term

**Creating a new question**
Creating a new question object using the submitted question, answer, category, and 
difficulty as application/json type. Returns a success status and id of newly created 
question if successful

*Sample*: curl http://127.0.0.1:5000/api/questions -X POST -H "Content-Type: application/json" -d '{"question": "What is the highest active volcano in Europe?", "answer": "Etna", "category": 3, "difficulty": 2}'
```
{
    "success": true,
    "added": 20
}
```
**Searching questions based on a search term**
Request contains search term data as application/json type
Returns a success status, a list of all question objects for whom the search term 
is a substring of the question, and total number of questions 

*Sample*: curl http://localhost:5000/api/questions -X POST -H "Content-Type: application/json" -d '{"searchTerm": "name"}'
```
{
  "questions": [
    {
      "answer": "Muhammad Ali", 
      "category": "4", 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    },
    {
      "answer": "Brazil", 
      "category": "6", 
      "difficulty": 3, 
      "id": 10, 
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    }
  ], 
  "success": true, 
  "totalQuestions": 19
}
```
##### GET /api/categories/<category_id>/questions
Requests all the questions based on a particular category (category_id).
Returns a success status, the list of questions for requested category (without pagination), 
the number of questions in this category, and category_id.

*Sample*: curl http://127.0.0.1:5000/api/categories/5/questions
```
{
  "currentCategory": 5,
  "questions": [
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    },
    {
      "answer": "Tom Cruise",
      "category": 5,
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }
  ],
  "success": true,
  "totalQuestions": 3
}
```
##### POST /api/quizzes
Enables the playing of a Trivia game
Returns a random question for a given category that has not been asked already. 
If a category isn't specified (quiz_category equal to 0) than a question is randomly chosen among all categories.
Request contains a quiz category and a list of previously asked questions encoded 
in application/json format.
Returns a success status and, if successful, a random question. 
If there are no more questions to return in that category, the API returns only a
success status (without a question). That tells the frontend the quiz is over.

*Sample*: get a question from all categories (category 0) with an empty list of previous questions 
(as it at happens at the beginning of the game):
 
curl -X POST http://127.0.0.1:5000/api/quizzes -H "Content-Type: application/json" -d '{previous_questions: [], quiz_category: {type: "click", id: 0}}'
```
{
  "question": {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
  }, 
  "success": true
}
```
*Sample*: get a question from the Entertainment category (category 5) when there are no more questions 
left in the category: 

curl -X POST http://127.0.0.1:5000/api/quizzes -H "Content-Type: application/json" -d '{previous_questions: [2, 4, 6], quiz_category: {type: "Entertainment", id: "5"}}'
```
{
  "success": true
}
```
