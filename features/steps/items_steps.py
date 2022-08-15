import requests
from behave import given
from compare import expect


@given('the following items')
def step_impl(context):
    """ Delete all Suppliers and load new ones """
    # List all of the pets and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/api/items"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for item in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{item['id']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new pets
    for row in context.table:
        payload = {
            "name": row['name']
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)
