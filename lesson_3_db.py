from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import lesson_3_models as models

engine = create_engine('sqlite:///gb_blog.db')  # Create an engine with SQLite connection
models.Base.metadata.create_all(bind=engine)  # Connection between Base class and the engine
SessionMaker = sessionmaker(bind=engine)  # Create SessionMaker with the engine
