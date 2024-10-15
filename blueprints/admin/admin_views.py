from flask import url_for, request, redirect, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_login import current_user


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('Você não tem permissão para acessar esta página.', 'error')
        return redirect(url_for('views.home', next=request.url))

    def scaffold_list_columns(self):
        columns = super(MyModelView, self).scaffold_list_columns()
        if 'id' not in columns:
            columns.insert(0, 'id')
        return columns


class PlacasView(MyModelView):
    column_filters = ['veiculo']
    column_searchable_list = ['placa']


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('Você não tem permissão para acessar esta página.', 'error')
        return redirect(url_for('views.home', next=request.url))
