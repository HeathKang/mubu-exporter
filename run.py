import os
import aiohttp
import asyncio
import rich
from rich.prompt import Prompt
from rich.console import Console

GET_SINGLE_DOC_PATH = "https://api2.mubu.com/v3/api/document/edit/get"
EXPORT_SINGLE_DOC_PATH = "https://mubu.com/convert/export"
PHONE_LOGIN_PATH = "https://api2.mubu.com/v3/api/user/phone_login"
GET_ALL_DOCUMENTS_PATH = "https://api2.mubu.com/v3/api/list/get_all_documents_page"
PDF_PATH = "pdf/"
DOCX_PATH = "docx/"
FAILED_LIST = []

console = Console()


async def get_url(doc_id, doc_name, jwt_token):
    headers = {
        "jwt-token": jwt_token,
    }
    payload = {"docId": doc_id, "password": ""}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=GET_SINGLE_DOC_PATH, json=payload, headers=headers
        ) as res:
            try:
                result = await res.json()
                console.log(f"Fetching [bold blue]{doc_name}[/bold blue] content")
                return (result["data"]["definition"], doc_name)
            except Exception as e:
                console.print_exception(e)
                return None


async def write_to_pdf(data, doc_name, jwt_token):
    if data == None:
        console.log(f"Get {data} for {doc_name} error.")
        return

    headers = {"jwt-token": jwt_token, "origin": "https://mubu.com"}
    payload = {"type": "pdf", "definition": data}
    file_name = PDF_PATH + doc_name + ".pdf"
    file_path = file_name.replace(file_name.split("/")[-1], "")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=EXPORT_SINGLE_DOC_PATH, json=payload, headers=headers
        ) as res:
            try:
                result = await res.content.read()

                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                with open(file_name, "wb") as f:
                    console.log(
                        f"Writing content to [bold blue]{file_name}[/bold blue]"
                    )
                    f.write(result)
            except Exception as e:
                console.log(e)
                FAILED_LIST.append(file_name)


async def write_to_word(data, doc_name, jwt_token):
    if data == None:
        console.log(f"Get {data} for {doc_name} error.")
        return

    headers = {"jwt-token": jwt_token, "origin": "https://mubu.com"}
    payload = {"type": "docx", "definition": data}
    file_name = DOCX_PATH + doc_name + ".docx"
    file_path = file_name.replace(file_name.split("/")[-1], "")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=EXPORT_SINGLE_DOC_PATH, json=payload, headers=headers
        ) as res:
            try:
                result = await res.content.read()

                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                with open(file_name, "wb") as f:
                    console.log(
                        f"Writing content to [bold blue]{file_name}[/bold blue]"
                    )
                    f.write(result)
            except Exception as e:
                console.log(e)
                FAILED_LIST.append(file_name)


async def get_all_file_id_names(jwt_token: str) -> dict:
    payload = {"start": ""}
    headers = {
        "jwt-token": jwt_token,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=GET_ALL_DOCUMENTS_PATH, json=payload, headers=headers
        ) as res:
            result = await res.json()

            file_id_names = __generate_filenames(result)
            return file_id_names


def __generate_filenames(data: list) -> dict:
    documents = data.get("data").get("documents")
    file_id_names = {d.get("id"): d.get("name") for d in documents}
    console.log(f"Get [yellow]{len(file_id_names.keys())}[/yellow] documents:")
    return file_id_names


async def get_jwt_token(phone: str, password: str) -> str:
    payload = {"phone": phone, "password": password, "callbackType": 0}

    async with aiohttp.ClientSession() as session:
        async with session.post(url=PHONE_LOGIN_PATH, json=payload) as res:
            result = await res.json()
            if result["code"] != 0:
                console.log(f"[bold red]Error! please see the details \n {result}")
                raise Exception(res)
            return result["data"]["token"]


def parse_command():
    file_type = {
        "1": "pdf",
        "2": "doc",
    }
    username = Prompt.ask(
        "Please enter [blue]your[/blue] [yellow]phone number[/yellow]"
    )
    password = Prompt.ask(
        "Please enter [blue]your[/blue] [yellow]password[/yellow]", password=True
    )

    file_type_number = Prompt.ask(
        "Please select [yellow]file type[/yellow] you want to export: [blue][1] pdf [2] doc[/blue], default is [green]pdf[/green]",
        choices=["1", "2"],
    )
    return username, password, file_type.get(file_type_number, "pdf")


async def main():
    rich.print(
        "[bold green]Welcome to use mubu-exporter,please follow the below guide to start!"
    )
    phone, password, file_type = parse_command()
    export_to_file = write_to_pdf if file_type == "pdf" else write_to_word
    token = await get_jwt_token(phone, password)
    file_id_names = await get_all_file_id_names(token)
    with console.status("[bold green] Fetching data...") as status:
        url_doc_name_tasks = [
            get_url(doc_id, doc_name, token)
            for doc_id, doc_name in file_id_names.items()
        ]
        results = await asyncio.gather(*url_doc_name_tasks)

        tasks = [export_to_file(url, doc_name, token) for url, doc_name in results]
        _ = await asyncio.gather(*tasks)

    if len(FAILED_LIST) == 0:
        rich.print(
            f"[blue]Export done, please check [bold]{PDF_PATH}[/bold] folder to see all documents."
        )
    else:
        rich.print(f"[red]There are some files can't export, please check it:")
        for file_name in FAILED_LIST:
            rich.print(f"[blue] {file_name}")


if __name__ == "__main__":
    asyncio.run(main())
