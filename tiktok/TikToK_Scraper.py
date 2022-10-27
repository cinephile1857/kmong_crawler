import os
import sys
import random
import pandas as pd
from playwright.sync_api import sync_playwright
import time
import System


class Scraper:

    def __init__(self):
        self.path = os.getcwd()
        self.proxy = ""

    def set_path(self, path):
        self.path = path

    def get_path(self):
        return self.path

    def set_proxy(self):
        ip = input("ip: ")
        port = input("port: ")
        self.proxy = "http://" + ip + ":" + port

    def get_proxy(self):
        return self.proxy

    @staticmethod
    def user_list(directory):
        pid = os.getpid()
        print("====#%d user list create====" % pid)
        result_c_path = directory + "\\result_c.csv"
        result_r_path = directory + "\\result_r.csv"
        temporary_save_path = directory + "\\user_list_not_duplicate.csv"
        save_path = directory + "\\user_list.csv"
        System.delete_file(save_path)
        for cnt, chunk in enumerate(pd.read_csv(result_c_path, chunksize=1)):
            id = "@" + str(chunk['sec_uid'].values[0])
            url = "https://www.tiktok.com/" + id
            user_unique_id = str(chunk['user_unique_id'].values[0])
            user_nickname = str(chunk['user_nickname'].values[0])
            data = [{'user_unique_id': user_unique_id,
                     'user_nickname': user_nickname,
                     'url': url}]
            System.overwrite_csv(pd.DataFrame(data), temporary_save_path)
        for cnt, chunk in enumerate(pd.read_csv(result_r_path, chunksize=1)):
            id = "@" + str(chunk['sec_uid'].values[0])
            url = "https://www.tiktok.com/" + id
            user_unique_id = str(chunk['user_unique_id'].values[0])
            user_nickname = str(chunk['user_nickname'].values[0])
            data = [{'user_unique_id': user_unique_id,
                     'user_nickname': user_nickname,
                     'url': url}]
            System.overwrite_csv(pd.DataFrame(data), temporary_save_path)
        for cnt, chunk in enumerate(pd.read_csv(temporary_save_path, chunksize=1000)):
            chunk = chunk.drop_duplicates()
            System.overwrite_csv(pd.DataFrame(chunk), save_path)
        System.delete_file(temporary_save_path)

    def user_info_single(self, directory):
        pid = os.getpid()
        print("====#%d user info scraping====" % pid)
        user_list_path = directory
        save_path = directory[:-4] + "_info.csv"
        except_path = directory[:-4] + "_exception.csv"
        count = 0
        count_max = 0
        for cnt, chunk in enumerate(pd.read_csv(user_list_path, chunksize=1)):
            count_max = cnt
        count_max += 1
        if not os.path.exists(save_path):
            with sync_playwright() as playwright:
                chromium = playwright.chromium
                if len(str(self.proxy)) == 0:
                    browser = chromium.launch(headless=False)
                else:
                    browser = chromium.launch(headless=False, proxy={"server": self.proxy})
                page = browser.new_page()
                for cnt, chunk in enumerate(pd.read_csv(user_list_path, chunksize=1)):
                    time.sleep(random.randrange(2, 5))
                    url = chunk['url'].values[0]
                    try:
                        with page.expect_response(
                                lambda response: "/api/user/detail" in response.url and response.status == 200) as api_user_detail:
                            page.goto(url)
                        result = api_user_detail.value.json()
                        chunk = chunk.drop('user_unique_id', axis=1)
                        chunk = chunk.drop('user_nickname', axis=1)
                        chunk = chunk.drop('url', axis=1)
                        chunk['user_id'] = result['userInfo']['user']['uniqueId']
                        chunk['follower_count'] = "'" + str(result['userInfo']['stats']['followerCount'])
                        chunk['following_count'] = "'" + str(result['userInfo']['stats']['followingCount'])
                        chunk['heart_count'] = "'" + str(result['userInfo']['stats']['heartCount'])
                        chunk['video_count'] = "'" + str(result['userInfo']['stats']['videoCount'])
                        System.overwrite_csv(chunk, save_path)
                    except Exception:
                        body = page.locator('body')
                        if "이 페이지 안내:" in body.all_text_contents()[0] or "About this page:" in body.all_text_contents()[0] or len(body.all_text_contents()[0]) == 0:
                            print("Captcha is on")
                            print(url)
                            sys.exit(0)
                        else:
                            print("except_path_add")
                            System.overwrite_csv(chunk, except_path)
                    print("#" + str(pid) + ": " + str(count) + "/" + str(count_max))
                    count += 1
        else:
            skip_row = 0
            except_add = 0
            for cnt, chunk in enumerate(pd.read_csv(save_path, chunksize=1)):
                skip_row = cnt+2
            if os.path.exists(except_path):
                for cnt, chunk in enumerate(pd.read_csv(except_path, chunksize=1)):
                    except_add = cnt + 1
            skip_row += except_add

            with sync_playwright() as playwright:
                chromium = playwright.chromium
                if len(str(self.proxy)) == 0:
                    browser = chromium.launch(headless=False)
                else:
                    browser = chromium.launch(headless=False, proxy={"server": self.proxy})
                page = browser.new_page()
                for cnt, chunk in enumerate(pd.read_csv(user_list_path, names=['url'], skiprows=skip_row, chunksize=1)):
                    try:
                        time.sleep(random.randrange(2, 5))
                        url = chunk['url'].values[0]
                        try:
                            with page.expect_response(
                                    lambda response: "/api/user/detail" in response.url and response.status == 200) as api_user_detail:
                                page.goto(url)
                            result = api_user_detail.value.json()
                            chunk = chunk.drop('url', axis=1)
                            chunk['user_id'] = result['userInfo']['user']['uniqueId']
                            chunk['follower_count'] = "'" + str(result['userInfo']['stats']['followerCount'])
                            chunk['following_count'] = "'" + str(result['userInfo']['stats']['followingCount'])
                            chunk['heart_count'] = "'" + str(result['userInfo']['stats']['heartCount'])
                            chunk['video_count'] = "'" + str(result['userInfo']['stats']['videoCount'])
                            System.overwrite_csv(chunk, save_path)
                        except Exception:
                            body = page.locator('body')
                            if "이 페이지 안내:" in body.all_text_contents()[0] or "About this page:" in \
                                    body.all_text_contents()[0] or len(body.all_text_contents()[0]) == 0:
                                print("Captcha is on")
                                print(url)
                                sys.exit(0)
                            else:
                                print("except_path_add")
                                System.overwrite_csv(chunk, except_path)
                        print("#" + str(pid) + ": " + str(count) + "/" + str(count_max-skip_row))
                        count += 1
                    except IndexError:
                        print("%d is finish" % pid)
        print("====#%d user info scraping finish====" % pid)

    def user_info_multi(self, directory):
        pid = os.getpid()
        print("====#%d user info scraping====" % pid)
        user_list_path = directory + "\\user_list.csv"
        save_path = directory + "\\user_list_info.csv"
        except_path = directory + "\\user_list_exception.csv"
        count = 0
        count_max = 0
        for cnt, chunk in enumerate(pd.read_csv(user_list_path, chunksize=1)):
            count_max = cnt
        count_max += 1
        if not os.path.exists(save_path):
            with sync_playwright() as playwright:
                chromium = playwright.chromium
                if len(str(self.proxy)) == 0:
                    browser = chromium.launch(headless=False)
                else:
                    browser = chromium.launch(headless=False, proxy={"server": self.proxy})
                page = browser.new_page()
                for cnt, chunk in enumerate(pd.read_csv(user_list_path, chunksize=1)):
                    time.sleep(random.randrange(2, 5))
                    url = chunk['url'].values[0]
                    try:
                        with page.expect_response(
                                lambda response: "/api/user/detail" in response.url and response.status == 200) as api_user_detail:
                            page.goto(url)
                        result = api_user_detail.value.json()
                        chunk = chunk.drop('user_unique_id', axis=1)
                        chunk = chunk.drop('user_nickname', axis=1)
                        chunk = chunk.drop('url', axis=1)
                        chunk['user_id'] = result['userInfo']['user']['uniqueId']
                        chunk['follower_count'] = "'" + str(result['userInfo']['stats']['followerCount'])
                        chunk['following_count'] = "'" + str(result['userInfo']['stats']['followingCount'])
                        chunk['heart_count'] = "'" + str(result['userInfo']['stats']['heartCount'])
                        chunk['video_count'] = "'" + str(result['userInfo']['stats']['videoCount'])
                        System.overwrite_csv(chunk, save_path)
                    except Exception:
                        body = page.locator('body')
                        if "이 페이지 안내:" in body.all_text_contents()[0] or "About this page:" in body.all_text_contents()[0] or len(body.all_text_contents()[0]) == 0:
                            print("Captcha is on")
                            print(url)
                            sys.exit(0)
                        else:
                            print("except_path_add")
                            System.overwrite_csv(chunk, except_path)
                    print("#" + str(pid) + ": " + str(count) + "/" + str(count_max))
                    count += 1
        else:
            skip_row = 0
            except_add = 0
            for cnt, chunk in enumerate(pd.read_csv(save_path, chunksize=1)):
                skip_row = cnt + 2
            if os.path.exists(except_path):
                for cnt, chunk in enumerate(pd.read_csv(except_path, chunksize=1)):
                    except_add = cnt + 1
            skip_row += except_add
            with sync_playwright() as playwright:
                chromium = playwright.chromium
                if len(str(self.proxy)) == 0:
                    browser = chromium.launch(headless=False)
                else:
                    browser = chromium.launch(headless=False, proxy={"server": self.proxy})
                page = browser.new_page()
                for cnt, chunk in enumerate(pd.read_csv(user_list_path, names=['url'], skiprows=skip_row, chunksize=1)):
                    try:
                        time.sleep(random.randrange(2, 5))
                        url = chunk['url'].values[0]
                        try:
                            with page.expect_response(
                                    lambda response: "/api/user/detail" in response.url and response.status == 200) as api_user_detail:
                                page.goto(url)
                            result = api_user_detail.value.json()
                            chunk = chunk.drop('url', axis=1)
                            chunk['user_id'] = result['userInfo']['user']['uniqueId']
                            chunk['follower_count'] = "'" + str(result['userInfo']['stats']['followerCount'])
                            chunk['following_count'] = "'" + str(result['userInfo']['stats']['followingCount'])
                            chunk['heart_count'] = "'" + str(result['userInfo']['stats']['heartCount'])
                            chunk['video_count'] = "'" + str(result['userInfo']['stats']['videoCount'])
                            System.overwrite_csv(chunk, save_path)
                        except Exception:
                            body = page.locator('body')
                            if "이 페이지 안내:" in body.all_text_contents()[0] or "About this page:" in \
                                    body.all_text_contents()[0] or len(body.all_text_contents()[0]) == 0:
                                print("Captcha is on")
                                print(url)
                                sys.exit(0)
                            else:
                                print("except_path_add")
                                System.overwrite_csv(chunk, except_path)
                        print("#" + str(pid) + ": " + str(count) + "/" + str(count_max - skip_row))
                        count += 1
                    except IndexError:
                        print("%d is finish" % pid)
        print("====#%d user info scraping finish====" % pid)

    def comment(self, url):
        pid = os.getpid()
        print("====#%d comment api scraping start====" % pid)
        with sync_playwright() as playwright:
            print("#%d make save directory and set initial value..." % pid)
            if "item_id" not in url:
                item_id = "&item_id=" + url[url.find("video/") + len("video/"):url.find("?")]
                url = url + item_id
                folder_path = self.path+"\\comment\\"+item_id[item_id.find('=')+1:]
            else:
                folder_path = self.path+"\\comment\\" + url[url.find('&item_id=')+len('&item_id=')-1 + 1:]
            System.create_folder(folder_path)
            maximum_delay_time = 5
            pointless_scroll_count = 0
            pointless_scroll_threshold = 30
            api_list = []
            print("#%d launch browser..." % pid)
            chromium = playwright.chromium
            browser = chromium.launch()
            page = browser.new_page()
            page.on("response", lambda response: api_list.append(response))
            page.goto(url)
            before_scroll_height = page.evaluate('(document.body.scrollHeight)')

            print("#%d scrolling and gathering comment api..." % pid)
            count = 0
            while True:
                page.mouse.wheel(0, before_scroll_height)
                if 0 <= count < 50:
                    time.sleep(1)
                elif 50 <= count < 100:
                    time.sleep(2)
                elif 100 <= count < 150:
                    time.sleep(3)
                elif 150 <= count < 200:
                    time.sleep(4)
                else:
                    time.sleep(5)
                new_scroll_height = page.evaluate('(document.body.scrollHeight)')
                if before_scroll_height == new_scroll_height:
                    time.sleep(maximum_delay_time)
                before_scroll_height = new_scroll_height
                pointless_scroll_count += 1
                for j in api_list:
                    if "/api/comment/list" in j.url:
                        print("#%d comment response %d save" % (pid, count))
                        save_path = folder_path + '\\comment_' + str(count) + '.pkl'
                        System.save_dictionary(save_path, j.json())
                        count += 1
                        pointless_scroll_count = 0
                api_list = []
                if pointless_scroll_count == pointless_scroll_threshold:
                    break

            print("#%d gathering reply api..." % pid)
            comment_xpath = 'xpath=//*[@id="app"]/div[2]/div[2]/div[1]/div[3]/div[1]/div[3]/div[2]/div'
            comment_locator = page.locator(comment_xpath)
            more_reply_locator = comment_locator.locator(".tiktok-1w2nwdz-StyledChevronDownFill.eo72wou3")
            count = 0
            while True:
                if more_reply_locator.count() == 1:
                    more_reply_locator.nth(0).click()
                    for j in api_list:
                        if "/api/comment/list/reply" in j.url:
                            print("#%d reply response %d save" % (pid, count))
                            save_path = folder_path + '\\reply_' + str(count) + '.pkl'
                            System.save_dictionary(save_path, j.json())
                            count += 1
                    api_list = []
                    break
                else:
                    more_reply_locator.nth(0).click()
                    for j in api_list:
                        if "/api/comment/list/reply" in j.url:
                            print("#%d reply response %d save" % (pid, count))
                            save_path = folder_path + '\\reply_' + str(count) + '.pkl'
                            System.save_dictionary(save_path, j.json())
                            count += 1
                    api_list = []

        print("====#%d comment api scraping finish====" % pid)

