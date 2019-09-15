import os
from projects import app, mail, project_manager
from projects.models import Project, User
from projects.forms import AuthRequestForm, LoginForm, \
    PasswordResetForm, FileRequired
from projects.helpers import unique_name_encoding, unique_name_decode
from projects_base.base.forms import TagsSearchForm
from flask import render_template, request, flash, redirect, url_for, \
    jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from projects.helpers import generate_confirmation_token, confirm_token
from bcrypt import hashpw, gensalt
import datetime


# Routes
@app.route("/")
@app.route("/projects", methods=['GET'])
def projects():
    form = TagsSearchForm()
    entities = Project.get_all()
    return render_template('projects.html', title=app.config['TITLE'],
                           grid_header=app.config['TITLE'] + " Projects",
                           objects=entities, form=form)


@app.route('/my_projects', methods=['GET'])
@login_required
def my_projects():
    form = TagsSearchForm()
    entities = [project for project in Project.get_all()
                if project._id in current_user.projects]
    return render_template('projects.html', objects=entities, form=form)


@app.route('/show/<object_id>', methods=['GET'])
def show(object_id):
    form_class = project_manager.get_form_class()
    form = form_class()
    entity = Project.get(object_id)
    if entity is None:
        flash("That project dosen't exist", 'danger')
        return redirect(url_for('projects'))

    owner = False
    if current_user.is_authenticated and object_id in current_user.projects:
        owner = True
        for attr in entity.__dict__:
            if attr != '_id' and attr != '_type':
                form[attr].data = entity.__dict__[attr]
            # Workaround for image upload required, set the label
            # to the currently used image and disable it as a required field
            if attr == "image":
                form[attr].label.text = "Stored image is: " \
                                        + unique_name_decode(
                    entity.__dict__[attr])
                form[attr].flags = None
    else:
        # Translate area keys to values
        if hasattr(entity, 'area'):
            entity.area = [area[1] for area in form.area.choices
                           if area[0] in entity.area]
    return render_template('project.html', object=entity, owner=owner,
                           form=form)


@app.route('/create_project', methods=['GET', 'POST'])
@login_required
def create():
    form_class = project_manager.get_form_class()
    form = form_class(CombinedMultiDict((request.files, request.form)))

    if form.validate_on_submit():
        f = form.image.data
        # Make sure the saved image is filename is unique
        filename = secure_filename(unique_name_encoding(f.filename))
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Remove special fields
        if form.__contains__('csrf_token'):
            form._fields.pop('csrf_token')
        form._fields.pop('image')
        # Save new instance
        new_instance = {key: field.data for key, field in
                        form.__dict__.items()
                        if hasattr(field, 'data')}

        new_instance['image'] = filename
        entity = Project(**new_instance)
        entity_id = entity.save()
        # Update user with new instance
        current_user.projects.append(entity_id)
        current_user.save()
        url = url_for('show', object_id=entity_id, _external=True)
        flash("Your submission has been received,"
              " your metadata can be found at: " + url, 'success')
        return redirect(url)
    return render_template('create_project.html', form=form)


@app.route('/update/<object_id>', methods=['POST'])
@login_required
def update(object_id):
    entity = Project.get(object_id)
    if entity is None:
        flash("That entity dosen't exist", 'danger')
        return redirect(url_for('datasets'))

    if object_id not in current_user.projects:
        flash("Your trying to update an entity that's not yours", 'danger')
        return redirect(url_for('datasets'))

    form_class = project_manager.get_form_class()
    form = form_class(CombinedMultiDict((request.files, request.form)))
    # Strip image upload validation on upload (Optional)
    form.image.validators = [validator for validator in form.image.validators
                             if type(validator) is not FileRequired]

    if form.validate_on_submit():
        # Only save the image if a new was submitted, else keep the old name
        f = form.image.data
        if f.filename != '':
            filename = secure_filename(unique_name_encoding(f.filename))
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Remove old
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], entity.image))
        else:
            filename = entity.image

        # Update every attribute except _id, _type, and image
        disabled_updates = ['_id', '_type', 'image']
        for attr in entity.__dict__:
            if attr not in disabled_updates:
                entity.__dict__[attr] = form[attr].data
        entity.__dict__['image'] = filename
        entity_id = entity.save()

        url = url_for('show', object_id=entity_id, _external=True)
        flash("Update Success, your data can be found at: " + url,
              'success')
        return redirect(url)
    form.image.flags = None
    return render_template('project.html', object=entity, form=form)


@app.route('/delete/<object_id>', methods=['POST'])
@login_required
def delete(object_id):
    entity = Project.get(object_id)
    if entity is None:
        flash("That entity dosen't exist", 'danger')
        return redirect(url_for('projects'))
    if object_id in current_user.projects:
        Project.remove(object_id)
        current_user.projects.remove(object_id)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], entity.image))
        current_user.save()
        flash("Entity: " + entity.name + " has been deleted", 'success')
    else:
        flash("Your trying to delete an entity you don't own", 'danger')
    return redirect(url_for('projects'))


# Sends approval emails to every app.config['ADMINS_EMAIL']
@app.route('/request_auth', methods=['POST'])
def request_auth():
    form = AuthRequestForm(request.form)
    if form.validate_on_submit():
        # Send confirmation token
        user = User.get_with_first('email', form.email.data)
        if user is None:
            token = generate_confirmation_token(email=form.email.data)
            confirm_url = url_for('approve_auth', token=token, _external=True)
            html = render_template('email/activate_user.html',
                                   email=form.email.data,
                                   confirm_url=confirm_url)
            msg = Message(subject=form.email.data
                          + " requests {title} Projects access".format(
                              title=app.config['TITLE']),
                          html=html, recipients=app.config['ADMINS_EMAIL'],
                          sender=app.config['MAIL_USERNAME'])
            mail.send(msg)
            return jsonify(data={
                'success': 'Request successfully submitted'
                           ', awaiting admin approval'})
        else:
            response = jsonify(
                data={'danger': 'That email has already been granted access'})
            response.status_code = 400
            return response
    response = jsonify(data={'danger': ', '.join(
        [msg for attr, errors in form.errors.items() for msg in errors])})
    response.status_code = 400
    return response


# Accepts approval from admin's
@app.route('/approve_auth/<token>')
def approve_auth(token):
    email = confirm_token(token)
    if email is False:
        flash('Confirmation failed, either it is invalid or expired.',
              'danger')
    else:
        user = User.get_with_first('email', email)
        if user is not None:
            flash('That email has already been registered')
        else:
            # Setup
            user = User(email=email,
                        password=hashpw(os.urandom(24), gensalt()),
                        projects=[], is_active=False, is_authenticated=False,
                        is_anonymous=False,
                        confirmed_on=datetime.datetime.now())
            user.save()

            token = generate_confirmation_token(email=email)
            reset_url = url_for('reset_password', token=token, _external=True)
            html = render_template('email/reset_password.html', email=email,
                                   reset_password_url=reset_url)
            msg = Message(subject='{title} Projects Account approval'.format(
                title=app.config['TITLE']
            ),
                html=html, recipients=[email],
                sender=app.config['MAIL_USERNAME'])
            mail.send(msg)
            flash("The account: " + email + " has been approved and created",
                  'success')
    return redirect(url_for('projects'))


@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password(token):
    email = confirm_token(token)
    if email is False:
        flash(
            'Attempted password reset failed,'
            ' the request is either invalid or expired', 'danger')
    else:
        form = PasswordResetForm(request.form)
        form.email.data = email
        if form.validate_on_submit():
            user = User.get_with_first('email', email)
            user.is_active = True
            user.is_authenticated = True
            user.is_anonymous = False
            user.email = email
            user.password = hashpw(bytes(form.password.data, 'utf-8'),
                                   gensalt())
            user.save()
            flash('Your password has now been updated', 'success')
            return redirect(url_for('projects'))
        return render_template('reset_password_form.html', form=form)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        valid_user = User.valid_user(form.email.data, form.password.data)
        if valid_user is not None:
            flash('Logged in successfully.', 'success')
            login_user(valid_user)
            return redirect(url_for('projects'))
        else:
            flash('Invalid Credentials', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('projects'))


# TODO -> refactor with fair search forms in common views instead.
@app.route('/search', methods=['GET'])
def tag_external_search():
    form = TagsSearchForm(request.args, csrf_enabled=False)
    entities = {}
    # The return form should contain a csrf_token
    return_form = TagsSearchForm()
    return_form.tag = form.tag
    if form.validate():
        entities = Project.get_with_search('tags', form.tag.data)
        return render_template('projects.html', objects=entities,
                               form=return_form)
    # pass on errors
    return_form._errors = form.errors
    return_form._fields['tag'] = form._fields['tag']
    return render_template('projects.html', objects=entities, form=return_form)


# TODO -> refactor with fair search forms in common views instead.
@app.route('/search', methods=['POST'])
def tag_native_search():
    form = TagsSearchForm(request.form)
    if form.validate_on_submit():
        result = {}
        tag = request.form['tag']
        entities = Project.get_with_search('tags', tag)
        if len(entities) > 0:
            result = [entity.serialize() for entity in entities]
        return jsonify(data=result)

    response = jsonify(data={'danger': ', '.join(
        [msg for attr, errors in form.errors.items() for msg in errors])})
    response.status_code = 400
    return response


@app.route('/static/<filename>')
def projects_static(filename):
    return send_from_directory(app.config['PROJECTS_STATIC_FOLDER'], filename)


@app.route('/static/images/<filename>')
def projects_images(filename):
    return send_from_directory(os.path.join(
        app.config['PROJECTS_STATIC_FOLDER'], 'images'), filename)
