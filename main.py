from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, RadioField, widgets, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, NumberRange
from flask_sqlalchemy import SQLAlchemy
import bleach
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6xtigininomahBXox7C0sKR6b'
##CONNECT TO DB
app.config['DATABASE_URL1'] = 'postgresql://sifcqwmvmcwdgt:1bd013a8d1fe76af1f4fe09f56119fcc508be6ffa25d8964c905e7d3593f4b75@ec2-34-207-12-160.compute-1.amazonaws.com:5432/d478acdjs7a4a3'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL1",  "sqlite:///db.sqlite")
Bootstrap(app)
db = SQLAlchemy(app)
ckeditor = CKEditor(app)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SurveyForm(FlaskForm):
    name = StringField('Enter your name', validators=[DataRequired()], render_kw={'class': 'input-group input-group-outline my-3'})
    email = StringField('Enter your email', validators=[DataRequired()], render_kw={'class': 'input-group input-group-outline mb-3'})
    number = IntegerField('On a scale of 1 to 10, how would you describe your progress since you joined Kamilimu', validators=[DataRequired(), NumberRange(min=1, max=10)], render_kw={'class': 'input-group input-group-outline my-3'})
    dropdown = SelectField('What is your mentor\'s name?:', choices=[('Abdul Rahman Rehmtulla'), ('Beryl Nekesa'), ('Derrick Ngig'), ('Faith Chepkemoi')], validators=[DataRequired()])
    radio_fields = RadioField('Which sessions did you find most beneficial?', choices=[('Scholarship'), ('Professional mentorship'), ('ICT Innovation')], validators=[DataRequired()])
    check_fields = MultiCheckboxField('Which segment should we improve on?', choices=[('Scholarship'), ('Professional mentorship'), ('ICT Innovation')], validators=[DataRequired()], render_kw={'class': 'some-selector', 'style': 'border:none;'})
    comments = CKEditorField("We would appreciate any additional feedback", render_kw={'class':'control-label'})
    submit = SubmitField('Submit', render_kw={'style': 'align-items:center'})

class SurveyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(50))
    number = db.Column(db.Integer)
    dropdown = db.Column(db.String(100))
    radio_fields = db.Column(db.String(100))
    check_fields = db.Column(db.String(100))
    comments = db.Column(db.Text)

# db.create_all()

## strips invalid tags/attributes
def strip_invalid_html(content):
    allowed_tags = ['a', 'abbr', 'acronym', 'address', 'b', 'br', 'div', 'dl', 'dt',
                    'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
                    'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'strike',
                    'span', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
                    'thead', 'tr', 'tt', 'u', 'ul']

    allowed_attrs = {
        'a': ['href', 'target', 'title'],
        'img': ['src', 'alt', 'width', 'height'],
    }

    cleaned = bleach.clean(content,
                           tags=allowed_tags,
                           attributes=allowed_attrs,
                           strip=True)

    return cleaned


@app.route("/", methods=["POST", "GET"])
def submit():
    form=SurveyForm()
    if form.validate_on_submit():
        new_survey = SurveyData()
        new_survey.name = form.name.data
        new_survey.email = form.email.data
        new_survey.number = form.number.data
        new_survey.dropdown = form.dropdown.data
        new_survey.radio_fields = form.radio_fields.data
        check_fields = request.form.getlist("check_fields")
        new_survey.check_fields = ','.join(check_fields)
        new_survey.comments = strip_invalid_html(form.comments.data)
        db.session.add(new_survey)
        db.session.commit()
        return redirect("success")
    return render_template('index.html', form=form)

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)