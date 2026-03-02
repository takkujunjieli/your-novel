from sqlmodel import Session, select
from core.db import engine, create_db_and_tables
from models.content import Content, Chapter

def seed_data():
    # 1. Ensure tables exist
    create_db_and_tables()
    
    with Session(engine) as session:
        # 2. Check if data already exists
        statement = select(Content)
        result = session.exec(statement)
        if result.first():
            print("Data already seeded!")
            return

        # 3. Create a Novel
        novel = Content(
            title="Whispers of the Neon Night",
            description="A cyberpunk thriller set in the year 2088.",
            tags=["Cyberpunk", "Adult", "Mystery"]
        )
        session.add(novel)
        session.commit()
        session.refresh(novel)

        # 4. Create a Chapter for that Novel
        chapter = Chapter(
            content_id=novel.id,
            chapter_number=1,
            title="The Silver Rain",
            content="The rain fell like liquid chrome against the glass...",
            word_count=10
        )
        session.add(chapter)
        session.commit()
        
        print(f"Successfully seeded novel: {novel.title}")

if __name__ == "__main__":
    seed_data()
