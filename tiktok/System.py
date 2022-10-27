import sys
import time

import psutil
import os
import shutil
import pickle
import pandas as pd
import natsort


def memory_check_variable(variable):
    kb = (0.001)*(sys.getsizeof(variable))
    print("Variable memory KB: %.3f KB"%kb)


def memory_check_system():
    memory_usage_dict = dict(psutil.virtual_memory()._asdict())
    memory_usage_percent = memory_usage_dict['percent']
    print(f"Memory usage percentage: {memory_usage_percent}%")
    # current process RAM usage
    pid = os.getpid()
    current_process = psutil.Process(pid)
    current_process_memory_usage_as_KB = current_process.memory_info()[0] / 2.**20
    print(f"Current memory KB: {current_process_memory_usage_as_KB: 9.3f} KB")


def read_input():
    new_input_list = []
    filename = 'input.xlsx'
    try:
        df = pd.read_excel(filename, header=None, engine='openpyxl')
        input_list = df.values.tolist()
        for i in input_list:
            new_input_list.append(i[0])
    except:
        print("You Need input.xlsx")
        quit()
    return new_input_list


def read_directory(directory):
    file_list = os.listdir(directory)
    file_list = natsort.natsorted(file_list)
    return file_list


def create_folder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
            print('Error: Creating directory.' + directory)


def delete_folder(directory):
    if os.path.exists(directory):
       shutil.rmtree(directory, ignore_errors=True)


def save_dictionary(directory, data):
    with open(directory, 'wb') as tf:
        pickle.dump(data, tf)


def read_dictionary(directory):
    with open(directory, 'rb') as fr:
        loaded = pickle.load(fr)
    return loaded


def delete_file(directory):
    if os.path.exists(directory):
        os.remove(directory)


def overwrite_csv(data,directory):
    if not os.path.exists(directory):
        data.to_csv(directory, mode='w', index=False, header=True, encoding='utf-8-sig')
    else:
        data.to_csv(directory, mode='a', index=False, header=False, encoding='utf-8-sig')


def csv_to_excel(src_dir,save_dir):
    src = pd.read_csv(src_dir)
    src.to_excel(save_dir,index=None,header=True)


if __name__ == '__main__':
    """
    https://free-proxy-list.net/
    https://www.proxydocker.com/kr/proxylist/type/https
    https://spys.one/en/free-proxy-list/
    https://www.freeproxylists.net/?c=&pt=&pr=HTTPS&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=90
    only find https / port is 80 or 8080
    """
    print("==============Proxy Check==============")
    ip = input("ip: ")
    port = input("port: ")
    server = "http://" + ip + ":" + port
    print("Proxy test: " + server)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch(headless=False, proxy={"server": server})
        page = browser.new_page()
        page.goto('https://www.tiktok.com/', timeout=0)
        time.sleep(5)
