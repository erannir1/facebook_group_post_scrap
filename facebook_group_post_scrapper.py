import logging
import pickle
from facebook_scraper import get_posts
from creds import fb_username, fb_password
from parameters import sent_email_addresses_path


def harvest_emails_fb_group_posts(group_id, pages_to_harvest, search_keys):
    try:
        with open(sent_email_addresses_path, "rb") as seap:   # Unpickling
            sent_email_addresses = pickle.load(seap)
    except FileNotFoundError as e:
        sent_email_addresses = []
    rec_email_dict = {}
    rec_email_counter = {}
    list_of_chars_to_replace = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')',
                                '>', '#', '+', ',', '-', '!', '$', '\'']
    for post in get_posts(group_id, pages=pages_to_harvest, credentials=(fb_username, fb_password)):
        serach_keys_copy = search_keys
        post_text = replace_multiple_ch(post['text'], list_of_chars_to_replace)
        rec_email_dict[post['post_id']] = [None, 0]
        for word in post_text.split():
            word_pro = [word.upper(), word.lower()]
            if '@' in word and word not in sent_email_addresses:
                email = word
                try:
                    rec_email_counter[email] += 1
                except KeyError as e:
                    rec_email_counter[email] = 0
                    rec_email_dict[post['post_id']][0] = email
            for search_word in serach_keys_copy:
                if search_word in word_pro:
                    try:
                        rec_email_dict[post['post_id']][1] += 1
                        serach_keys_copy.remove(search_word)
                    except KeyError or NameError as e:
                        logging.info("search word {} is in post: {}, but there is no Email".format(search_word, post['post_id']))
    return rec_email_dict


def get_mail_list_from_dict(email_dict):
    emails = list(email_dict.items())
    email_list = [(value[1][0], value[1][1]) for value in emails if value[1][0] is not None]
    return email_list


def replace_multiple_ch(text, chars_to_replace_list):
    for ch in chars_to_replace_list:
        if ch in text:
            text = text.replace(ch, " ")
    return text