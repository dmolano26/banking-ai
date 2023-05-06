#!/bin/bash

echo New Account Alice:

curl -s -H "Content-Type: application/json" -X POST -d '{"full_name": "alice", "email":"alice@example.com","password":"alice"}' http://localhost:5000/api/v1/account

echo New Account Bob:

curl -s -H "Content-Type: application/json" -X POST -d '{"full_name": "bob", "email":"bob@example.com","password":"bob"}' http://localhost:5000/api/v1/account

echo Login Alice:

ALICETOKEN=$(curl -s -H "Content-Type: application/json" -X POST -d '{"username":"alice@example.com","password":"alice"}' http://localhost:5000/auth | jq -r ".access_token")

echo Login Bob:

BOBTOKEN=$(curl -s -H "Content-Type: application/json" -X POST -d '{"username":"bob@example.com","password":"bob"}' http://localhost:5000/auth | jq -r ".access_token")

echo Get Account Alice:

ALICE=$(curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: JWT $ALICETOKEN" | jq -r ".identity")
echo $ALICE 
ALICEBALANCE=$(curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: JWT $ALICETOKEN" | jq -r ".balance")
echo $ALICEBALANCE

echo Get Account Bob:

BOB=$(curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: JWT $BOBTOKEN" | jq -r ".identity")
echo $BOB 

echo Deposit 100 dollars Alice:

ALICEDEPOSIT=$(curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/deposit -H "Authorization: JWT $ALICETOKEN" -d '{"amount_in_cents": 10000}' | jq -r ".data")

if [ "$ALICEDEPOSIT" = "10000" ]
then
echo Success
else
echo $ALICEDEPOSIT
echo Deposit Failed
exit 1
fi

echo Get Account Alice:

curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: JWT $ALICETOKEN"

echo Transfer 10 dollars to Bob:

TRANSFER='{"amount_in_cents": 1000, "destination": "'$BOB'"}'
echo $TRANSFER
curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/transfer -H "Authorization: JWT $ALICETOKEN" -d "$TRANSFER"

echo Get Account Alice:

curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: JWT $ALICETOKEN"

echo Get Account Bob:

curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: JWT $BOBTOKEN"


echo Transfer 10 dollars to unknown:

TRANSFER='{"amount_in_cents": 1000, "destination": "0db7b668-2856-4c86-83cf-a0b42c80d935"}'
RESULT=$(curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/transfer -H "Authorization: JWT $ALICETOKEN" -d "$TRANSFER" | jq -r ".error")

if [ "<class 'banking.applicationmodel.AccountNotFoundError'>: 0db7b668-2856-4c86-83cf-a0b42c80d935" = "$RESULT" ]
then
echo Successfully blocked an invalid transfer
else
echo Failed, should have blocked an invalid transfer
echo $RESULT
exit 1
fi

