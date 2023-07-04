import random
from django.shortcuts import render, redirect
from .models import Project, UploadHistory
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.user import User
from facebook_business.exceptions import FacebookRequestError
import paramiko
from .forms import CreateProjectForm, ProjectOpenKeyForm
from authentication.models import CustomUser
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

load_dotenv()

USER= os.getenv('pa_user')
PASSWORD = os.getenv('pa_password')

CURRENCY = ['uah', 'usd', 'eur', 'gbp']
UPLOAD_TIME = 12
ACCOUNT_LIMIT = {
    'Start': 1,
    'Standard': 5,
    'Standard+': 10,
    'Unlimited': 1000
}


def projects_main(request):
    if not request.user.is_authenticated:
        return redirect('projects')
    if int(request.user.project_count) >= ACCOUNT_LIMIT[request.user.billing_plan]:
        projects = Project.objects.filter(user=request.user.pk)
        upload_history = UploadHistory.objects.order_by('-upload_date')
        return render(request, 'projects_page.html', {'projects': projects,
                                                      'history': upload_history, 'block_creating': 1})
    if request.user.is_authenticated:
        projects = Project.objects.filter(user=request.user.pk)
        upload_history = UploadHistory.objects.order_by('-upload_date')
        return render(request, 'projects_page.html', {'projects': projects, 'history': upload_history})


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
                ssh_list = file_content.decode().split('\n')

            if request.POST["ssh_key"] not in ssh_list:
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
        upload_history = UploadHistory.objects.filter(project=pk).order_by('-upload_date')
        project = Project.objects.get(pk=pk)
        form = ProjectOpenKeyForm(initial={'ssh_key': project.ssh_key})
        return render(request, 'project_detail.html', {'project': project, 'form': form, 'history': upload_history})


# def get_account_list(request):
#     if request.user.is_authenticated:
#         user_a_id = request.user.fb_app_id
#         user_a_sec = request.user.fb_account_secret
#         user_a_token = request.user.fb_access_token
#
#         FacebookAdsApi.init(user_a_id, user_a_sec, user_a_token)
#
#         me = User(fbid='me')
#         ad_accounts = me.get_ad_accounts(fields=['name', 'account_id'])
#
#         return render(request, 'index.html', {'accounts': ad_accounts})


def create_project(request):
    if not request.user.is_authenticated:
        return redirect('projects')
    if int(request.user.project_count) >= ACCOUNT_LIMIT[request.user.billing_plan]:
        return redirect('projects')
    if request.method == 'POST':
        account_id = request.POST['dropdown']
        form = CreateProjectForm(request.POST)
        ad_currency = request.POST['dropdown-ad-currency']
        ga_currency = request.POST['dropdown-ga-currency']
        start_date = request.POST['date']
        # print(start_date)
        if form.is_valid():
            project_name = request.POST['project_name']
            exists = Project.objects.filter(project_name=project_name).exists()
            if exists:
                project_name = project_name + str(random.randint(1, 1000))
            proj = form.save(commit=False)
            proj.account_id = f'act_{account_id}'
            proj.user = CustomUser.objects.get(pk=request.user.pk)
            proj.filename_to_transfer = f'{project_name}_cost_data.csv'
            proj.ad_account_currency = ad_currency
            proj.ga4_currency = ga_currency
            currency_response = requests.get(f'https://cdn.jsdelivr.net/gh/fawazahmed0/'
                                             f'currency-api@1/latest/currencies/{ad_currency}/{ga_currency}.json')
            proj.exchange_rate = currency_response.json()[f'{ga_currency}']

            user_a_id = request.user.fb_app_id
            user_a_sec = request.user.fb_account_secret
            user_a_token = request.user.fb_access_token

            FacebookAdsApi.init(user_a_id, user_a_sec, user_a_token)

            today = datetime.now()
            two_day_ago = today - timedelta(days=2)
            yesterday = today - timedelta(days=1)
            current_time = datetime.now()
            hour = current_time.hour

            account = AdAccount(f'act_{account_id}')
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
                'time_range': {
                    'since':  f'{start_date}',
                    'until': two_day_ago.strftime('%Y-%m-%d') if hour < UPLOAD_TIME else yesterday.strftime('%Y-%m-%d')
                },
            })
            campaign_data = []
            for i in insights:
                campaign_data.append([i['adset_id'], i['adset_name'], 'facebook', i['campaign_name'], i['date_stop'],
                                      i['impressions'], i['clicks'],
                                      format(float(i['spend']) * currency_response.json()[f'{ga_currency}'], '.2f')])

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname='ssh.pythonanywhere.com', username=USER, password=PASSWORD)
            sftp = ssh.open_sftp()
            sftp.chdir('/home/neyokee/fb_cost_data/')
            keys = ['campaign_id_column', 'campaign_name', 'campaign_source_column',
                    'campaign_medium_column', 'date_column', 'daily_impressions_column',
                    'daily_clicks_column', 'daily_cost_column']
            with sftp.open(f'{project_name}_cost_data.csv', 'w') as remote_file:
                remote_file.write(','.join(keys).encode())

            with sftp.open(f'{project_name}_cost_data.csv', 'a') as remote_file:
                for i in campaign_data:
                    remote_file.write(f'\n{",".join(i)}')
            proj.upload_status = 'Success'
            request.user.project_count = request.user.project_count + 1
            request.user.save()
            sftp.close()
            ssh.close()
            proj.save()
            upload_history = UploadHistory(upload_date=f'{today.strftime("%Y-%m-%d")}', upload_status='Success',
                                           status_description='No problems detected',
                                           project=Project.objects.get(id=proj.id))
            upload_history.save()
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
            print(f'Current hour now: {datetime.now().hour}')
            return render(request, 'create_project.html', {'form': form, 'accounts': ad_accounts, 'currency': CURRENCY})


def delete_project(request, pk):
    proj = Project.objects.get(pk=pk)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='ssh.pythonanywhere.com', username=USER, password=PASSWORD)
    sftp = ssh.open_sftp()
    remote_file_path = '/home/neyokee/.ssh/authorized_keys'
    # if proj.ssh_key:
    #     with sftp.open(remote_file_path) as file:
    #         file_content = file.read()
    #         ssh_list = file_content.decode().split('\n')
    #
    #     new_ssh = [key for key in ssh_list if key != proj.ssh_key]
    #     with sftp.open(remote_file_path, 'w') as file:
    #         file.write('\n'.join(new_ssh).encode())

    sftp.remove(f'/home/neyokee/fb_cost_data/{proj.filename_to_transfer}')
    sftp.close()
    proj.delete()
    request.user.project_count = request.user.project_count - 1
    request.user.save()
    return redirect('projects')
