drop table if exists kingdom;
create table kingdom (
    id text primary key,
    status text not null,
    coin integer not null,
    allegiance text,
    drinks integer not null,
    soldiers integer not null
);

drop table if exists banned;
create table banned (
    noble text,
    outlaw text
);

drop table if exists drinks;
create table drinks (
    name text primary key,
    coin integer not null
);

drop table if exists starting_coin;
create table starting_coin (
    status text primary key,
    coin integer not null
);

drop table if exists quests;
create table quests (
    quest text,
    level text
);

drop table if exists challenges;
create table challenges (
    challenge text
);

drop table if exists wages;
create table wages (
    level text primary key,
    coin integer not null
);

insert into drinks values ('water', -1);
insert into drinks values ('beer', 5);
insert into starting_coin values ('noble', 50);
insert into starting_coin values ('peasant', 0);
insert into wages values ('easy', 10);
insert into wages values ('medium', 15);
insert into wages values ('hard', 25);

insert into quests (quest, level) values
    ("Stare into someone's eyes for a whole minute without laughing. You choose the person.", 'easy'),
    ("Write a Facebook message to the last person you messaged about how much you love one of the following: Star Wars, the Disney Channel, Spiderman.", 'medium'),
    ("Put a blindfold on, find someone at the party, and touch their face. Guess who.", 'medium'),
    ("Find three people and give them the most genuine, heartfelt complements.", 'easy'),
    ("Dance with an inanimate object for a minute.", 'medium'),
    ("Allow yourself to be tickled for thirty seconds. You choose your torturer.", 'medium'),
    ("Eat some food in the sexist way possible.", 'medium'),
    ("Show me the following emotions in this order: rage, confusion, depression, excitement, fear.", 'easy'),
    ("Break dance, do the robot, or moonwalk.", 'easy'),
    ("Go give someone a hug.", 'easy'),
    ("Name all seven of Snow White's dwarfs in thirty seconds.", 'easy'),
    ("Pretend to be someone in the room for a minute.", 'easy'),
    ("Make a statue and hold that position for a minute.", 'easy'),
    ("Have a conversation with an inanimate object for a minute.", 'easy'),
    ("Put food on someone else's stomach and eat it off.", 'hard'),
    ("Act out a scene from your favorite movie.", 'medium'),
    ("Be a monkey for five minutes.", 'medium'),
    ("Scare someone at this party.", 'medium'),
    ("Moan passionately. Louder. People should hear you moan.", 'hard'),
    ("Seduce someone with facial expressions.", 'hard'),
    ("Sit on a chair and peddle as if riding a bicycle. Pantomime an entire Tour de France stage, complete with hill ascents and a dramatic finish.", 'easy'),
    ("Put ice cubes in your armpits and act like a train for a minute.", 'medium'),
    ("Make someone in the room laugh.", 'medium'),
    ("Put a blindfold on and slow dance with someone.", 'medium'),
    ("Pick your favorite song and dance to it until the song ends.", 'medium');

insert into challenges (challenge) values
    ('DUEL: Challenge your target to a game of beer pong with one cup. The first person to make a shot wins. You go first.'),
    ('DEATH BY EMBARSSMENT: Convince your target to sing at least one line from the next song that plays.'),
    ('POISON: Poison the drink of your target with salt. He or she must take at least one sip of the poisoned drink.'),
    ('DUEL: Yell "HELLO! MY NAME IS INIGO MONTOYA! YOU KILLED MY FATHER! PREPARE TO DIE!". Challenge your target to one game of flip cup. The loser dies.'),
    ('SIREN: Lure your target to a secluded area. If they come with you, whisper, "I know you want me" in his or her ear.'),
    ("STABBED IN THE BACK: Go in for a friendly hug and secretly place a sign with an appropriate insult on your target's back. The sign must be kept on for at least 2 minutes to be successful."),
    ('REBELLION: There is unsettlement among the peasants. Convince at least three other peasants to hold hands and form a circle around your target. Chant, "That blood which thou hast spilled, should join you closely in an eternal bond" three times as you circle the target. The target must not leave the circle until the chanting is complete.'),
    ('WAR: Each side is allowed to choose an army of any three people to play flip cup. Both armies MUST march into battle in formation. The general of the losing side dies.'),
    ('VENOMOUS SNAKE: Slither (you MUST be visibly slithering!) to your target and touch them.'),
    ("RACE: Give someone a piggyback around the apartment. Time it. Tell your victim to carry the same person. Who is faster?");
