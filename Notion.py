import credentials
from notion.client import NotionClient


def getToDOTask(boardName=None):
    """
    Get task list page from Notion
    """
    token = credentials.Notion_token
    client = NotionClient(token_v2=token)

    tasklist_page = client.get_collection_view(credentials.task_list_page_url)

    if boardName == "td":
        boardName = "To Do"
    elif boardName == "ing":
        boardName = "Doing"
    elif boardName == "done":
        boardName = "done"
    else:
        boardName = "To Do - today"

    for task in tasklist_page.collection.get_rows(search="To Do - today"):
        yield task.title


if __name__ == '__main__':
    for title in getToDOTask():
        print(title)