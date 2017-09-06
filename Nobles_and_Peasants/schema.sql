drop table if exists kingdom;
create table kingdom (
    id text primary key,
    status text not null,
    coin integer,
    allegiance text,
    drinks integer,
    soldiers integer
);

drop table if exists banned;
create table banned (
    noble text,
    outlaw text
);

drop table if exists drinks;
create table drinks (
    name text,
    coin integer
);

drop table if exists starting_coin;
create table starting_coin (
    status text,
    coin integer
);

insert into drinks values ('water', -1);
insert into starting_coin values ('noble', 50);
insert into starting_coin values ('peasant', 0);