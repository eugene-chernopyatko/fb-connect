import csv
import sqlite3

import paramiko
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
import os
from dotenv import load_dotenv

load_dotenv()

USER= os.getenv('pa_user')
PASSWORD = os.getenv('pa_password')

conn = sqlite3.connect('/home/neyokee/fb-connect/db.sqlite3')
cursor = conn.cursor()

user_id_cursor = cursor.execute('SELECT id,fb_app_id,fb_account_secret,fb_access_token FROM authentication_customuser')
user_id_list = user_id_cursor.fetchall()

for data in user_id_list:
    user_a_id = data[1]
    user_a_sec = data[2]
    user_a_token = data[3]

    FacebookAdsApi.init(user_a_id, user_a_sec, user_a_token)

    project_cursor = cursor.execute(f'SELECT account_id,filename_to_transfer FROM datatransfer_project WHERE user_id = {data[0]}')
    project_data_list = project_cursor.fetchall()
    for proj in project_data_list:
        print(proj)
        account = AdAccount(proj[0])
        insights = account.get_insights(fields=[
            # AdsInsights.Field.campaign_id,
            AdsInsights.Field.campaign_name,
            AdsInsights.Field.adset_id,
            AdsInsights.Field.adset_name,
            AdsInsights.Field.spend,
            AdsInsights.Field.impressions,
            AdsInsights.Field.clicks,
        ], params={
            'level': 'adset',
            'time_increment': 1,
            'date_preset': 'yesterday',
        })
        campaign_data = []

        for i in insights:
            campaign_data.append(
                {
                    'campaign_id_column': i['adset_id'],
                    'campaign_name': i['adset_name'],
                    'campaign_source_column': 'facebook',
                    'campaign_medium_column': i['campaign_name'],
                    'date_column': i['date_stop'],
                    'daily_impressions_column': i['impressions'],
                    'daily_clicks_column': i['clicks'],
                    'daily_cost_column': float(i['spend'])*proj.exchange_rate
                }
            )
        try:
            keys = campaign_data[0].keys()
        except IndexError:
            print('List is empty')
        finally:
            keys = ['campaign_id_column', 'campaign_name', 'campaign_source_column',
                    'campaign_medium_column', 'date_column', 'daily_impressions_column',
                    'daily_clicks_column', 'daily_cost_column']
            with open(f'/home/neyokee/fb-connect/trash_files/{proj[1]}', mode='w+', newline='') as file:
                dict_writer = csv.DictWriter(file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(campaign_data)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname='ssh.pythonanywhere.com', username=USER, password=PASSWORD)
        sftp = ssh.open_sftp()
        sftp.put(f'/home/neyokee/fb-connect/trash_files/{proj[1]}', f'/home/neyokee/fb_cost_data/{proj[1]}')
        sftp.close()
        ssh.close()

# b = cursor.execute('SELECT project_name FROM datatransfer_project WHERE user_id = 1')
# pro = b.fetchall()
# for i in rows:
#     print(i)
#
# print(pro)