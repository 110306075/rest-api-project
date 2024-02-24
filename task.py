import os
import requests
from dotenv import load_dotenv
import jinja2
load_dotenv()
domain = os.getenv("MAILGUN_DOMAIN")
template_laoder = jinja2.FileSystemLoader("template")
template_env = jinja2.Environment(loader = template_laoder)




def render_template(template_filename, **context):
    return template_env.get_template(template_filename).render(**context)

def send_simple_message(to,subject,body,html):

    return requests.post(
		f"https://api.mailgun.net/v3/{domain}/messages",
		auth=("api", os.getenv("MAILGUN_API_KEY")),
		data={"from": "David <mailgun@{domain}>",
			"to": [to],
			"subject": subject,
			"text": body,
            "html":html,},
            )


def send_user_registration_email(email,username):
    return send_simple_message(
        email,
        "Successfully signed up",
        f"Hi{username} You have just successfully signed up",
        render_template("email/action.html")
    )