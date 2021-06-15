import logging
from facebook_scraper import get_posts
from creds import fb_username, fb_password


def harvest_emails_fb_group_posts(group_id, pages_to_harvest, search_keys):
    rec_email_dict = {}
    for post in get_posts('232940231122621', pages=10, credentials=(fb_username, fb_password)):
        for word in (post['text']).split():
            word_pro = [word.upper(), word.lower()] + word.split(',./[]?\`~!@#$%^&*()_+=-><";:')
            if '@' in word:
                email = word
                try:
                    rec_email_dict[email] += 1
                except KeyError as e:
                    rec_email_dict[email] = 0
            for search_word in search_keys:
                if search_word in word_pro:
                    try:
                        rec_email_dict[email] += 1
                    except KeyError or NameError as e:
                        logging.info("search word {} is in post: {}, but there is no Email".format(search_word, post['post_id']))
            email = None
    return rec_email_dict


def sort_list_by_dict_counter(dict_to_sort):
    sorted_list_by_value = sorted(dict_to_sort.items(), key=lambda item: item[1])
    return sorted_list_by_value