from app.models import Type, Flight, User, Receipt, ReceiptDetail, Comment
from app import db
from sqlalchemy import func
from app import app
from flask_login import current_user
from sqlalchemy.sql import extract
import hashlib


def get_type():
    return Type.query.all()


def get_flight(kw=None, type_id=None, page=None, airport_start_id=None, airport_end_id=None):
    flight = Flight.query.filter(Flight.active)

    if kw:
        flight = flight.filter(Flight.ten_chuyen_bay.contains(kw))

    if type_id:
        flight = flight.filter(Flight.type_id.__eq__(type_id))

    if page:
        page = int(page)
        page_size = app.config['PAGE_SIZE']
        start = (page - 1) * page_size

        return flight.slice(start, start + page_size)

    return flight.all()


def count_flight():
    return Flight.query.filter(Flight.active).count()


def get_flight_by_id(flight_id):
    return Flight.query.get(flight_id)


def get_user_by_id(user_id):
    return User.query.get(user_id)


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()), User.password.__eq__(password), User.active).first()


def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(),
                username=username,
                password=password,
                email=kwargs.get('email'),
                phone=kwargs.get('phone'),
                avatar=kwargs.get('avatar'))

    db.session.add(user)
    db.session.commit()


def flight_count_by_type():
    return Type.query.join(Flight, Flight.type_id.__eq__(Type.id), isouter=True).add_column(
        func.count(Flight.id)).group_by(Type.id).all()


def add_receipt(ticket):
    if ticket:
        receipt = Receipt(user=current_user)
        db.session.add(receipt)

        for t in ticket.values():
            d = ReceiptDetail(receipt=receipt, flight_id=t['id'], quantity=t['quantity'], unit_price=t['gia'])
            db.session.add(d)

        db.session.commit()


def count_ticket(ticket):
    total_quantity, total_amount = 0, 0
    if ticket:
        for c in ticket.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['gia']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }


def stats_revenue(kw=None, from_date=None, to_date=None):
    query = db.session.query(Flight.id, Flight.ten_chuyen_bay,
                             func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .join(ReceiptDetail, ReceiptDetail.flight_id.__eq__(Flight.id), isouter=True) \
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id)) \
        .group_by(Flight.id, Flight.ten_chuyen_bay)

    if kw:
        query = query.filter(Flight.ten_chuyen_bay.contains(kw))
    if from_date:
        query = query.filter(Receipt.created_date.__ge__(from_date))
    if to_date:
        query = query.filter(Receipt.created_date.__le__(to_date))

    return query.all()


def flight_moth_stats(year):
    return db.session.query(extract('month', Receipt.created_date),
                            func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price))\
                            .join(ReceiptDetail,ReceiptDetail.receipt_id.__eq__(Receipt.id))\
                            .filter(extract('year', Receipt.created_date) == year)\
                            .group_by(extract('month', Receipt.created_date))\
                            .order_by(extract('month', Receipt.created_date)).all()


def add_comment(content, flight_id):
    c = Comment(content=content, flight_id=flight_id, user=current_user)

    db.session.add(c)
    db.session.commit()

    return c


def get_comments(flight_id, page=1):
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1) * page_size

    return Comment.query.filter(Comment.flight_id.__eq__(flight_id)).order_by(-Comment.id).slice(start, start + page_size).all()


def count_comment(flight_id):
    return Comment.query.filter(Comment.flight_id.__eq__(flight_id)).count()