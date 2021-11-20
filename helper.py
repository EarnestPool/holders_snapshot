import requests
import json
import os
import math

# code was originally writen for cozytokens.io 
class CozyAnalytics:
	def __init__(self, API_KEY):
		self.API_KEY = API_KEY

	def get_assets_page_by_policy_id(self, policy_id, page_num):
		API_KEY = self.API_KEY
		r = requests.get(('https://cardano-mainnet.blockfrost.io/api/v0/assets/policy/'+policy_id), headers={'project_id': API_KEY}, params={'page': page_num})
		return json.loads(r.text)


	def get_nfts_from_policy(self, policy):
		API_KEY = self.API_KEY
		print(f'Making a list of assets for \'{policy}\'')
		asset_ids = []

		page_num = 1

		finished = False

		assets = []
		while not finished:
			page_assets = self.get_assets_page_by_policy_id(policy, page_num)
			if page_assets:
				assets += page_assets
				print(f'Collected {(page_num-1)*100+len(page_assets)} assets of the policy')
				page_num += 1
			else:
				print('Done!')
				print(f'Total of {len(assets)} was collected')
				finished = True

		print('Filtering out the assets whose quantity is different from \'1\'.')
		for asset in assets:
			if int(asset['quantity']) == 1:
				asset_ids.append(asset['asset'])

		print(f'Total number of NFTs under this policy is {len(asset_ids)}')


		return asset_ids

	# https://cardano-mainnet.blockfrost.io/api/v0/assets/{asset}/addresses
	def get_info_on_addresses_by_asset(self, asset):
		API_KEY = self.API_KEY
		r = requests.get(('https://cardano-mainnet.blockfrost.io/api/v0/assets/'+asset+'/addresses'), headers={'project_id': API_KEY})
		return json.loads(r.text)

	# https://cardano-mainnet.blockfrost.io/api/v0/addresses/{address}
	def get_stake_address_from_address(self, address):
		API_KEY = self.API_KEY
		r = requests.get(('https://cardano-mainnet.blockfrost.io/api/v0/addresses/'+address), headers={'project_id': API_KEY})
		try:
			stake1 = json.loads(r.text)['stake_address']
		except:
			stake1 = None
		return stake1 

	def get_asset_ownership_dict(self, asset_ids_list):
		API_KEY = self.API_KEY
		ownership_dict = {}
		for asset_id in asset_ids_list:
			addr_info_list = []
			addr1 = self.get_info_on_addresses_by_asset(asset_id)[0]['address']
			stake1 = self.get_stake_address_from_address(addr1)
			if stake1 == None:
				stake1 = addr1
			addr_info_list.append(addr1)
			addr_info_list.append(stake1)
			ownership_dict[asset_id] = addr_info_list
		return ownership_dict

	def get_holders_dict(self, asset_ids_list):
		total_pages = math.ceil(len(asset_ids_list)/100)
		ownership_dict = {}
		for i in range(1, total_pages+1):
			attempts = 0
			if i == total_pages:
				lower = (i-1) * 100
				upper = len(asset_ids_list)
			else:
				lower = (i-1) * 100
				upper = i*100
			successful = False

			while not successful and attempts <= 5:
				try:
					print(f'Collecting data on holders of assets in the range {lower} - {upper}')
					temp_dict = self.get_asset_ownership_dict(asset_ids_list[lower:upper])
					ownership_dict.update(temp_dict)
					successful = True
				except:
					attempts += 1
					print(f'Something went wrong when tried to get info on owners for assets in range {lower} - {upper}')
					if attempts <= 5:
						print(f'Trying again...\nAttempt {attempts}')
					successful = False
		return ownership_dict
