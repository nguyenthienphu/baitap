from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Boolean
from app import db, app
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
import enum
from datetime import datetime


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRoleEnum(enum.Enum):
    USER = 1
    ADMIN = 2


class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False, unique=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    email = Column(String(50), unique=True)
    phone = Column(String(50), unique=True)
    active = Column(Boolean, default=True)
    avatar = Column(String(100))
    joined_date = Column(DateTime, default=datetime.now())
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.USER)
    receipt = relationship('Receipt', backref='user', lazy=True)
    comment = relationship('Comment', backref='user', lazy=True)

    def __str__(self):
        return self.name


class Type(BaseModel):
    ten_loai = Column(String(50), nullable=False, unique=True)
    flight = relationship('Flight', backref='type', lazy=True)

    def __str__(self):
        return self.ten_loai


flight_airport = db.Table('flight_airport',
                          Column('flight_id', Integer, ForeignKey('flight.id'), primary_key=True),
                          Column('airport_id', Integer, ForeignKey('airport.id'), primary_key=True))


class Flight(BaseModel):
    ten_chuyen_bay = Column(String(50))
    ma_chuyen_bay = Column(Integer)
    ngay_gio = Column(DateTime)
    gia = Column(Float, default=0)
    hinh_anh = Column(String(100))
    ghe_1 = Column(Integer)
    ghe_2 = Column(Integer)
    time = Column(Integer)
    active = Column(Boolean, default=True)
    type_id = Column(Integer, ForeignKey(Type.id), nullable=False)
    airport = relationship('Airport', secondary='flight_airport', lazy='subquery', backref=backref('flight', lazy=True))
    receipt_detail = relationship('ReceiptDetail', backref='flight', lazy=True)
    comment = relationship('Comment', backref='flight', lazy=True)

    def __str__(self):
        return self.ten_chuyen_bay


class Airport(BaseModel):
    name = Column(String(50), nullable=False, unique=True)

    def __str__(self):
        return self.name


class Comment(BaseModel):
    content = Column(String(255), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created_date = Column(DateTime, default=datetime.now())

    def __str__(self):
        return self.content


class Receipt(BaseModel):
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    detail = relationship('ReceiptDetail', backref='receipt', lazy=True)
    created_date = Column(DateTime, default=datetime.now())


class ReceiptDetail(db.Model):
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False, primary_key=True)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False, primary_key=True)
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        
