drop table if exists parties;
create table parties (
    party_id text primary key,
    password text not null
);

drop table if exists players;
create table players (
    id text not null,
    party_id text not null,
    player_status text not null,
    coin integer not null,
    noble_id text,
    drinks integer not null,
    soldiers integer not null
);

drop table if exists outlaws;
create table outlaws (
    party_id text not null,
    noble_id text not null,
    peasant_id text not null
);

drop table if exists drinks;
create table drinks (
    party_id text not null,
    drink_name text not null,
    drink_cost integer not null
);

drop table if exists starting_coin;
create table starting_coin (
    party_id text not null,
    player_status text not null,
    coin integer not null
);

drop table if exists quest_rewards;
create table quest_rewards (
    party_id text not null,
    difficulty text not null,
    reward integer not null
);

drop table if exists quests;
create table quests (
    party_id text not null,
    quest text not null,
    difficulty text not null
);

drop table if exists challenges;
create table challenges (
    party_id text not null,
    challenge text not null
);
