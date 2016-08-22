import flask
import pytest

from forms import *


def test_form():
    app = flask.Flask(__name__)
    app.testing = True

    class BasicForm(Form):
        a = IntField('args', required=True, name='a')
        b = StringField('args', required=True)
        c = StringField('args', required=False, default='default')
        d = FloatField('args', required=True)

    class RequireForm(Form):
        x = StringField('args', required=True, default='default')

    @app.route('/')
    @BasicForm
    def index():
        assert form.a == 10
        assert form.b == 'hello'
        assert form.c == 'default'
        assert form.d == 12.5
        return ''

    with app.test_client() as c:
        c.get('/?a=10&b=hello&d=12.5')

    @app.route('/require')
    @RequireForm
    def require():
        return str(form.x)

    with app.test_client() as c:
        with pytest.raises(ValidationError):
            c.get('/require')

    class SizeForm(Form):
        s = IntField('args', min_val=5,max_val=10)

    @app.route('/size')
    @SizeForm
    def size():
        assert form.s == 5
        return ''

    with app.test_client() as c:
        c.get('/size?s=5')

    class ListForm(Form):
        l = CSVListField('args', each_field=IntField, description='list')

    @app.route('/list')
    @ListForm
    def list_form():
        assert form.l == [1, 2, 3]
        return ''

    with app.test_client() as c:
        c.get('/list?l=1,2,3')


