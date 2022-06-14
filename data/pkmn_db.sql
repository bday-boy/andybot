CREATE TABLE IF NOT EXISTS PokemonSpecies (
    name            TEXT    PRIMARY KEY,
    dex_number      INTEGER,
    generation      INTEGER,
    is_legendary    INTEGER,
    is_mythical     INTEGER,
    fully_evolved   INTEGER
);

CREATE TABLE IF NOT EXISTS PokemonForms (
    species_name    TEXT,
    form_name       TEXT    PRIMARY KEY,
    is_alt_form     INTEGER,
    is_viable       INTEGER,
    type_1          TEXT,
    type_2          TEXT,
    ability_1       TEXT,
    ability_2       TEXT,
    hidden_ability  TEXT,
    bst             INTEGER,
    hp              INTEGER,
    atk             INTEGER,
    def             INTEGER,
    spa             INTEGER,
    spd             INTEGER,
    spe             INTEGER,
    speed_rank      REAL,
    FOREIGN KEY (species_name)
        REFERENCES PokemonSpecies (name)
            ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS PokemonRoles (
    form_name               TEXT PRIMARY KEY,
    physical_durability     REAL,
    special_durability      REAL,
    physical_offense        REAL,
    special_offense         REAL,
    offense_defense_bias    REAL,
    physical_special_bias   REAL,
    base_stat_ranking       REAL,
    FOREIGN KEY (form_name)
        REFERENCES PokemonForms (form_name)
            ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS TypeDamageTo (
    type        TEXT PRIMARY KEY,
    normal      REAL,
    fighting    REAL,
    flying      REAL,
    poison      REAL,
    ground      REAL,
    rock        REAL,
    bug         REAL,
    ghost       REAL,
    steel       REAL,
    fire        REAL,
    water       REAL,
    grass       REAL,
    electric    REAL,
    psychic     REAL,
    ice         REAL,
    dragon      REAL,
    dark        REAL,
    fairy       REAL
);

CREATE TABLE IF NOT EXISTS TypeDamageFrom (
    type        TEXT PRIMARY KEY,
    normal      REAL,
    fighting    REAL,
    flying      REAL,
    poison      REAL,
    ground      REAL,
    rock        REAL,
    bug         REAL,
    ghost       REAL,
    steel       REAL,
    fire        REAL,
    water       REAL,
    grass       REAL,
    electric    REAL,
    psychic     REAL,
    ice         REAL,
    dragon      REAL,
    dark        REAL,
    fairy       REAL
);