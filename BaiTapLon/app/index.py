from flask import render_template, request, redirect, session, jsonify, url_for
from app import app, login
import dao
from flask_login import login_user, logout_user, login_required, current_user
import math
import cloudinary.uploader


@app.route("/")
def index():
    kw = request.args.get('kw')
    type_id = request.args.get('type_id')
    page = request.args.get('page')

    airport_start_id = request.args.get('airport_start_id')
    airport_end_id = request.args.get('airport_end_id')

    flight = dao.get_flight(kw, type_id, page, airport_start_id, airport_end_id)


    num = dao.count_flight()

    return render_template('index.html', flight=flight,
                           pages=math.ceil(num / app.config['PAGE_SIZE']))


@app.route("/flight/<int:flight_id>")
def flight_detail(flight_id):
    flight = dao.get_flight_by_id(flight_id)
    comment = dao.get_comments(flight_id=flight_id,
                               page=int(request.args.get('page', 1)))

    return render_template('details.html',
                           flight=flight,
                           comment=comment,
                           pages=math.ceil(dao.count_comment(flight_id=flight_id) / app.config['COMMENT_SIZE']))


@app.context_processor
def common_response():
    return {
        'type': dao.get_type(),
        'ticket': dao.count_ticket(session.get('ticket'))
    }


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/admin/login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)
    return redirect('/admin')


@app.route('/login', methods=['get', 'post'])
def login():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)

            next = request.args.get('next', 'index')
            return redirect(url_for(next))

    return render_template('login.html')


@app.route("/logout")
def log_out():
    logout_user()
    return redirect('/')


@app.route("/register", methods=['get', 'post'])
def register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        username = request.form.get('username')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')
        avatar_path = None

        try:
            if password.strip().__eq__(confirmPassword.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']
                dao.add_user(name=name, email=email, phone=phone, username=username, password=password, avatar=avatar_path)
                return redirect('/login')
            else:
                err_msg = "Mật khẩu không khớp"
        except Exception as ex:
            err_msg = "Hệ thống đang có lỗi: " + str(ex)

    return render_template('register.html', err_msg=err_msg)


@app.route('/api/add-ticket', methods=['post'])
def add_to_ticket():
    data = request.json
    id = str(data.get('id'))
    ten_chuyen_bay = data.get('ten_chuyen_bay')
    gia = data.get('gia')

    ticket = session.get('ticket')
    if not ticket:
        ticket = {}

    if id in ticket:
        ticket[id]['quantity'] = ticket[id]['quantity'] + 1
    else:
        ticket[id] = {
            'id': id,
            'ten_chuyen_bay': ten_chuyen_bay,
            'gia': gia,
            'quantity': 1
        }
    session['ticket'] = ticket
    return jsonify(dao.count_ticket(ticket))


@app.route('/api/update-ticket', methods=['put'])
def update_ticket():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')

    ticket = session.get('ticket')
    if ticket and id in ticket:
        ticket[id]['quantity'] = quantity
        session['ticket'] = ticket

    return jsonify(dao.count_ticket(ticket))


@app.route('/api/delete-ticket/<flight_id>', methods=['delete'])
def delete_ticket(flight_id):
    ticket = session.get('ticket')

    if ticket and flight_id in ticket:
        del ticket[flight_id]
        session['ticket'] = ticket

    return jsonify(dao.count_ticket(ticket))


@app.route('/api/pay', methods=['post'])
@login_required
def pay():
    try:
        dao.add_receipt(session.get('ticket'))
        del session['ticket']
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})


@app.route('/ticket')
def ticket():
    return render_template('ticket.html', sum=dao.count_ticket(session.get('ticket')))


@app.route('/api/comment', methods=['post'])
@login_required
def add_comment():
    data = request.json
    content = data.get('content')
    flight_id = data.get('flight_id')

    try:
        c = dao.add_comment(content=content, flight_id=flight_id)
    except:
        return {'status': 404, 'err_msg': 'Chương trình đang bị lỗi'}

    return {'status': 201, 'comment': {
        'id': c.id,
        'content': c.content,
        'created_date': c.created_date,
        'user': {
            'username': current_user.username,
            'avatar': current_user.avatar
        }
    }}


@app.route('/pay', methods=['get', 'post'])
@login_required
def pays():
    return render_template('pay.html')


if __name__ == '__main__':
    from app import admin
    app.run(debug=True)

