EXISTING_EMAIL={
    "message":"The email already exists in the database"
}
BAD_REQUEST={
    "status_code":400,
    "detail":"THE SERVER CANNOT PROCESS YOUR REQUEST!",
}
UNAUTHORIZED={
    "status_code":401,
    "detail":"AUTHETICATION IS REQUIRED OR FAILED!"
}
FORBIDDEN={
    "status_code":403,
    "detail":"THE SERVER REFUSES TO AUTHORIZE YOUR REQUEST!"
}
NOT_FOUND={
    "status_code":404,
    "detail":"RESOURCE COULD NOT BE FOUND!"
}
METHOD_NOT_ALLOWED={
    "status_code":405,
    "detail":"REQUESTED METHOD IS NOT SUPPORTED!"
}
REQUEST_TIMEOUT={
    "status_code":408,
    "detail":"SERVER TIMED OUT WAITING!"
}
CONFLICT={
    "status_code":409,
    "detail":"REQUEST CANNOT BE COMPLETED DUE TO A CONFLICT WITH THE CURRENT STATE!"
}
TOO_MANY_REQUESTS={
    "status_code":429,
    "detail":"TOO MANY REQUESTS!"
}
INTERNAL_SERVER_ERROR={
    "status_code":500,
    "detail":"INTERNAL SERVER ERROR!"
}
