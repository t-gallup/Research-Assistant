import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Request


def init_firebase():
    # Access Firebase credentials through Firebase JSON
    cred = credentials.Certificate('firebase-adminsdk.json')

    firebase_admin.initialize_app(cred)


async def verify_firebase_token(request: Request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        raise HTTPException(status_code=401, detail='No token provided')

    try:
        decoded_token = auth.verify_id_token(token)
        request.state.user_id = decoded_token['uid']
        return decoded_token
    except Exception as _:
        raise HTTPException(status_code=401, detail='Invalid token')
