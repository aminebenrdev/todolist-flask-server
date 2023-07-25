from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'  
db = SQLAlchemy(app)

class ToDoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completedat = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completedat': self.completedat.strftime('%Y-%m-%d %H:%M') if self.completedat else None,
            'is_completed': self.is_completed
        }

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

@app.route('/api/')
def index():
    all_items = ToDoItem.query.all()
    return jsonify([item.to_dict() for item in all_items])


@app.route('/api/create', methods=['POST'])
def create():
    try:
        data = request.get_json()
        item = ToDoItem(title = data['title'], description = data['description'], is_completed = False)

        db.session.add(item)
        db.session.commit()

        return jsonify(item.to_dict())
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route('/api/<int:id>', methods=['PUT', 'DELETE'])
def update(id):
    try:
        if request.method == 'PUT':
            item = ToDoItem.query.get(id)

            if item:
                data = request.get_json()

                item.title = data.get('title', item.title)
                item.description = data.get('description', item.description)
                item.completedat = datetime.now() if item.is_completed == False and data['is_completed'] == True else item.completedat
                item.is_completed = data.get('is_completed', item.is_completed)

                db.session.commit()

                return jsonify(success=True, message='Item is updated')
            else:
                return jsonify(success=True, message='Item not exist'),404
        else:
            item = ToDoItem.query.get(id)
            db.session.delete(item)
            db.session.commit()

            return jsonify(success=True, message='Item is deleted')
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    
@app.route('/api/<int:id>/done', methods=['GET'])
def done(id):
    try:
        item = ToDoItem.query.get(id)

        if item:
            item.completedat = datetime.now()
            item.is_completed = True

            db.session.commit()

            return jsonify(item.to_dict())
        else:
            return jsonify(success=False, message='Item not exist'),404

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    