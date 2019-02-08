CREATE TABLE `user` (
	`greyd_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`facebook_id`	TEXT NOT NULL,
	`full_name`	TEXT NOT NULL,
	`e_mail`	TEXT,
	`user_status`	INTEGER NOT NULL DEFAULT 0, /* 0=normal  1=authorized user 2=banned user */
	`user_level`	INTEGER NOT NULL DEFAULT 1,
	`total_score`	INTEGER NOT NULL DEFAULT 0,
	`location`	TEXT NOT NULL DEFAULT '0.0,0.0',
	`location_city`	TEXT
);

CREATE TABLE `guest` (
	`guest_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`lobby_id`	INTEGER NOT NULL DEFAULT 0,
	`location`	TEXT NOT NULL DEFAULT '0.0,0.0'
);

CREATE TABLE `lobbies` (
	`lobby_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`lobby_owner_greyd_id`	INTEGER NOT NULL,
	`lobby_status`	INTEGER NOT NULL DEFAULT 0, /* 0=preparing 1=on game 2=finished game */
	`lobby_center_location` TEXT NOT NULL DEFAULT '0.0,0.0',
	`lobby_name`	TEXT NOT NULL DEFAULT 'lobi',
	`game_distance`	INTEGER NOT NULL DEFAULT 25, /* maximum map zone m^2 type */
	`lobby_setup_time`	TEXT, /* dd/mm/yyyy hh:mm*/
	`game_start_time`	TEXT, /* dd/mm/yyyy hh:mm*/
	`game_end_time`	TEXT, /* dd/mm/yyyy hh:mm*/
	`game_life_number`	INTEGER NOT NULL DEFAULT 0, /* if life time equal 0 then the game will end with time */
	`game_max_time`	INTEGER NOT NULL DEFAULT 0, /* if max time equal 0 then game will end with life */
	`current_bait_location`	TEXT,
	`winner_greyd_id`	INTEGER
);

CREATE TABLE `lobbies_chat` (
	`chat_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`session_id`	INTEGER NOT NULL, /* user_to_lobby table session_id */
	`chat_content`	TEXT NOT NULL,
	`chat_time`	TEXT NOT NULL DEFAULT '01/01/1970 00:00' /* dd/mm/yyyy hh:mm */
);

CREATE TABLE `user_location` (
	`location_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`session_id`	INTEGER NOT NULL, /* user_to_lobby table session_id */
	`bait_location`	TEXT NOT NULL DEFAULT '0.0,0.0',
	`user_location`	TEXT NOT NULL DEFAULT '0.0,0.0',
	`is_bait_taken`	INTEGER NOT NULL DEFAULT 0 /* 0=false 1=true */
);

CREATE TABLE `user_to_lobby` (
	`session_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`lobby_id`	INTEGER NOT NULL, /* lobbies table relation lobby_id */
	`greyd_id`	INTEGER NOT NULL, /* user table relation user_id */
	`user_lobby_entry_time`	TEXT NOT NULL DEFAULT '01/01/1970 00:00',
	`user_lobby_exit_time`	TEXT NOT NULL DEFAULT '01/01/1970 00:00',
	`remaining_life` INTEGER DEFAULT 0,
	`is_game_won`	INTEGER DEFAULT 0 /* 0=false 1=true */
);
