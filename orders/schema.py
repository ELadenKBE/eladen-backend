from typing import Callable

import graphene
from graphene_django import DjangoObjectType

from app.errors import UnauthorizedError, ResourceError
from app.permissions import permission, Admin, User, Seller
from goods.models import Good
from goods.schema import GoodType
from users.schema import UserType
from .models import Order


class OrderType(DjangoObjectType):
    class Meta:
        model = Order


class Query(graphene.ObjectType):
    orders = graphene.List(OrderType, searched_id=graphene.Int())

    @permission(roles=[Admin, User])
    def resolve_orders(self, info, searched_id=None, **kwargs):
        """
        TODO add docstring

        :param searched_id:
        :param info:
        :param kwargs:
        :return:
        """
        if searched_id:
            return [Order.get_by_id_with_permission(info,
                                                    searched_id=searched_id)]
        return Order.get_all_orders_with_permission(info)


class CreateOrder(graphene.Mutation):
    id = graphene.Int()
    time_of_order = graphene.String()
    delivery_address = graphene.String()
    items_price = graphene.Float()
    delivery_price = graphene.Float()
    user = graphene.Field(UserType)
    delivery_status = graphene.String()
    payment_status = graphene.String()
    goods = graphene.List(GoodType)

    class Arguments:
        time_of_order = graphene.String()
        delivery_address = graphene.String()
        goods_ids = graphene.List(graphene.ID, required=True)

    @permission(roles=[Admin, User])
    def mutate(self, info,
               time_of_order,
               delivery_address,
               goods_ids):
        # TODO notify sellers
        user = info.context.user or None
        if user is None:
            raise UnauthorizedError("Unauthorized access!")
        order = Order(time_of_order=time_of_order,
                      delivery_address=delivery_address,
                      # TODO calculate delivery and items price
                      items_price=1000,
                      delivery_price=100,
                      delivery_status="order created",
                      payment_status="not paid",
                      user=user)
        order.save()
        order.goods.add(*goods_ids)
        order.save()

        goods = Good.objects.filter(id__in=goods_ids).all()

        # should decrease amounts of goods after order created
        def decrease_amount_func(good: Good):
            good.amount -= 1
            return good

        updated_goods = [decrease_amount_func(good) for good in goods]
        Good.objects.bulk_update(updated_goods, fields=["amount"])

        return CreateOrder(
            id=order.id,
            delivery_address=order.delivery_address,
            items_price=order.items_price,
            delivery_price=order.delivery_price,
            time_of_order=order.time_of_order,
            user=user,
            delivery_status=order.delivery_status,
            payment_status=order.payment_status,
            goods=order.goods.all()
        )


class UpdateOrder(graphene.Mutation):
    id = graphene.Int()
    time_of_order = graphene.String()
    delivery_address = graphene.String()
    items_price = graphene.Float()
    delivery_price = graphene.Float()
    user = graphene.Field(UserType)
    delivery_status = graphene.String()
    payment_status = graphene.String()

    class Arguments:
        order_id = graphene.Int()
        delivery_address = graphene.String()

    @permission(roles=[Admin])
    def mutate(self, info,
               order_id,
               delivery_address=None):
        # TODO return error if None?
        order: Order = Order.objects.filter(id=order_id).first()
        user = info.context.user or None
        order.update_with_permission(info, delivery_address)
        return UpdateOrder(
            id=order.id,
            delivery_address=order.delivery_address,
            items_price=order.items_price,
            delivery_price=order.delivery_price,
            time_of_order=order.time_of_order,
            user=user
        )


class ChangeDeliveryStatus(graphene.Mutation):
    id = graphene.Int()
    delivery_status = graphene.String()

    class Arguments:
        id = graphene.Int()
        delivery_status = graphene.String()

    def mutate(self, info, id_arg, delivery_status):
        user = info.context.user or None
        if user is None:
            raise UnauthorizedError("Unauthorized access!")
        order = Order.objects.get(id=id_arg)
        if order is None:
            raise ResourceError("Order is not accessible")
        order.delivery_status = delivery_status
        order.save()

        return ChangeDeliveryStatus(id=order.id,
                                    delivery_status=order.delivery_status)


class ChangePaymentStatus(graphene.Mutation):
    id = graphene.Int()
    payment_status = graphene.String()

    class Arguments:
        id = graphene.Int()
        payment_status = graphene.String()

    def mutate(self, info, id_arg, payment_status):
        user = info.context.user or None
        if user is None:
            raise UnauthorizedError("Unauthorized access!")
        order = Order.objects.get(id=id_arg)
        if order is None:
            raise ResourceError("Order is not accessible")
        order.payment_status = payment_status
        order.save()

        return ChangeDeliveryStatus(id=order.id,
                                    payment_status=order.payment_status)


class DeleteOrder(graphene.Mutation):
    id = graphene.Int(required=True)

    class Arguments:
        order_id = graphene.Int(required=True)

    @permission(roles=[Admin])
    def mutate(self, info, order_id):
        order = Order.objects.filter(id=order_id).first()
        order.delete()
        return DeleteOrder(
            id=order_id
        )


class Mutation(graphene.ObjectType):
    create_order = CreateOrder.Field()
    change_delivery_status = ChangeDeliveryStatus.Field()
    change_payment_status = ChangePaymentStatus.Field()
    update_order = UpdateOrder.Field()
    delete_order = DeleteOrder.Field()
