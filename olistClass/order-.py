import pandas as pd
import numpy as np
from olist.utils import haversine_distance
from olist.data import Olist
from functools import reduce


class Order:
    '''
    DataFrames containing all orders as index,
    and various properties of these orders as columns
    '''
    def __init__(self):
        # Assign an attribute ".data" to all new instances of Order
        self.data = Olist().get_data()

    def get_wait_time(self, is_delivered=True):
        """
        Returns a DataFrame with:
        [order_id, wait_time, expected_wait_time, delay_vs_expected, order_status]
        and filters out non-delivered orders unless specified
        """
        # Hint: Within this instance method, you have access to the instance of the class Order in the variable self, as well as all its attributes
        olist= Olist
        data=olist.get_data(self)
        #make a copy of the orders dataframe
        orders = data['orders'].copy()
            # Calculate wait_time in days
        orders['order_purchase_timestamp']=pd.to_datetime(orders['order_purchase_timestamp'])
        orders['order_delivered_customer_date']=pd.to_datetime(orders['order_delivered_customer_date'])
        orders["wait_time"] = orders['order_delivered_customer_date']-orders['order_purchase_timestamp']
        orders["wait_time"]=orders["wait_time"].dt.days
        # calculate expect_wait_time
        orders['order_estimated_delivery_date']=pd.to_datetime(orders['order_estimated_delivery_date'])
        orders["expect_wait_time"] = orders['order_estimated_delivery_date']-orders['order_purchase_timestamp']
        orders["expect_wait_time"]=orders["expect_wait_time"].dt.days
        #calculate delay_vs_expected
        orders["delay_vs_expected"]=orders["wait_time"]-orders["expect_wait_time"]
        #orders["delay_vs_expected"]=orders[orders["delay_vs_expected"]<0]["delay_vs_expected"]=0
        orders.loc[orders["delay_vs_expected"]<0,'delay_vs_expected']=0
        # filter delivered orders
        wait_time_orders=orders[['order_id','wait_time','expect_wait_time','delay_vs_expected','order_status']]
        #update wait timer order with only delivered orders
        wait_time_orders = wait_time_orders.loc[wait_time_orders["order_status"] == "delivered"]
        self.wait_time_orders=wait_time_orders
        return self.wait_time_orders

    def get_review_score(self):
        """
        Returns a DataFrame with:
        order_id, dim_is_five_star, dim_is_one_star, review_score
        """
        data=self.data
        reviews=data['order_reviews'].copy()
        reviews["dim_is_five_star"]= reviews["review_score"]==5
        reviews["dim_is_one_star"]=reviews["review_score"]==1
        reviews["dim_is_five_star"]= reviews.dim_is_five_star.astype(int)
        reviews["dim_is_one_star"]=reviews.dim_is_one_star.astype(int)
        reviews=reviews[["order_id","dim_is_five_star","dim_is_one_star","review_score"]]
        self.reviews=reviews
        return self.reviews

    def get_number_items(self):
        """
        Returns a DataFrame with:
        order_id, number_of_items
        """
        data=self.data
        items_copy=data['order_items'].copy()
        order_copy=data['orders'].copy()
        items_copy=items_copy.groupby("order_id").size().reset_index(name='number_of_items')
        item_order_merge=order_copy.merge(items_copy,on='order_id', how='right')
        item_order_merge=item_order_merge[['order_id',"number_of_items"]]
        self.item_order_merge=item_order_merge
        return self.item_order_merge

    def get_number_sellers(self):
        """
        Returns a DataFrame with:
        order_id, number_of_sellers
        """
        data=self.data
        sellers = data['sellers'].copy()
        order_items = data['order_items'].copy()
        tmp=order_items.merge(sellers, on='seller_id',how="outer")
        number_of_seller=tmp.groupby("order_id").size().reset_index(name='number_of_sellers')
        self.number_of_seller=number_of_seller
        return self.number_of_seller

    def get_price_and_freight(self):
        """
        Returns a DataFrame with:
        order_id, price, freight_value
        """
        data=self.data
        orders = data['orders'].copy()
        order_items = data['order_items'].copy()
        order_items=order_items[['order_id','price','freight_value']]
        order_items=order_items.groupby("order_id")[["price",'freight_value']].sum().reset_index()
        order_price_freight=order_items.merge(orders,on='order_id', how='inner')
        order_price_freight=order_price_freight[['order_id','price','freight_value']]
        self.order_price_freight=order_price_freight
        return self.order_price_freight


    # Optional
    def get_distance_seller_customer(self):
        """
        Returns a DataFrame with:
        order_id, distance_seller_customer
        """
        pass  # YOUR CODE HERE

    def get_training_data(self,
                          is_delivered=True,
                          with_distance_seller_customer=False):
        """
        Returns a clean DataFrame (without NaN), with the all following columns:
        ['order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected',
        'order_status', 'dim_is_five_star', 'dim_is_one_star', 'review_score',
        'number_of_items', 'number_of_sellers', 'price', 'freight_value',
        'distance_seller_customer']
        """
        # Hint: make sure to re-use your instance methods defined above
        wait_time_order=Order().get_wait_time()
        review_score=Order().get_review_score()
        number_item=Order().get_number_items()
        number_seller=Order().get_number_sellers()
        price_freight=Order().get_price_and_freight()
        dfs=[wait_time_order, review_score, number_item, number_seller, price_freight]
        training_data=reduce(lambda left, right : left.merge(right,on='order_id',how='inner'),dfs).reset_index()
        self.traing_data=training_data
        return self.traing_data
