from http import HTTPStatus


def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "username": "testusername",
            "password": "password",
            "email": "tes@tes.com",
        },
    )  # act (ação)

    assert response.status_code == HTTPStatus.CREATED

    assert response.json() == {
        "username": "testusername",
        "email": "tes@tes.com",
        "id": 1,
    }


def test_read_users(client):
    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "users": [
            {"username": "testusername", "email": "tes@tes.com", "id": 1}
        ]
    }


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            "username": "testusername", "email": "tes@tes.com", "id": 1, "password": "senha1"

        }
        )

 # assert response.status_code ==
