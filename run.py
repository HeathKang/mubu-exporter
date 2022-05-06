import os
import requests
import rich
from rich.console import Console

GET_SINGLE_DOC_PATH = "https://api2.mubu.com/v3/api/document/edit/get"
EXPORT_SINGLE_DOC_PATH = "https://mubu.com/convert/export"
PHONE_LOGIN_PATH = "https://api2.mubu.com/v3/api/user/phone_login"
GET_ALL_DOCUMENTS_PATH = "https://api2.mubu.com/v3/api/list/get_all_documents_page"
PDF_PATH = 'pdf/'
console = Console()

def get_url(doc_id, doc_name, jwt_token):
    headers = {
        "jwt-token": jwt_token,
    }
    payload = {"docId": doc_id,"password":""}
        
    res = requests.post(url=GET_SINGLE_DOC_PATH,
        headers=headers,
        json=payload)
    console.log(f"Fetching [bold blue]{doc_name}[/bold blue] content")
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
    if not os.path.exists(PDF_PATH):
        os.makedirs(PDF_PATH)
    with open(file_name, "wb") as f:
        console.log(f"Writing content to [bold blue]{file_name}[/bold blue]")
        f.write(res.content)
        
def get_all_file_id_names(jwt_token: str) -> dict:
    payload = {"start":""}
    headers = {
        "jwt-token": jwt_token,
    }
    res = requests.post(url=GET_ALL_DOCUMENTS_PATH,
    headers=headers,
    json=payload)

    file_id_names = __generate_filenames(res.json())
    return file_id_names

def __generate_filenames(data: list) -> dict:
    documents = data.get("data").get("documents")
    file_id_names = {d.get("id"): d.get("name") for d in documents}
    console.log(f"Get [yellow]{len(file_id_names.keys())}[/yellow] documents:")
    return file_id_names

def get_jwt_token(phone:str, password:str) -> str:
        
    payload = {
        "phone": phone,
        "password": password,
        "callbackType":0
        }

    res = requests.post(url=PHONE_LOGIN_PATH,
            json=payload)

    if res.json()['code'] != 0:
        console.log(f"[bold red]Error! please see the details \n {res.json()}")
        raise Exception(res.json())
    return res.json()["data"]["token"]

def parse_command():
    username = console.input("Please enter [blue]your[/blue] [yellow]phone number[/yellow]:")
    password = console.input("Please enter [blue]your[/blue] [yellow]password[/yellow]:")
    return username, password

def main():
    rich.print("[bold green]Welcome to use mubu-exporter,please follow the below guide to start!")
    phone, password = parse_command()
    token = get_jwt_token(phone, password)
    file_id_names = get_all_file_id_names(token)
    with console.status("[bold green] Fetching data...") as status:
        for doc_id, doc_name in file_id_names.items():
            data = get_url(doc_id, doc_name, token)
            write_to_pdf(data, doc_name, token)
    rich.print(f"[blue]Export done, please check [bold]{PDF_PATH}[/bold] folder to see all documents.")

if __name__ == '__main__':
    main()

 