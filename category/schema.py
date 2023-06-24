import graphene
from graphene_django import DjangoObjectType

from app.permissions import permission, Admin, All
from category.models import Category
from category.repository import CategoryRepository
from app.product_service import ProductService


class CategoryType(DjangoObjectType):

    product_service = ProductService()

    class Meta:
        model = Category


class Query(graphene.ObjectType):
    categories = graphene.List(CategoryType,
                               search=graphene.String(),
                               searched_id=graphene.String(),
                               )

    @permission(roles=[All])
    def resolve_categories(self, info, **kwargs):
        """
        Return all elements if search arguments are not given.

        :param info: request context information
        :return:
        """
        return CategoryType.product_service.get_categories(info)


class CreateCategory(graphene.Mutation):
    id = graphene.Int()
    title = graphene.String(required=True)

    class Arguments:
        title = graphene.String()

    @permission(roles=[Admin])
    def mutate(self, info, title):
        """
        TODO add docs

        :param info:
        :param title:
        :return:
        """
        created_category = CategoryType.product_service.create_category(info)

        return CreateCategory(
            id=created_category.id,
            title=created_category.title
        )


class UpdateCategory(graphene.Mutation):
    id = graphene.Int(required=True)
    title = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()

    @permission(roles=[Admin])
    def mutate(self, info, id, title):
        """
        TODO add docs

        :param info:
        :param id:
        :param title:
        :return:
        """
        category = CategoryType.product_service.update_category(info=info)

        return UpdateCategory(
            id=category.id,
            title=category.title
        )


class DeleteCategory(graphene.Mutation):
    id = graphene.Int(required=True)
    title = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)

    @permission(roles=[Admin])
    def mutate(self, info, id):
        """
        TODO add docs

        :param info:
        :param id:
        :return:
        """
        CategoryType.product_service.delete_category(info)

        return CreateCategory(
            id=id
        )


class Mutation(graphene.ObjectType):
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()
