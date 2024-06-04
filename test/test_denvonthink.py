from MyPyTest.client.devonthink_client import *


def test_databases():
    print("Databases:")
    for db in dt.databases:
        print(db.name)
        assert db.name == "Inbox"


# pytest -q -s "/Users/yutianran/Documents/MyPKM/test_denvonthink.py::test_inbox"
def test_selected_records():
    # get selected records
    records = dt.selected_records
    # get the first selected record and print its information
    if records:
        first = records[0]
        print(first.name)
        print(first.type)
        print(first.reference_url)
        print(first.plain_text)
    selected_record = records[0]
    print(selected_record.name)


def test_inbox():
    inbox = dt.inbox
    print(inbox.name)
    # create a new folder in inbox
    dt.create_location("new-group-from-pydt3", inbox)
    # create record in inbox
    record = dt.create_record_with(
        {
            "name": "hello-from-pydt3",
            "type": "markdown",
            "plain text": "# Hello from pydt3",
        },
        inbox,
    )
    print(record)


def test_add_webloc_bookmark_to_readlater():
    create_webloc_record("test-webloc", "https://www.google.com")
