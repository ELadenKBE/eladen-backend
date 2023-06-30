import graphene
from decouple import config

from app.base_service import BaseService
from app.product_service import GoodType
from goods.models import Good


class OrderType(graphene.ObjectType):
    id = graphene.Int()
    time_of_order = graphene.String()
    items_price = graphene.Decimal()
    delivery_price = graphene.Float()
    user_id = graphene.Int()
    delivery_status = graphene.String()
    payment_status = graphene.String()
    goods = graphene.List(GoodType)
    delivery_address = graphene.String()

    def __init__(self,
                 id=None,
                 timeOfOrder=None,
                 itemsPrice=None,
                 deliveryPrice=None,
                 userId=None,
                 deliveryStatus=None,
                 paymentStatus=None,
                 goods=None,
                 deliveryAddress=None
                 ):
        self.id = id
        self.time_of_order = timeOfOrder
        self.items_price = itemsPrice
        self.user_id = userId
        self.delivery_status = deliveryStatus
        self.payment_status = paymentStatus
        self.delivery_address = deliveryAddress
        self.delivery_price = deliveryPrice
        self.goods = goods


class OrderService(BaseService):

    url = config('ORDER_SERVICE_URL', default=False, cast=str)
    service_name = 'Order'

    def get_orders(self, info):
        items_list = self._get_data(entity_name='orders', info=info)
        objects = [self._create_order_filler(**order) for order in items_list]
        return objects

    @staticmethod
    def _create_order_filler(**params):
        if 'goods' in params:
            goods_dict = params['goods']
            del params['goods']
            goods = [Good(**param) for param in goods_dict]
            type_object = OrderType(goods=goods, **params)
            return type_object
        else:
            type_object = OrderType(**params)
            return type_object