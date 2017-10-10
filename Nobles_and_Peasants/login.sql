drop table if exists parties;
create table parties (
    party_id text primary key,
    password text not null
);