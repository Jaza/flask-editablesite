from flask import current_app as app
from flask_script import Command, Option, prompt, prompt_pass


class CreateUser(Command):
    """Creates a user."""

    def get_options(self):
        return (
            Option('--email',
                   help='User e-mail'),
            Option('--first-name',
                   help='User first name'),
            Option('--last-name',
                   help='User last name'),
            Option('--password',
                   help='User password')
        )

    def create_user(self, email, first_name, last_name, password):
        from flask_editablesite.user.models import User

        u = User(email=email, first_name=first_name,
                 last_name=last_name, active=True)
        u.set_password(password)
        u.save()

        return u

    def run(self, email=None, first_name=None, last_name=None, password=None):
        if not email:
            email = prompt("A valid email address")

        if not first_name:
            first_name = prompt("First name")

        if not last_name:
            last_name = prompt("Last name")

        if not password:
            password = prompt_pass("Password")

        user = (
            (not app.config.get('USE_SESSIONSTORE_NOT_DB'))
            and self.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password)
            or None)

        if not user:
            user = "Can't create the user"

        print(user)
