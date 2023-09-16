users_db = [
    {
        'user_id': 0,
        'email': 'user0@gmail.com',
        'password': '$2b$12$QXzeLeNIcuxIz94cd1ce/OlsFkgr3oTCbThVmSliZFD1VYDSDqFFa' # user0
    },
    {
        'user_id': 1,
        'email': 'user1@gmail.com',
        'password': '$2b$12$ZspQ4qmHfDldmEm6EDbJPeh99IOK/NryCZCPdhhCaRar4b6d6luYi' # user1
    },
    {
        'user_id': 2,
        'email': 'user2@gmail.com',
        'password': '$2b$12$rPWDsHeD1x1MGmAvDbwGBuQF7rm.KaW/uUbe.hamS7NvGJjwOjcla' # user2
    }
]


def get_user_by_email(email):
    for user in users_db:
        if user['email'] == email:
            return user