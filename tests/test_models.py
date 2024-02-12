# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Change it an save it
        product.description = "testing"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "testing")

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        # Create 5 Products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_update_product_without_id(self):
        """It should Update a Product without ID"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Change product id to none
        product.id = None
        # check that DataValidationError("Update called with empty ID field") is raised
        with self.assertRaises(DataValidationError):
            product.update()

    def test_serialize_a_product(self):
        """It should serialize a Product into a dictionary"""
        product = ProductFactory()
        product.id = 1  # Assigning a specific ID for testing
        product.name = "Test Product"
        product.description = "A product used for testing"
        product.price = Decimal('10.99')
        product.available = True
        product.category = Category.FOOD  # Assuming FOOD is a valid Category enum

        serialized_product = product.serialize()

        # Verify that the product is correctly serialized
        self.assertEqual(serialized_product["id"], product.id)
        self.assertEqual(serialized_product["name"], product.name)
        self.assertEqual(serialized_product["description"], product.description)
        self.assertEqual(serialized_product["price"], "10.99")  # Price should be a string
        self.assertEqual(serialized_product["available"], product.available)
        self.assertEqual(serialized_product["category"], product.category.name)  # Check enum string conversion

    def test_deserialize_product(self):
        """It should deserialize a product with valid data"""
        data = {
            "name": "Test Product",
            "description": "A product used for testing.",
            "price": "19.99",
            "available": True,
            "category": "FOOD"
        }
        product = Product()
        product.deserialize(data)

        self.assertEqual(product.name, data["name"])
        self.assertEqual(product.description, data["description"])
        self.assertEqual(product.price, Decimal(data["price"]))
        self.assertEqual(product.available, data["available"])
        self.assertEqual(product.category, Category.FOOD)

    def test_deserialize_product_invalid_available_type(self):
        """It should not deserialize a product with an invalid type for 'available'"""
        data = {
            "name": "Invalid Available Type",
            "description": "The available field is not a boolean.",
            "price": "10.00",
            "available": "yes",  # Invalid type
            "category": "FOOD"
        }
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_deserialize_product_missing_key(self):
        """It should not deserialize a product with missing keys"""
        data = {
            # "name" is missing
            "description": "A description.",
            "price": "5.00",
            "available": True,
            "category": "CLOTHS"
        }
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_deserialize_product_invalid_category(self):
        """It should not deserialize a product with an invalid category"""
        data = {
            "name": "Invalid Category",
            "description": "Invalid category test.",
            "price": "15.00",
            "available": True,
            "category": "INVALID_CATEGORY"  # Invalid category
        }
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_find_by_price(self):
        """It should return all products with a given price"""
        # Create products with different prices
        product1 = ProductFactory.create(price=Decimal('19.99'))
        product1.create()
        product2 = ProductFactory.create(price=Decimal('19.99'))
        product2.create()
        ProductFactory.create(price=Decimal('29.99')).create()

        # Search for products by price
        found_products = Product.find_by_price(Decimal('19.99')).all()

        # Verify that the correct products are returned
        self.assertEqual(len(found_products), 2)
        for product in found_products:
            self.assertEqual(product.price, Decimal('19.99'))

        # test the string input functionality
        found_products_str = Product.find_by_price("19.99").all()
        self.assertEqual(len(found_products_str), 2)
        for product in found_products_str:
            self.assertEqual(product.price, Decimal('19.99'))

    def test_find_by_availability(self):
        """It should return products based on their availability"""
        # Create products with different availability statuses
        available_product = ProductFactory.create(available=True)
        available_product.create()
        unavailable_product = ProductFactory.create(available=False)
        unavailable_product.create()

        # Search for available products
        available_products = Product.find_by_availability(True).all()

        # Verify that only available products are returned
        self.assertTrue(all(product.available for product in available_products))
        self.assertEqual(len(available_products), 1)
        self.assertIn(available_product, available_products)

        # Search for unavailable products
        unavailable_products = Product.find_by_availability(False).all()

        # Verify that only unavailable products are returned
        self.assertTrue(all(not product.available for product in unavailable_products))
        self.assertEqual(len(unavailable_products), 1)
        self.assertIn(unavailable_product, unavailable_products)
