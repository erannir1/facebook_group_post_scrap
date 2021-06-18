import logging
import smtplib
import pickle
from creds import gmail_username, gmail_password
from fb_group_post_scarp import post_dict, emails_and_grades
from facebook_group_post_scrapper import harvest_emails_fb_group_posts, get_mail_list_from_dict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from parameters import sent_email_addresses_path, search_words, group_id, mail_subject, mail_attach, mail_content_path,\
    number_of_page_to_harvest


def send_resume_to_rec(emails_list, mail_grade, mail_subject_line, email_content, attachment):
    sent_email_addresses = []
    # The mail addresses and password
    for receiver in emails_list:
        if receiver[2] >= mail_grade and receiver[1] not in sent_email_addresses:
            # Setup the MIME
            message = MIMEMultipart()
            message['From'] = "Eran Nir <{}>".format(gmail_username)
            message['To'] = receiver[1]
            message['Subject'] = mail_subject_line  # The subject line
            # The body and the attachments for the mail
            message.attach(MIMEText(email_content, 'plain'))
            payload = MIMEBase('application', "octet-stream")
            with open(attachment, 'rb') as attach_file:  # Open the file as binary mode
                payload.set_payload(attach_file.read())
            encoders.encode_base64(payload)  # encode the attachment
            # add payload header with filename
            attach_name = attachment.split('\\')[-1]
            payload.add_header('content-disposition', 'attachment', filename=attach_name)
            message.attach(payload)
            # Create SMTP session for sending the mail
            session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
            session.starttls()  # enable security
            session.login(gmail_username, gmail_password)  # login with mail_id and password
            text = message.as_string()
            session.sendmail(gmail_username, receiver[1], text)
            session.quit()
            logging.info('Mail sent to: %s', receiver[1])
            sent_email_addresses.append(receiver)
        else:
            logging.info("Did not send mail to {} due to low grade.".format(receiver))
    return sent_email_addresses


def upload_list_pickle(list_to_upload, path, upload=False):
    if upload:
        with open(path, "wb") as seap:  # Pickling
            pickle.dump(list_to_upload, seap)


if __name__ == "__main__":
    emails_dict = harvest_emails_fb_group_posts(group_id=group_id, pages_to_harvest=number_of_page_to_harvest,
                                                search_keys=search_words)
    sorted_emails_tup_list = get_mail_list_from_dict(emails_dict)
    grade = len(search_words) * 0.4
    mail_content = open(mail_content_path).read()
    sent_email_addresses_list = send_resume_to_rec(sorted_emails_tup_list,
                                                   grade, mail_subject, mail_content, mail_attach)
    upload_list_pickle(list_to_upload=sent_email_addresses_list, path=sent_email_addresses_path, upload=False)
