from app.models.user import User
from app.extensions import db_session


def test_password_hashing():
    u = User(full_name="Hasher", email="hash@test.org", role="farmer")
    u.set_password("SecurePass@123")
    assert u.check_password("SecurePass@123") is True
    assert u.check_password("WrongPassword") is False
    assert u.password_hash != "SecurePass@123"


def test_user_registration(client):
    # Test valid registration
    res = client.post('/register', data={
        'csrf_token': 'dummy',  # In testing, csrf validation is adapted or token passed
        'full_name': 'New Farmer',
        'email': 'newfarmer@test.org',
        'password': 'Password@123',
        'confirm_password': 'Password@123',
        'role': 'farmer',
        'phone': '1234567890',
        'farm_name': 'New Sunrise Farm'
    }, follow_redirects=True)

    # Note: testing requires session CSRF token unless bypassed in testing config
    user = db_session.query(User).filter_by(email='newfarmer@test.org').first()
    # If CSRF validation failed because of mock token, verify with session token
    if not user:
        with client.session_transaction() as sess:
            token = sess['_csrf_token']
        res = client.post('/register', data={
            'csrf_token': token,
            'full_name': 'New Farmer',
            'email': 'newfarmer@test.org',
            'password': 'Password@123',
            'confirm_password': 'Password@123',
            'role': 'farmer',
            'phone': '1234567890',
            'farm_name': 'New Sunrise Farm'
        }, follow_redirects=True)
        user = db_session.query(User).filter_by(email='newfarmer@test.org').first()

    assert user is not None
    assert user.full_name == 'New Farmer'
    assert user.role == 'farmer'
    assert user.check_password('Password@123') is True


def test_user_login_and_logout(client, auth_users):
    user = auth_users['farmer1']

    # Get session CSRF
    with client.session_transaction() as sess:
        sess['_csrf_token'] = 'test-token'

    # Valid Login
    res = client.post('/login', data={
        'csrf_token': 'test-token',
        'email': user.email,
        'password': 'Farmer@123'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Livestock Health Dashboard" in res.data or b"Dashboard" in res.data

    # Logout
    res_logout = client.get('/logout', follow_redirects=True)
    assert res_logout.status_code == 200
    assert b"You have been logged out" in res_logout.data or b"Sign In" in res_logout.data


def test_protected_routes_redirect_unauthenticated(client):
    res = client.get('/dashboard', follow_redirects=False)
    assert res.status_code == 302
    assert '/login' in res.location

    res2 = client.get('/animals', follow_redirects=False)
    assert res2.status_code == 302
    assert '/login' in res2.location
