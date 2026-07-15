from marshmallow import fields, validate, Schema
from ..extensions import ma
from ..models.user import User

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ("password_hash",)

class RegisterSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.String(required=True, validate=validate.Length(min=8))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class PasswordResetRequestSchema(Schema):
    email = fields.Email(required=True)

class PasswordResetSchema(Schema):
    token = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=8))

class UpdateProfileSchema(Schema):
    username = fields.String(validate=validate.Length(min=3, max=50))
    preferences = fields.Dict()

user_schema = UserSchema()
register_schema = RegisterSchema()
login_schema = LoginSchema()
password_reset_request_schema = PasswordResetRequestSchema()
password_reset_schema = PasswordResetSchema()
update_profile_schema = UpdateProfileSchema()
