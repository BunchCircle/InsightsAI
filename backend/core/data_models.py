from dataclasses import dataclass

@dataclass
class InputData:
    variable_name: str
    data_path: str
    data_description: str

@dataclass
class User:
    id: int
    username: str
    password_hash: str
