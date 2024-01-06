from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose
from app.models import Flight, Type, UserRoleEnum, User, Airport
from app import app, db, dao
from flask_login import logout_user, current_user
from flask import redirect, request
from datetime import datetime

admin = Admin(app=app, name='QUẢN TRỊ CHUYẾN BAY', template_mode='bootstrap4')


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class MyTypeView(AuthenticatedAdmin):
    column_list = ['ten_loai', 'flight']
    edit_modal = True
    details_modal = True
    column_filters = ['ten_loai']
    column_searchable_list = ['ten_loai']


class MyFlightView(AuthenticatedAdmin):
    can_view_details = True
    edit_modal = True
    details_modal = True
    column_exclude_list = ['hinh_anh']


class MyUserView(AuthenticatedAdmin):
    pass


class MyAirportView(AuthenticatedAdmin):
    pass


class MyAirportStartView(AuthenticatedAdmin):
    pass


class MyAirportEndView(AuthenticatedAdmin):
    pass


class StatsView(AuthenticatedUser):
    @expose("/")
    def index(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        year = request.args.get('year', datetime.now().year)
        return self.render('admin/stats.html',stats=dao.flight_count_by_type(), revenue=dao.stats_revenue(kw=kw, from_date=from_date, to_date=to_date),
                           month_stats=dao.flight_moth_stats(year=year))


class LogoutView(AuthenticatedUser):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


admin.add_view(MyTypeView(Type, db.session))
admin.add_view(MyFlightView(Flight, db.session))
admin.add_view(MyAirportView(Airport, db.session))
admin.add_view(MyUserView(User, db.session))
admin.add_view(StatsView(name='Thống kê báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))
