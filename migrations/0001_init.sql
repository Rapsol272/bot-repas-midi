PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
  version TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Configuration par serveur (guild)
CREATE TABLE IF NOT EXISTS guild_config (
  guild_id INTEGER PRIMARY KEY,
  admin_role_name TEXT NOT NULL DEFAULT 'Chef',
  timezone TEXT NOT NULL DEFAULT 'Europe/Paris',
  default_meal_price_cents INTEGER NOT NULL DEFAULT 500,
  menu_channel_id INTEGER NULL
);

-- Repas (menu du jour)
CREATE TABLE IF NOT EXISTS meals (
  meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id INTEGER NOT NULL,
  meal_date TEXT NOT NULL,                 -- YYYY-MM-DD
  title TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  price_cents INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'OPEN',     -- OPEN/CLOSED
  created_by_user_id INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  closed_at TEXT NULL,
  UNIQUE(guild_id, meal_date),
  FOREIGN KEY(guild_id) REFERENCES guild_config(guild_id) ON DELETE CASCADE
);

-- Participants Discord
CREATE TABLE IF NOT EXISTS participants (
  participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
  meal_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  status TEXT NOT NULL,                    -- YES/NO
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(meal_id, user_id),
  FOREIGN KEY(meal_id) REFERENCES meals(meal_id) ON DELETE CASCADE
);

-- Invités externes : "code" + nom + participation à un repas
CREATE TABLE IF NOT EXISTS external_invites (
  invite_id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id INTEGER NOT NULL,
  code TEXT NOT NULL UNIQUE,               -- code de participation (ex: ABCD-1234)
  display_name TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  created_by_user_id INTEGER NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1,
  FOREIGN KEY(guild_id) REFERENCES guild_config(guild_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS external_participants (
  ext_participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
  meal_id INTEGER NOT NULL,
  invite_id INTEGER NOT NULL,
  status TEXT NOT NULL,                    -- YES/NO
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(meal_id, invite_id),
  FOREIGN KEY(meal_id) REFERENCES meals(meal_id) ON DELETE CASCADE,
  FOREIGN KEY(invite_id) REFERENCES external_invites(invite_id) ON DELETE CASCADE
);

-- Catalogue plats (historisation)
CREATE TABLE IF NOT EXISTS dishes (
  dish_id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  normalized_name TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(guild_id, normalized_name),
  FOREIGN KEY(guild_id) REFERENCES guild_config(guild_id) ON DELETE CASCADE
);

-- Association repas -> plats (un repas peut contenir plusieurs plats)
CREATE TABLE IF NOT EXISTS meal_dishes (
  meal_id INTEGER NOT NULL,
  dish_id INTEGER NOT NULL,
  PRIMARY KEY (meal_id, dish_id),
  FOREIGN KEY(meal_id) REFERENCES meals(meal_id) ON DELETE CASCADE,
  FOREIGN KEY(dish_id) REFERENCES dishes(dish_id) ON DELETE CASCADE
);

-- Ledger (cagnote) : une écriture par dette de repas, remboursements, ajustements
CREATE TABLE IF NOT EXISTS ledger_entries (
  entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id INTEGER NOT NULL,
  user_id INTEGER NULL,                    -- NULL possible pour écritures globales (évite pour MVP)
  meal_id INTEGER NULL,
  entry_type TEXT NOT NULL,                -- DEBIT/CREDIT/ADJUST
  amount_cents INTEGER NOT NULL,           -- positif
  status TEXT NOT NULL DEFAULT 'POSTED',    -- POSTED ou PENDING pour remboursement
  note TEXT NOT NULL DEFAULT '',
  created_by_user_id INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  approved_by_user_id INTEGER NULL,
  approved_at TEXT NULL,
  FOREIGN KEY(guild_id) REFERENCES guild_config(guild_id) ON DELETE CASCADE,
  FOREIGN KEY(meal_id) REFERENCES meals(meal_id) ON DELETE SET NULL
);

-- Audit log (optionnel mais utile)
CREATE TABLE IF NOT EXISTS audit_log (
  audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id INTEGER NOT NULL,
  actor_user_id INTEGER NOT NULL,
  action TEXT NOT NULL,
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(guild_id) REFERENCES guild_config(guild_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_meals_guild_date ON meals(guild_id, meal_date);
CREATE INDEX IF NOT EXISTS idx_participants_meal ON participants(meal_id);
CREATE INDEX IF NOT EXISTS idx_ledger_user ON ledger_entries(guild_id, user_id);
CREATE INDEX IF NOT EXISTS idx_ledger_status ON ledger_entries(guild_id, status);
