from pydantic import BaseModel, Field, EmailStr


class UserSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    
    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'email': 'user0@gmail.com',
                    'password': 'user0'
                }
            ]
        }
    }