drop table if exists parties;
create table parties (
    party_id text primary key,
    password text not null
);

drop table if exists kingdom;
create table kingdom (
    id text not null,
    party_id text not null,
    status text not null,
    coin integer not null,
    allegiance text,
    drinks integer not null,
    soldiers integer not null
);

drop table if exists banned;
create table banned (
    party_id text not null,
    noble text not null,
    outlaw text not null
);

drop table if exists drinks;
create table drinks (
    party_id text not null,
    name text not null,
    coin integer not null
);

drop table if exists starting_coin;
create table starting_coin (
    party_id text not null,
    status text not null,
    coin integer not null
);

drop table if exists quests;
create table quests (
    party_id text not null,
    quest text not null,
    level text not null
);

drop table if exists challenges;
create table challenges (
    party_id text not null,
    challenge text not null
);

drop table if exists wages;
create table wages (
    party_id text not null,
    level text not null,
    coin integer not null
);
