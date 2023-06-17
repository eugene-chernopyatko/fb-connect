import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Project
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.user import User
from facebook_business.exceptions import FacebookRequestError
import csv
import paramiko
from .forms import CreateProjectForm, ProjectOpenKeyForm
from authentication.models import CustomUser
import os
from dotenv import load_dotenv
import requests

load_dotenv()

USER= os.getenv('pa_user')
PASSWORD = os.getenv('pa_password')

CURRENCY = ['uah', 'usd', 'eur', 'gbp']


def projects_main(request):
    if not request.user.is_authenticated:
        return redirect('projects')
    if request.user.is_authenticated:
        projects = Project.objects.filter(user=request.user.pk)
        return render(request, 'projects_page.html', {'projects': projects})


def get_project(request, pk):
    if request.method == 'POST':
        form = ProjectOpenKeyForm(request.POST)
        if form.is_valid():
            project = Project.objects.get(pk=pk)
            project.ssh_key = request.POST['ssh_key']
            project.save()
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname='ssh.pythonanywhere.com', username=USER, password=PASSWORD)
            sftp = ssh.open_sftp()
            remote_file_path = '/home/neyokee/.ssh/authorized_keys'
            with sftp.open(remote_file_path) as file:
                file_content = file.read()

            new_file_content = file_content.decode() + f'\n{request.POST["ssh_key"]}'

            with sftp.open(remote_file_path, 'w') as file:
                file.write(new_file_content.encode())

            sftp.close()
            ssh.close()
            return redirect('projects')
        else:
            project = Project.objects.get(pk=pk)
            return render(request, 'project_detail.html', {'project': project, 'form': form})

    else:
        project = Project.objects.get(pk=pk)
        form = ProjectOpenKeyForm(initial={'ssh_key': project.ssh_key})
        return render(request, 'project_detail.html', {'project': project, 'form': form})


def get_account_list(request):
    if request.user.is_authenticated:
        user_a_id = request.user.fb_app_id
        user_a_sec = request.user.fb_account_secret
        user_a_token = request.user.fb_access_token

        FacebookAdsApi.init(user_a_id, user_a_sec, user_a_token)

        me = User(fbid='me')
        ad_accounts = me.get_ad_accounts(fields=['name', 'account_id'])

        return render(request, 'index.html', {'accounts': ad_accounts})


def create_project(request):
    if not request.user.is_authenticated:
        return redirect('projects')
    if request.method == 'POST':
        account_id = request.POST['dropdown']
        form = CreateProjectForm(request.POST)
        ad_currency = request.POST['dropdown-ad-currency']
        ga_currency = request.POST['dropdown-ga-currency']
        if form.is_valid():
            project_name = request.POST['project_name']
            proj = form.save(commit=False)
            proj.account_id = f'act_{account_id}'
            proj.user = CustomUser.objects.get(pk=request.user.pk)
            proj.filename_to_transfer = f'{project_name}_cost_data.csv'
            proj.ad_account_currency = ad_currency
            proj.ga4_currency = ga_currency
            currency_response = requests.get(f'https://cdn.jsdelivr.net/gh/fawazahmed0/'
                                             f'currency-api@1/latest/currencies/{ad_currency}/{ga_currency}.json')
            proj.exchange_rate = currency_response.json()[f'{ga_currency}']
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname='ssh.pythonanywhere.com', username=USER, password=PASSWORD)
            sftp = ssh.open_sftp()
            sftp.chdir('/home/neyokee/fb_cost_data/')
            with sftp.open(f'{project_name}_cost_data.csv', 'w') as remote_file:
                pass

            sftp.close()
            ssh.close()
            proj.save()
            return redirect('projects')
        else:
            user_a_id = request.user.fb_app_id
            user_a_sec = request.user.fb_account_secret
            user_a_token = request.user.fb_access_token

            FacebookAdsApi.init(user_a_id, user_a_sec, user_a_token)

            me = User(fbid='me')
            ad_accounts = me.get_ad_accounts(fields=['name', 'account_id'])
            return render(request, 'create_project.html', {'form': form, 'accounts': ad_accounts, 'currency': CURRENCY})
    else:
        form = CreateProjectForm()
        try:
            user_a_id = request.user.fb_app_id
            user_a_sec = request.user.fb_account_secret
            user_a_token = request.user.fb_access_token

            FacebookAdsApi.init(user_a_id, user_a_sec, user_a_token)

            me = User(fbid='me')
            ad_accounts = me.get_ad_accounts(fields=['name', 'account_id'])
        except FacebookRequestError:
            ad_accounts = []
            form.errors('You have to change access token to see ad accounts')
            print('#################################')
        finally:
            # form = CreateProjectForm()
            return render(request, 'create_project.html', {'form': form, 'accounts': ad_accounts, 'currency': CURRENCY})


def delete_project(request, pk):
    proj = Project.objects.get(pk=pk)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='ssh.pythonanywhere.com', username=USER, password=PASSWORD)
    sftp = ssh.open_sftp()
    remote_file_path = '/home/neyokee/.ssh/authorized_keys'
    if proj.ssh_key:
        with sftp.open(remote_file_path) as file:
            file_content = file.read()
            ssh_list = file_content.decode().split('\n')

        new_ssh = [key for key in ssh_list if key != proj.ssh_key]
        with sftp.open(remote_file_path, 'w') as file:
            file.write('\n'.join(new_ssh).encode())

    sftp.remove(f'/home/neyokee/fb_cost_data/{proj.filename_to_transfer}')
    sftp.close()
    proj.delete()
    return redirect('projects')


def go(request):
    if request.user.is_authenticated:
        user_a_id = request.user.fb_app_id
        user_a_sec = request.user.fb_account_secret
        user_a_token = request.user.fb_access_token

        FacebookAdsApi.init(user_a_id, user_a_sec, user_a_token)

        project = Project.objects.get(pk=13)

        account = AdAccount(project.account_id)
        insights = account.get_insights(fields=[
            # AdsInsights.Field.campaign_id,
            # AdsInsights.Field.campaign_name,
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
                    'campaign_medium_column': 'cpa',
                    'date_column': i['date_stop'],
                    'daily_impressions_column': i['impressions'],
                    'daily_clicks_column': i['clicks'],
                    'daily_cost_column': i['spend']
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
            with open(f'trash/{project.filename_to_transfer}', mode='w+', newline='') as file:
                dict_writer = csv.DictWriter(file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(campaign_data)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname='ssh.pythonanywhere.com', username=USER, password=PASSWORD)
        sftp = ssh.open_sftp()
        sftp.put(f'trash/{project.filename_to_transfer}', '/home/neyokee/fb_cost_data/Brander_cost_data.csv')
        sftp.close()
        ssh.close()
        return HttpResponse('OK')