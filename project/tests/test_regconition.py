

def test_create(test_client, test_pic_addr):
    response = test_client.post("/user/", json={"name":"obama"},)
    assert response.status_code == 200
    userid = response.json()['id']

    pic_file = open(test_pic_addr.joinpath("obama.png"), "rb")
    response = test_client.post(
        f"/user/{userid}/picture/",
        files={"upload_file": ("pic", pic_file, "image/png")}
    )
    assert response.status_code == 200

    pic_file.seek(0)
    response = test_client.get(
        f"/user/{userid}/verification/",
        files={"upload_file": ("pic", pic_file, "image/png")}
    )
    assert response.status_code == 200
    assert response.json()

    pic_file2 = open(test_pic_addr.joinpath("baiden.png"), "rb")
    response = test_client.get(
        f"/user/{userid}/verification/",
        files={"upload_file": ("pic", pic_file2, "image/png")}
    )
    assert response.status_code == 200
    assert not response.json()
    import pdb; pdb.set_trace()

