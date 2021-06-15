import logging
import smtplib
import pickle
from creds import gmail_username, gmail_password
from facebook_group_post_scrapper import harvest_emails_fb_group_posts, sort_list_by_dict_counter
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from parameters import sent_email_addresses_path, search_words, group_id, mail_subject, mail_attach, mail_content_path,\
    number_of_page_to_harvest


def send_resume_to_rec(emails_list, mail_grade, mail_subject_line, email_content, attachment):
    sent_email_addresses = []
    # The mail addresses and password
    sender_address = gmail_username
    sender_pass = gmail_password
    for receiver in emails_list:
        if receiver[1] >= mail_grade and receiver[0] not in sent_email_addresses:
            # Setup the MIME
            message = MIMEMultipart()
            message['From'] = "Eran Nir <{}>".format(sender_address)
            message['To'] = receiver[0]
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
            session.login(sender_address, sender_pass)  # login with mail_id and password
            text = message.as_string()
            session.sendmail(sender_address, receiver[0], text)
            session.quit()
            logging.info('Mail sent to: %s', receiver[0])
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
    sorted_emails_tup_list = sort_list_by_dict_counter(emails_dict)
    grade = len(search_words)
    mail_content = open(mail_content_path).read()
    sent_email_addresses_list = send_resume_to_rec(sorted_emails_tup_list,
                                                   grade, mail_subject, mail_content, mail_attach)
    upload_list_pickle(list_to_upload=sent_email_addresses_list, path=sent_email_addresses_path, upload=False)
