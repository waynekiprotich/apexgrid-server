import bcrypt
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import create_access_token
from ..models.user import User, RefreshToken
from ..extensions import db
import secrets

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_tokens(user_id):
    access_token = create_access_token(identity=str(user_id))
    
    raw_token = secrets.token_hex(32)
    token_hash = hash_password(raw_token)
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    rt = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.session.add(rt)
    db.session.commit()
    
    return access_token, raw_token, rt.id

def revoke_refresh_token(token_id, user_id):
    rt = RefreshToken.query.filter_by(id=token_id, user_id=user_id).first()
    if rt:
        rt.revoked = True
        db.session.commit()

def verify_refresh_token(token_id, raw_token):
    rt = RefreshToken.query.filter_by(id=token_id, revoked=False).first()
    if rt:
        expires_at = rt.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            
        if expires_at > datetime.now(timezone.utc):
            if check_password(raw_token, rt.token_hash):
                return rt
    return None

def generate_password_reset_token(user_id):
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_password(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    from ..models.user import PasswordResetToken
    prt = PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.session.add(prt)
    db.session.commit()
    
    return raw_token, prt.id

def verify_and_use_password_reset_token(token_id, raw_token):
    from ..models.user import PasswordResetToken
    prt = PasswordResetToken.query.filter_by(id=token_id, used=False).first()
    if prt:
        expires_at = prt.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            
        if expires_at > datetime.now(timezone.utc):
            if check_password(raw_token, prt.token_hash):
                prt.used = True
                db.session.commit()
                return prt
    return None

def update_password(user_id, new_password):
    user = User.query.get(user_id)
    if user:
        user.password_hash = hash_password(new_password)
        db.session.commit()

