Project Plan
-----------------------

## Team
* 526555 Anna Lonka
* 478001 Ville Saarinen
* 292009 Jukka Nevalainen

## Goal

Online game store that serves both developers and players.

## Plans

We are going to implement and prioritise all the mandatory features, which means:  
**authentication**, using django user model with email authentication  
**basic player functionalities**, the database has a list of the games the player has bought, player has access to the games and can play them  
**basic developer functionalities**, the database has a list of the games the developer has made, track sold games  
**game/service interaction**, when the game ends, it  sends postMessage with the current score to database  

We are also going to try to do some extra features:  
**3rd party login**, using django's own app  
**mobile friendly**, bootstrap has functionality for this  
**social media sharing**, creating and using own functions to share in social media  


Models that we are going to do:
**user**(django user, player or developer group)  
**player_games**(userID, gameID)  
**developer_games**(userID, gameID)  
**games**(name, maker, url)  
**highscore**(playerid, gameid, score)  

Views that we are going to do:  
login, store, developer inventory, payment, game with high score, userinfo

## Process and Time Schedule

We are using slack as a communication platform and we will use Trello to track our project.

First we are going to estimate the effort that it takes to do different parts of the project, so that we can get a schedule. Initial estimations will be based on the available points for each feature. We will use Scrum-inspired development sprints to maintain working pace as the team’s size makes strict observance of Scrum unnecessary.

Features will be developed in their own feature branches, which will be merged into a development branch. Pull requests will be used to ensure code is reviewed. At the end of sprints, the development branch will be merged into master. We do not have release branches, as the product is not being used by customers during the project.

Following the course’s recommendations and requirements, we will use Django as our framework and Bootstrap as our front-end library.

- Week 51 project plan
- Week 52 setting up the project
- Weeks 1-2 working on the mandatory features
- Weeks 3-4 working on the mandatory features
- Weeks 5-6 working on the extra features
- Weeks 7-8 Polishing and testing the project and is done by 19.2. midnight

## Testing
We will use Django’s own testing framework. Testing will be done continuously during development.

## Risk Analysis
There is quite little time to do the project, so that might be a risk. We are going to prioritize the mandatory features, so that we would get a functioning product before the deadline.


## Final Submission

[Read it here](https://docs.google.com/document/d/1oYBlcDfPoMbxM9EBsQpR9cdCZMxmuFqG-wTBDbomxPk/edit?usp=sharing)