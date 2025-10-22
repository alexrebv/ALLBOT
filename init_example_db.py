from db import init_db, SessionLocal
from models import User, Role
import bcrypt
init_db()
db = SessionLocal()
# create roles
if not db.query(Role).first():
    db.add_all([Role(name='manager', description='Manager'), Role(name='admin', description='Admin')])
    db.commit()
# create a test user: login=test, password=pass123
if not db.query(User).filter(User.login=='test').first():
    pw = 'pass123'.encode('utf-8')
    h = bcrypt.hashpw(pw, bcrypt.gensalt()).decode('utf-8')
    u = User(login='test', password_hash=h, role_id=1)
    db.add(u)
    db.commit()
    print('Created test user: login=test password=pass123')
else:
    print('Test user exists')
db.close()
