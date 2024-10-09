#HAVE TO IMPORT realestate.db and start engine

#MUST CAST dtarp REID to integer before == FAVORITES

# Example function to add a favorite for a user
def add_favorite(user_id, reid):
    new_favorite = Favorites(user_id=user_id, reid=reid)
    session.add(new_favorite)
    session.commit()
    print(f"Favorite added for user {user_id} with reid {reid}")

# Example function to query favorites for a user
def query_user_favorites(user_id):
    favorites = session.query(Favorites).filter_by(user_id=user_id).all()
    for favorite in favorites:
        print(f"User {user_id} has favorite with reid {favorite.reid}")