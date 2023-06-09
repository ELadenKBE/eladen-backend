from django.db.models import QuerySet, Q
from graphql import GraphQLResolveInfo

from app.errors import UnauthorizedError, ResourceError
from app.repository_base import RepositoryBase, IRepository
from goods.models import Good
from orders.models import Order
from users.models import ExtendedUser


class OrdersRepository(RepositoryBase, IRepository):

    model = Order

    @staticmethod
    def get_by_id(searched_id: str,
                  info: GraphQLResolveInfo = None) -> [QuerySet]:
        """
                TODO add strings

                :param info:
                :param searched_id:
                :return:
                """
        user: ExtendedUser = info.context.user
        if user.is_user():
            return Order.objects.filter(user=user, id=searched_id).first()
        if user.is_admin():
            return Order.objects.filter(id=searched_id).first()

    @staticmethod
    def get_items_by_filter(search_filter: Q,
                            info: GraphQLResolveInfo = None) -> [QuerySet]:
        pass

    @staticmethod
    def get_all_items(info: GraphQLResolveInfo = None) -> [QuerySet]:
        """
                TODO add docstr

                :param info:
                :return:
                """
        user: ExtendedUser = info.context.user
        if user.is_user():
            return Order.objects.filter(user=user).all()
        if user.is_admin():
            return Order.objects.all()

    @staticmethod
    def create_item(info: GraphQLResolveInfo = None, **kwargs) -> [QuerySet]:
        """
                TODO add docs

                :param info:
                :return:
                """
        # TODO notify sellers
        user = info.context.user or None
        if user is None:
            raise UnauthorizedError("Unauthorized access!")
        order = Order(time_of_order=kwargs["time_of_order"],
                      delivery_address=kwargs["delivery_address"],
                      # TODO calculate delivery and items price
                      items_price=1000,
                      delivery_price=100,
                      delivery_status="order created",
                      payment_status="not paid",
                      user=user)
        order.save()
        good_ids = kwargs["goods_ids"]
        order.goods.add(*good_ids)
        order.save()

        goods = Good.objects.filter(id__in=good_ids).all()

        # should decrease amounts of goods after order created
        def decrease_amount_func(good: Good):
            good.amount -= 1
            return good

        updated_goods = [decrease_amount_func(good) for good in goods]
        Good.objects.bulk_update(updated_goods, fields=["amount"])
        return order

    @staticmethod
    def update_item(info: GraphQLResolveInfo = None, **kwargs) -> [QuerySet]:
        """

        :param info:
        :param kwargs:
        :return:
        """
        order: Order = Order.objects.filter(id=kwargs["order_id"]).first()
        # TODO return error if None?
        user: ExtendedUser = info.context.user
        if user.is_user() and order.user == user or user.is_admin():
            if kwargs["delivery_address"] is not None:
                order.delivery_address = kwargs["delivery_address"]
            order.save()
        else:
            raise UnauthorizedError(
                "Not enough permissions to call this endpoint")
        return order

    @staticmethod
    def change_delivery_status(info: GraphQLResolveInfo,
                               id_arg: str,
                               delivery_status: str) -> [QuerySet]:

        """
                TODO add docs

                :param info:
                :param id_arg:
                :param delivery_status:
                :return:
                """
        user = info.context.user or None
        if user is None:
            raise UnauthorizedError("Unauthorized access!")
        order = Order.objects.get(id=id_arg)
        if order is None:
            raise ResourceError("Order is not accessible")
        order.delivery_status = delivery_status
        order.save()
        return order

    @staticmethod
    def change_payment_status(info: GraphQLResolveInfo,
                              id_arg: str,
                              payment_status: str) -> [QuerySet]:
        user = info.context.user or None
        if user is None:
            raise UnauthorizedError("Unauthorized access!")
        order = Order.objects.get(id=id_arg)
        if order is None:
            raise ResourceError("Order is not accessible")
        order.payment_status = payment_status
        order.save()
        return order

    @staticmethod
    def delete_item(info: GraphQLResolveInfo, searched_id: str):
        order = Order.objects.filter(id=searched_id).first()
        order.delete()