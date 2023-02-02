from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

import data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    age = db.Column(db.Integer)
    email = db.Column(db.String, unique=True)
    role = db.Column(db.String)
    phone = db.Column(db.String)

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_dict(self):
        dic = {col.name: getattr(self, col.name) for col in self.__table__.columns if "date" not in col.name}
        dic["start_date"] = str(self.start_date)
        dic["end_date"] = str(self.end_date)
        return dic


"""with db.session.begin():
    db.create_all()
    users = [User(**user) for user in data.users]
    db.session.add_all(users)
    offers = [Offer(**offer) for offer in data.offers]
    db.session.add_all(offers)
    orders = [Order(
        id=order['id'],
        name=order['name'],
        description=order['description'],
        start_date=datetime.strptime(order['start_date'], '%m/%d/%Y').date(),
        end_date=datetime.strptime(order['start_date'], '%m/%d/%Y').date(),
        address=order['address'],
        price=order['price'],
        customer_id=order['customer_id'],
        executor_id=order['executor_id']
    ) for order in data.orders]
    db.session.add_all(orders)
    db.session.commit()"""


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        return jsonify([user.to_dict() for user in User.query.all()])
    elif request.method == 'POST':
        with db.session.begin():
            db.session.add(User(**json.loads(request.data)))
            db.session.commit()
        return '', 204


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        return jsonify([order.to_dict() for order in Order.query.all()])
    elif request.method == 'POST':
        with db.session.begin():
            db.session.add(Order(**json.loads(request.data)))
            db.session.commit()
        return '', 204


@app.route('/offers', methods=['GET', 'POST'])
def offers():
    if request.method == 'GET':
        return jsonify([offer.to_dict() for offer in Offer.query.all()])
    elif request.method == 'POST':
        with db.session.begin():
            db.session.add(Offer(**json.loads(request.data)))
            db.session.commit()
        return '', 204


@app.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def user(id):
    user = User.query.get(id)
    if request.method == 'GET':
        return jsonify(user.to_dict())
    elif request.method == 'PUT':
        dic = user.to_dict()
        dic.update(json.loads(request.data))
        db.session.query(User).filter(User.id == id).update(dic)
        db.session.commit()
        return '', 204
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return '', 204


@app.route('/offers/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def offer(id):
    offer = Offer.query.get(id)
    if request.method == 'GET':
        return jsonify(offer.to_dict())
    elif request.method == 'PUT':
        dic = offer.to_dict()
        dic.update(json.loads(request.data))
        db.session.query(Offer).filter(Offer.id == id).update(dic)
        db.session.commit()
        return '', 204
    elif request.method == 'DELETE':
        db.session.delete(offer)
        db.session.commit()
        return '', 204


@app.route('/orders/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def order(id):
    order = Order.query.get(id)
    if request.method == 'GET':
        return jsonify(order.to_dict())
    elif request.method == 'PUT':
        orderj = json.loads(request.data)
        dic = order.to_dict()
        dic.update({
            'id': orderj['id'],
            'name': orderj['name'],
            'description': orderj['description'],
            'start_date': datetime.strptime(orderj['start_date'], '%Y-%m-%d').date(),
            'end_date': datetime.strptime(orderj['start_date'], '%Y-%m-%d').date(),
            'address': orderj['address'],
            'price': orderj['price'],
            'customer_id': orderj['customer_id'],
            'executor_id': orderj['executor_id']
        })
        db.session.query(Order).filter(Order.id == id).update(dic)
        db.session.commit()
        return '', 204
    elif request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run()
