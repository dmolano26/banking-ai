#!/bin/bash

echo New Account Alice:

curl -s -H "Content-Type: application/json" -X POST -d '{"full_name": "alice", "email_address":"alice@example.com","password":"alice"}' http://localhost:5000/api/v1/signup

echo New Account Bob:

curl -s -H "Content-Type: application/json" -X POST -d '{"full_name": "bob", "email_address":"bob@example.com","password":"bob"}' http://localhost:5000/api/v1/signup

echo Login Alice:

ALICETOKEN=$(curl -s -H "Content-Type: application/json" -X POST -d '{"email_address":"alice@example.com","password":"alice"}' http://localhost:5000/api/v1/login | jq -r ".access_token")

echo Login Bob:

BOBTOKEN=$(curl -s -H "Content-Type: application/json" -X POST -d '{"email_address":"bob@example.com","password":"bob"}' http://localhost:5000/api/v1/login | jq -r ".access_token")

echo Get Account Alice:

ALICE=$(curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: Bearer $ALICETOKEN" | jq -r ".identity")
echo $ALICE 
ALICEBALANCE=$(curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: Bearer $ALICETOKEN" | jq -r ".balance")
echo $ALICEBALANCE

echo Get Account Bob:

BOB=$(curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: Bearer $BOBTOKEN" | jq -r ".identity")
echo $BOB 

echo Deposit 100 dollars Alice:

ALICEDEPOSIT=$(curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/deposit -H "Authorization: Bearer $ALICETOKEN" -d '{"amount": 100}' | jq -r ".result")

if [ "$ALICEDEPOSIT" = "success" ]
then
echo Success deposit
else
echo $ALICEDEPOSIT
echo Deposit Failed
exit 1
fi

echo Get Account Alice:

curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: Bearer $ALICETOKEN"

echo Transfer 10 dollars to Bob:

TRANSFER='{"amount": 10, "destination_id": "'$BOB'"}'
echo $TRANSFER
curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/transfer -H "Authorization: Bearer $ALICETOKEN" -d "$TRANSFER"

echo Get Account Alice:

curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: Bearer $ALICETOKEN"

echo Get Account Bob:

curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: Bearer $BOBTOKEN"


echo Transfer 10 dollars to unknown:

TRANSFER='{"amount": 10, "destination_id": "0db7b668-2856-4c86-83cf-a0b42c80d935"}'
RESULT=$(curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/transfer -H "Authorization: Bearer $ALICETOKEN" -d "$TRANSFER" | jq -r ".error")

if [ "Account not found." = "$RESULT" ]
then
echo Successfully blocked an invalid transfer
else
echo Failed, should have blocked an invalid transfer
echo $RESULT
exit 1
fi

echo Withdraw 10 dollars on Alice account:

ALICEDEPOSIT=$(curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/withdraw -H "Authorization: Bearer $ALICETOKEN" -d '{"amount": 10}' | jq -r ".result")

if [ "$ALICEDEPOSIT" = "success" ]
then
echo Success withdraw
else
echo $ALICEDEPOSIT
echo Deposit Failed
exit 1
fi

echo Withdraw 1000 dollars on Alice account:

ALICEDEPOSIT=$(curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/withdraw -H "Authorization: Bearer $ALICETOKEN" -d '{"amount": 1000}' | jq -r ".message")

if [ "$ALICEDEPOSIT" = "success" ]
then
echo Success withdraw
exit 1
else
echo $ALICEDEPOSIT
fi

