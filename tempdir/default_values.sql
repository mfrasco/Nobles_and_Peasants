insert into drinks (party_id, drink_name, drink_cost) values
    (~PARTY_ID~, 'water', -1),
    (~PARTY_ID~, 'beer', 3);

insert into starting_coin (party_id, player_status, coin) values
    (~PARTY_ID~, 'noble', 50),
    (~PARTY_ID~, 'peasant', 0);

insert into quest_rewards (party_id, difficulty, reward) values
    (~PARTY_ID~, 'easy', 10),
    (~PARTY_ID~, 'medium', 15),
    (~PARTY_ID~, 'hard', 25);

insert into quests (party_id, quest, difficulty) values
    (~PARTY_ID~, "Stare into someone's eyes for a whole minute without laughing. You choose the person.", 'easy'),
    (~PARTY_ID~, "Write a Facebook message to the last person you messaged about how much you love one of the following: Star Wars, the Disney Channel, Spiderman.", 'medium'),
    (~PARTY_ID~, "Put a blindfold on, find someone at the party, and touch their face. Guess who.", 'medium'),
    (~PARTY_ID~, "Find three people and give them the most genuine, heartfelt complements.", 'easy'),
    (~PARTY_ID~, "Dance with an inanimate object for a minute.", 'medium'),
    (~PARTY_ID~, "Allow yourself to be tickled for thirty seconds. You choose your torturer.", 'medium'),
    (~PARTY_ID~, "Eat some food in the sexist way possible.", 'medium'),
    (~PARTY_ID~, "Show me the following emotions in this order: rage, confusion, depression, excitement, fear.", 'easy'),
    (~PARTY_ID~, "Break dance, do the robot, or moonwalk.", 'easy'),
    (~PARTY_ID~, "Go give someone a hug.", 'easy'),
    (~PARTY_ID~, "Name all seven of Snow White's dwarfs in thirty seconds.", 'easy'),
    (~PARTY_ID~, "Pretend to be someone in the room for a minute.", 'easy'),
    (~PARTY_ID~, "Make a statue and hold that position for a minute.", 'easy'),
    (~PARTY_ID~, "Have a conversation with an inanimate object for a minute.", 'easy'),
    (~PARTY_ID~, "Put food on someone else's stomach and eat it off.", 'hard'),
    (~PARTY_ID~, "Act out a scene from your favorite movie.", 'medium'),
    (~PARTY_ID~, "Be a monkey for five minutes.", 'medium'),
    (~PARTY_ID~, "Scare someone at this party.", 'medium'),
    (~PARTY_ID~, "Moan passionately. Louder. People should hear you moan.", 'hard'),
    (~PARTY_ID~, "Seduce someone with facial expressions.", 'hard'),
    (~PARTY_ID~, "Sit on a chair and peddle as if riding a bicycle. Pantomime an entire Tour de France stage, complete with hill ascents and a dramatic finish.", 'easy'),
    (~PARTY_ID~, "Put ice cubes in your armpits and act like a train for a minute.", 'medium'),
    (~PARTY_ID~, "Make someone in the room laugh.", 'medium'),
    (~PARTY_ID~, "Put a blindfold on and slow dance with someone.", 'medium'),
    (~PARTY_ID~, "Pick your favorite song and dance to it until the song ends.", 'medium');

insert into challenges (party_id, challenge) values
    (~PARTY_ID~, 'DUEL: Challenge your target to a game of beer pong with one cup. The first person to make a shot wins. You go first.'),
    (~PARTY_ID~, 'DEATH BY EMBARSSMENT: Convince your target to sing at least one line from the next song that plays.'),
    (~PARTY_ID~, 'POISON: Poison the drink of your target with salt. He or she must take at least one sip of the poisoned drink.'),
    (~PARTY_ID~, 'DUEL: Yell "HELLO! MY NAME IS INIGO MONTOYA! YOU KILLED MY FATHER! PREPARE TO DIE!". Challenge your target to one game of flip cup. The loser dies.'),
    (~PARTY_ID~, 'SIREN: Lure your target to a secluded area. If they come with you, whisper, "I know you want me" in his or her ear.'),
    (~PARTY_ID~, "STABBED IN THE BACK: Go in for a friendly hug and secretly place a sign with an appropriate insult on your target's back. The sign must be kept on for at least 2 minutes to be successful."),
    (~PARTY_ID~, 'REBELLION: There is unsettlement among the peasants. Convince at least three other peasants to hold hands and form a circle around your target. Chant, "That blood which thou hast spilled, should join you closely in an eternal bond" three times as you circle the target. The target must not leave the circle until the chanting is complete.'),
    (~PARTY_ID~, 'WAR: Each side is allowed to choose an army of any three people to play flip cup. Both armies MUST march into battle in formation. The general of the losing side dies.'),
    (~PARTY_ID~, 'VENOMOUS SNAKE: Slither (you MUST be visibly slithering!) to your target and touch them.'),
    (~PARTY_ID~, "RACE: Give someone a piggyback around the apartment. Time it. Tell your victim to carry the same person. Who is faster?");
