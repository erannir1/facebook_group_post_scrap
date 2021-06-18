import logging
import pickle
from facebook_scraper import get_posts
from creds import fb_username, fb_password
from parameters import sent_email_addresses_path, list_of_chars_to_replace, group_id, number_of_page_to_harvest, search_words


def get_post_info(group_id, pages_to_harvest, list_of_chars_to_replace):
    post_dict = {}
    for post in get_posts(group_id, pages=pages_to_harvest, credentials=(fb_username, fb_password)):
        post['email'] = None
        post['grade'] = 0
        post['post_replaced_text'] = replace_multiple_ch(post['text'], list_of_chars_to_replace)
        post_dict[post['post_id']] = post
    return post_dict


def get_rec_email(post_dict):
    try:
        with open(sent_email_addresses_path, "rb") as seap:   # Unpickling
            sent_email_addresses = pickle.load(seap)
    except FileNotFoundError as fnfe:
        sent_email_addresses = []
    for post_id in post_dict:
        for word in post_dict[post_id]['post_replaced_text'].split():
            if '@' in word and word not in sent_email_addresses:
                post_dict[post_id]['email'] = word
    return post_dict


def grade_post(post_dict, search_keys):
    for post_id in post_dict:
        search_keys_copy = search_keys
        for word in post_dict[post_id]['post_replaced_text'].split():
            word_pro = [word.upper(), word.lower()]
            for search_word in search_keys_copy:
                if search_word in word_pro:
                    post_dict[post_id]['grade'] += 1
                    search_keys_copy.remove(search_word)
    return post_dict


def get_emails_and_grades(post_dict, sort=False):
    emails_list = []
    for post_id in post_dict:
        if post_dict[post_id]["email"] is not None:
            emails_list.append((post_id, post_dict[post_id]["email"], post_dict[post_id]["grade"]))
    if sort:
        emails_list.sort(key=lambda tup: tup[2], reverse=True)
    return emails_list


def get_emails_above_grade(emails_list, min_grade, is_list_sorted=False):
    emails_above_grade = []
    for email in emails_list:
        if is_list_sorted:
            if email[2] < min_grade:
                break
        if email[2] >= min_grade:
            emails_above_grade.append(email)
    return emails_above_grade


def replace_multiple_ch(text, chars_to_replace_list):
    for ch in chars_to_replace_list:
        if ch in text:
            text = text.replace(ch, " ")
    return text


if __name__ == "__main__":
    post_dict = get_post_info(group_id=group_id,
                              pages_to_harvest=number_of_page_to_harvest,
                              list_of_chars_to_replace=list_of_chars_to_replace)
    post_dict = get_rec_email(post_dict)
    post_dict = grade_post(post_dict, search_keys=search_words)
    emails_and_grades = get_emails_and_grades(post_dict, sort=True)
print(1)
