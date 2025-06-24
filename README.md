### U.S. Stock News Summarizer with AWS
This project is a Flask web application deployed on AWS Elastic Beanstalk.
Crawl U.S. stock news from selected news websites, using the OpenAI API to analyze a summary of the U.S. stock market performance for the most recent trading day from the scraped data.
Include three parts:
  * S&P 500 index performance data and percentage change for yesterday
  * The strongest and weakest industry sectors (at least two each)
  * Significant movements (significant rise or fall or major announcements) of 3-5 important individual stocks

## Project Structure
* ```application``` - Main Flask web application
* ```news_crawl``` - News crawler and summarizer
* ```requirements``` - Python dependencies
* ```.ebextensions/``` - AWS Elastic Beanstalk enviroment config
* ```.ebextensions/app.config``` - Apache mod_wsgi config
* ```.ebextensions/chrome.config``` - Installs Chrome dependencies

## Technologies Used
* Python
* Flask
* Selenium + ChromeDriver
* OpenAI API
* AWS Elastic Beanstalk

## Get Started
1. Clone the repository
```
git clone <repo-url>
```
2. Install dependencies
```
pip install -r requirements.txt
```
3. Set Variables before running
* Set your OpenAI API key in ```news_crawl.py```
 ```
 OpenAI(api_key = <api_key>)
 ```
* Set your s3 bucket in ```application.py```
 ```
 bucket_name = <your becket name>
 ```
4. Local testing
```
python application.py
```
The application will be avaliable at ```http://127.0.0.1:8000/``` (Elastic Beastalk listening port 8000)
5. Deployed to AWS Elastic Beanstalk
* Zip the entire folder (including ```.ebextensions/```)
* Create an Elastic Beanstalk web server environment
* Upload your zip file
Elastic Beanstalk will deploy the application and save the summary to your bucket
