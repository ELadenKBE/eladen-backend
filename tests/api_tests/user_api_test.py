from django.db import models

from app.errors import UnauthorizedError
from goods.models import Good
from users.models import ExtendedUser
from .base_api_test import WrapperForBaseTestClass


class UserEndpointTests(WrapperForBaseTestClass.BaseEndpointsTests):
    """Test goods list endpoint.
        """
    model = ExtendedUser
    mutation_create = '''mutation{{
                              createUser(username: "{0}",
                                         email: "testemail@gmail.com",
                                         password: "12345",
                                         role:1){{
                                                        id
                                                        username
                                                        email
                                                  }}
                                                }}'''
    mutation_create_name = "createUser"
    all_query = """query{
                    users{
                          id
                            username
                            email
                        }
                      }"""
    by_id_query = """query{
                    users(searchedId:1){
                          id
                            username
                            email
                        }
                      }"""
    mutation_update = ''''''
    mutation_update_name = ''

    mutation_delete = ''''''
    plural_name = "users"

    @staticmethod
    def create_item_with(user) -> models.Model:
        pass

    def test_create_item_as_admin(self):
        self.create_item_as("admin")

    def test_create_item_as_seller(self):
        with self.assertRaises(UnauthorizedError):
            self.create_item_as("seller")

    def test_create_item_as_user(self):
        with self.assertRaises(UnauthorizedError):
            self.create_item_as("user")

    def test_create_item_as_anon(self):
        self.create_item_as()

    def test_update_by_id_as_admin(self):
        self.fail()

    def test_update_by_id_as_seller(self):
        self.fail()

    def test_update_by_id_as_user(self):
        self.fail()

    def test_update_by_id_as_anon(self):
        self.fail()

    def test_delete_by_id_as_admin(self):
        self.fail()

    def test_delete_by_id_as_seller(self):
        self.fail()

    def test_delete_by_id_as_user(self):
        self.fail()

    def test_delete_by_id_as_anon(self):
        self.fail()