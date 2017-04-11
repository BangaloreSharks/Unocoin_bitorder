# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Merchant(models.Model):
	merchant_email = models.CharField(max_length = 50)
	merchant_id = models.IntegerField()
	bit_addr = models.CharField(max_length = 50)
	def __str__(self):
		return str(self.merchant_id)


class menuItem(models.Model):
	merchant = models.ForeignKey('Merchant', default = None , blank = True)
	name = models.CharField(max_length = 100)
	price = models.FloatField()
	def __str__(self):
		return str(self.merchant.merchant_id)

class Order(models.Model):
 	merchant = models.ForeignKey('Merchant', default = None , blank = True)
	client = models.CharField(max_length=100, default = None)
	eta = models.CharField(max_length=100, default=None, blank=True)
	def __str__(self):
		return str(self.merchant.merchant_id)+self.client

class OrderItem(models.Model):
	order = models.ForeignKey('Order', default = None , blank = True)
	item = models.ForeignKey('menuItem', default = None , blank = True)
	qty = models.IntegerField(default=0)
	def __str__(self):
		return str(self.order.client)+str(self.item.name)
