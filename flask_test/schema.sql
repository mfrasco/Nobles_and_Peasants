drop table if exists kingdom;
create table kingdom (
    id integer primary key,
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
