PRAGMA foreign_keys = ON;

-- Notes : uniquement par users Discord (MVP)
CREATE TABLE IF NOT EXISTS dish_ratings (
  rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id INTEGER NOT NULL,
  dish_id INTEGER NOT NULL,
  meal_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  comment TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(guild_id, dish_id, meal_id, user_id),
  FOREIGN KEY(guild_id) REFERENCES guild_config(guild_id) ON DELETE CASCADE,
  FOREIGN KEY(dish_id) REFERENCES dishes(dish_id) ON DELETE CASCADE,
  FOREIGN KEY(meal_id) REFERENCES meals(meal_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ratings_dish ON dish_ratings(guild_id, dish_id);
