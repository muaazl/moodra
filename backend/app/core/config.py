from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    SPACY_MODEL: str = "en_core_web_sm"
    SENTIMENT_MODEL: str = "SamLowe/roberta-base-go_emotions"
    TOXICITY_MODEL: str = "unitary/unbiased-toxic-roberta"
    TOPIC_MODEL: str = "all-MiniLM-L6-v2"
    class Config:
        env_file = ".env"
settings = Settings()
