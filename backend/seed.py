import pandas as pd
from app import app, db, CardContent

def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        df = pd.read_csv('backend/cards.csv')

        for index, row in df.iterrows():
            card = CardContent(
                card_id=row['card_id'],
                card_name=row['card_name'],
                image_url=row['image_url'],
                text_sos_state=row['text_sos_state'],
                text_sos_resource=row['text_sos_resource'],
                text_sos_action=row['text_sos_action'],
                text_daily=row['text_daily'],
                text_love_self=row['text_love_self']
            )
            db.session.add(card)

        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
