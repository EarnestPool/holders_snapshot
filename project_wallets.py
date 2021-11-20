import requests
import json
import os
from helper import *
import collections
import csv
from collections import OrderedDict

# You can put your API key here to skip the authentication loop
API_KEY = ''

# You can provide the policy id/ids as a list here to skip the policy id loop
policy_ids = []

ready = False

if API_KEY:
	ready = True
while not ready:
	API_KEY = input('Please input your blockfrost api key (project_id): ')

	auth_headers={'project_id': API_KEY}

	r = requests.get('https://cardano-mainnet.blockfrost.io/api/v0/', headers = auth_headers)

	r = json.loads(r.text)

	error_code = r.get('status_code', None)

	print('\nVerifying...\n')

	if error_code:
		error_message = r.get('message', None)
		print(f'Error: {error_message}') #{r.get('message', None)}')
		print('Please try again\n')
	else:
		print('\nSUCCESS! You are authenticated\n')
		ready = True

cozy_analytics = CozyAnalytics(API_KEY)


correct = False

if policy_ids:
	correct = True

while not correct:
	print('Please provide the following info:')
	policy_ids = input('project policy id or policy ids (separating by comma and space): ')
	policy_ids = policy_ids.split(', ')
	
	print('\nHere is the policy id/ids you provided:\n')
	for policy_id in policy_ids:
		print(policy_id)

	r = input('\nIs this correct? (y/n): ')

	if r == 'y':
		print('\nAwesome! Let\'s continue!')
		correct = True
	else:
		print('\nLet\'s try again!')

asset_ids = []
if asset_ids:
	pass
else:
	if policy_ids:
		print('Finding the NFTs of provided policy/policies:')
		for policy in policy_ids:
			temp = cozy_analytics.get_nfts_from_policy(policy)
			asset_ids += temp

	with open('asset_ids.json','w') as f:
		json.dump({'asset_ids':asset_ids}, f)

# now let's find the holders
asset_ownership_dict = cozy_analytics.get_holders_dict(asset_ids)

with open('asset_ownership_dict.json','w') as f:
	json.dump(asset_ownership_dict,f)

holders = {}
for key, value in asset_ownership_dict.items():
   stake_addr = value[1]
   if stake_addr in holders:
      small_list = holders[stake_addr] + [key]
      holders[stake_addr] = small_list
   else:
      holders[stake_addr] = [key]

assets_per_holder = {}
for key, value in holders.items():
    assets_per_holder[key] = len(value)

sorted_dict = collections.OrderedDict(assets_per_holder)

# open the file in the write mode
f = open('holders.csv', 'w')

# create the csv writer
writer = csv.writer(f)

writer.writerow(['wallet stake address','# of assets with the policy'])

for w in sorted(assets_per_holder, key=assets_per_holder.get, reverse=True):
    writer.writerow([w, assets_per_holder[w]])

# close the file
f.close()

ordered_assets_per_holder = {}
for key in sorted(assets_per_holder, key=assets_per_holder.get, reverse=True):
	ordered_assets_per_holder[key] = assets_per_holder[key]

with open('holders.json','w') as f:
	json.dump(ordered_assets_per_holder, f)