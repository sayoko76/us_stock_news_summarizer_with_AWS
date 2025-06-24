from flask import Flask
import boto3
import datetime
from news_crawl import news

application = Flask(__name__)

@application.route('/')
def index():
    return 'application test 1.0'

@application.route('/upload_s3')
def upload_s3():    
    
    try:
        # upload to s3
        content = f'hello, time: {datetime.datetime.now()}'
        file_name = f'hello_time_{datetime.date.today().isoformat()}.txt'
        # file_name = f'hello_time_{datetime.datetime.now().isoformat()}.txt'
        bucket_name = 'news-crawl-sayoko76' 
        
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=content.encode('utf-8'))
        return f'hello world_{content}', 200
    except Exception as e:
        return f'error upload to s3: {e}', 500
        
    
@application.route('/news')
def news_crawl():    
    summary = news(news_website='cnyes', news=5)
    
    try:
        file_name = f'US_stocks_news_{datetime.date.today().isoformat()}.txt'
        bucket_name = <bucket name>
        
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=summary.encode('utf-8'))
        return f'Upload to s3 success!\nSummary: \n\n {summary}', 200
    except Exception as e:
        return f'error upload to s3: {e}', 500
    
    

@application.route('/health') 
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    application.run(port=8000, debug=True) 