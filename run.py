import pickle
import time
import requests
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service


GET_SINGLE_DOC_PATH = "https://api2.mubu.com/v3/api/document/edit/get"
EXPORT_SINGLE_DOC_PATH = "https://mubu.com/convert/export"
PDF_PATH = 'pdf/'

def save_cookied_url(url):
    opts = Options()
    service = Service(executable_path=r"C:\Users\N_Kang\Desktop\tools\edgedriver_win64\msedgedriver.exe")
    driver = webdriver.Edge(options=opts,service=service)
    driver.get(url)
    time.sleep(30)
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
    driver.close()

def init_driver():
    opts = Options()
    service = Service(executable_path=r"C:\Users\N_Kang\Desktop\tools\edgedriver_win64\msedgedriver.exe")
    opts.add_argument("--headless")

    driver = webdriver.Edge(options=opts,service=service)
    cookies = pickle.load(open("cookies.pkl", "rb"))
    driver.get("https://mubu.com")
    for cookie in cookies:
        driver.add_cookie(cookie)
    return driver

def get_url(doc_id, doc_name, jwt_token):
    headers = {
        "jwt-token": jwt_token,
    }
    payload = {"docId": doc_id,"password":""}
    
    res = requests.post(url=GET_SINGLE_DOC_PATH,
            headers=headers,
            json=payload)
    print(f"=================================================================")
    print(f"----------------waiting for get {doc_id} ： {doc_name} content--------------------")
    print(f"=================================================================")
    return res.json()["data"]["definition"]

def write_to_pdf(data, doc_name, jwt_token):
    headers = {
        "jwt-token": jwt_token,
        "origin": "https://mubu.com"
    }
    payload = {
        "type": "pdf",
        "definition": data
    }
    res = requests.post(url=EXPORT_SINGLE_DOC_PATH,
            headers=headers,
            json=payload)

    file_name = PDF_PATH + doc_name + '.pdf'
    with open(file_name, "wb") as f:
        print(f"=================================================================")
        print(f"---------------------write content to {file_name}----------------")
        print(f"=================================================================")
        f.write(res.content)
        
def get_all_file_id_names(url="https://api2.mubu.com/v3/api/list/get_all_documents_page") -> dict:
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        if cookie.get('name').lower() == 'jwt-token':
            jwt_token = cookie.get('value')
    payload = {"start":""}
    headers = {
        "jwt-token": jwt_token,
    }
    res = requests.post(url=url,
    headers=headers,
    json=payload)

    file_id_names = __generate_filenames(res.json())
    return file_id_names

def __generate_filenames(data: list) -> dict:
    documents = data.get("data").get("documents")
    file_id_names = {d.get("id"): d.get("name") for d in documents}
    print(f"=================================================================")
    print(f"get {len(file_id_names.keys())} contents:")
    print(file_id_names)
    print(f"=================================================================")
    return file_id_names

def get_jwt_token(path="cookies.pkl") -> str:
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        if cookie.get('name').lower() == 'jwt-token':
            jwt_token = cookie.get('value')
    return jwt_token


def main():
    # save_cookied_url("https://mubu.com/login")
    file_id_names = get_all_file_id_names()
    token = get_jwt_token()
    for doc_id, doc_name in file_id_names.items():
        data = get_url(doc_id, doc_name, token)
        write_to_pdf(data, doc_name, token)


if __name__ == '__main__':
    main()

 