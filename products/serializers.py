from .models import Product, ProductCategory
from rest_framework import serializers


class ProductCategorySerializer(serializers.ModelSerializer):
    '''
    Serializer to serialize product categories
    '''
    class Meta:
        model = ProductCategory
        fields = "__all__"


class ProductReadSerializer(serializers.ModelSerializer):
    '''
    This is a ProductReadSerializer which is used while reading or retreiving the products info
    '''
    seller = serializers.CharField(
        source="seller.get_full_name", read_only=True)
    # Here the source category.name -> category is the name given to the serializer
    # since we have the category instance inside the category we can access the names through category.name
    # if the serializer name was category_instance then to extract name we would write category_instance.name
    category = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class ProductWriteSerializer(serializers.ModelSerializer):
    '''
    This is a ProductWriteSerializer which is used while creating or updating a product record
    '''
    # serializers.CurrentUserDefault(): Automatically assigns the currently logged-in user when creating an address.
    # Purpose: Ensures a user can only create a product for themselves, preventing users from setting another user's ID manually.
    seller = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = ProductCategorySerializer()

    class Meta:
        model = Product
        fields = (
            "seller",
            "category",
            "name",
            "desc",
            "image",
            "price",
            "quantity",
        )

    def create(self, validated_data):
        # Popping out and extracting the category field data
        category = validated_data.pop("category")

        # Creating the category record in the table
        category_instance, created = ProductCategory.objects.get_or_create(
            **category)

        # Creating a product record with the remaining validated data and passing in the category_instance after creation
        product = Product.objects.create(
            **validated_data, category=category_instance)
        return product

    def update(self, instance, validated_data):
        # We update the category data if it is present in the request
        if "category" in validated_data:
            # Extract the category serialize instance from the object
            category_serializer = self.fields["category"]

            # Extracting the updated category data from the validated_data
            category_updated_data = validated_data.pop("category")

            # Extracting the old instance of the category
            category_instance = instance.category
            category_serializer.update(
                category_instance, category_updated_data)
        return super().update(instance, validated_data)
