from pydantic import BaseModel

class OmadaConfig(BaseModel):
    host: str
    username: str
    password: str

class HomeAssistantConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str

class Config(BaseModel):
    interval: int
    omada: OmadaConfig
    homeassistant: HomeAssistantConfig
    devices: dict[str, str]

def load_config(filename: str) -> Config:
    with open(filename) as f:
        config = Config.parse_raw(f.read())
    return config
