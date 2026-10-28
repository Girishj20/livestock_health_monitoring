from app.utils.security import verify_farm_access, verify_animal_access
from app.models.farm import Farm
from app.models.animal import Animal
from app.extensions import db_session


def test_cross_farm_data_isolation(auth_users, test_farm_and_animal):
    f1 = auth_users['farmer1']
    f2 = auth_users['farmer2']
    farm1 = test_farm_and_animal['farm']
    animal1 = test_farm_and_animal['animal']

    # Farmer 1 owns Farm 1
    assert verify_farm_access(f1, farm1.id, required_level='view') is True
    assert verify_animal_access(f1, animal1.id, required_level='view') is True

    # Farmer 2 does NOT have access to Farm 1 or Animal 1
    assert verify_farm_access(f2, farm1.id, required_level='view') is False
    assert verify_animal_access(f2, animal1.id, required_level='view') is False


def test_admin_and_vet_cross_access(auth_users, test_farm_and_animal):
    admin = auth_users['admin']
    vet = auth_users['vet']
    farm1 = test_farm_and_animal['farm']
    animal1 = test_farm_and_animal['animal']

    # Both Admin and Vet have universal view authority for clinical / supervisory tasks
    assert verify_farm_access(admin, farm1.id, required_level='view') is True
    assert verify_animal_access(admin, animal1.id, required_level='view') is True

    assert verify_farm_access(vet, farm1.id, required_level='view') is True
    assert verify_animal_access(vet, animal1.id, required_level='view') is True


def test_admin_console_rbac(client, auth_users):
    farmer = auth_users['farmer1']
    admin = auth_users['admin']

    # Farmer attempts to access admin dashboard -> redirected
    with client.session_transaction() as sess:
        sess['user_id'] = farmer.id
        sess['user_role'] = farmer.role

    res_farmer = client.get('/admin', follow_redirects=False)
    assert res_farmer.status_code == 302
    assert '/dashboard' in res_farmer.location

    # Admin accesses admin dashboard -> allowed 200 OK
    with client.session_transaction() as sess:
        sess['user_id'] = admin.id
        sess['user_role'] = admin.role

    res_admin = client.get('/admin', follow_redirects=False)
    assert res_admin.status_code == 200
    assert b"System Administration Console" in res_admin.data
