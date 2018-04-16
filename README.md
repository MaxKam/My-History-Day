#My History Day

This app shows you events that happened on this day from your Google calendar.

Built with Python and Flask. 

##Prerequisites
Because we are authenticating users with Google using OAuth2 and accessing the Google Calendar API, you will need to create a project with Google and generate authorization credentials. Steps below explain how to do that. 

Enable APIs for your project
Any application that calls Google APIs needs to enable those APIs in the API Console. To enable the appropriate APIs for your project:

1. Open the Library page in the Google API Console.
2. Select the project associated with your application. Create a project if you do not have one already.
3. Use the Library page to find each API, in this case the **Calendar API** that your application will use. Click on each API and enable it for your project.

Create authorization credentials
Any application that uses OAuth 2.0 to access Google APIs must have authorization credentials that identify the application to Google's OAuth 2.0 server. The following steps explain how to create credentials for your project. Your applications can then use the credentials to access APIs that you have enabled for that project.

1. Open the Credentials page in the API Console.
2. Click Create credentials > OAuth client ID.
3. Complete the form. Set the application type to Web application. Applications that use languages and frameworks like PHP, Java, Python, Ruby, and .NET must specify authorized redirect URIs. The redirect URIs are the endpoints to which the OAuth 2.0 server can send responses.

For testing, you can specify URIs that refer to the local machine, such as http://localhost:8080.

After creating your credentials, download the client_secret.json file from the API Console. Securely store the file in a location that only your application can access. **For this app, store the credentials in the config folder under the project folder.**

*Important: Do not store the client_secret.json file in a publicly-accessible location. In addition, if you share the source code to your application—for example, on GitHub—store the client_secret.json file outside of your source tree to avoid inadvertently sharing your client credentials.*

## Installation

**Requires Python 3.5 or greater**

Make sure that you have pip installed and run this command from the project folder: ```pip install -r requirements.txt```


## Setup on webserver
This tutorial does a great job of walking through how to setup Flask with Nginx on a webserver. 
[Flask with Nginx](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04)

It's highly recommended to setup Nginx with a SSL cert and use HTTPS only for the website. This is a tutorial on how to do that using Let's Encrypt, a certificate authority that provides free certs.
[Nginx and Let's Encrypt](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04)

## Contributing
Feel free to contribute any fixes or features. 