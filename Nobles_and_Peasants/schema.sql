drop table if exists parties;
create table parties (
    id integer primary key autoincrement,
    party_name text unique not null,
    password text not null
);

drop table if exists players;
create table players (
    id integer primary key autoincrement,
    party_id integer not null,
    player_name text not null,
    player_status text not null,
    coin integer not null,
    noble_name text,
    drinks integer not null,
    soldiers integer not null,
    foreign_key (party_id) references parties (id)
);

drop table if exists outlaws;
create table outlaws (
    id integer primary key autoincrement,
    party_id integer not null,
    noble_id integer not null,
    peasant_id integer not null,
    foreign_key (party_id) references parties (id),
    foreign_key (noble_id) references players (id),
    foreign_key (peasant_id) references players (id)
);

drop table if exists drinks;
create table drinks (
    id integer primary key autoincrement,
    party_id integer not null,
    drink_name text not null,
    drink_cost integer not null,
    foreign_key (party_id) references parties (id)
);

drop table if exists starting_coin;
create table starting_coin (
    id integer primary key autoincrement,
    party_id integer not null,
    player_status text not null,
    coin integer not null
);

drop table if exists quest_rewards;
create table quest_rewards (
    id integer primary key autoincrement,
    party_id integer not null,
    difficulty text not null,
    reward integer not null
);

drop table if exists quests;
create table quests (
    id integer primary key autoincrement,
    party_id integer not null,
    quest text not null,
    difficulty text not null
);

drop table if exists challenges;
create table challenges (
    id integer primary key autoincrement,
    party_id integer not null,
    challenge text not null
);
