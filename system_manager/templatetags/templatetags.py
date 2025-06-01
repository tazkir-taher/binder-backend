# import json
#
# from django import template
# from datetime import datetime
#
# import system_manager.views
# from system_settings.models import SystemSettings
# from django.contrib.auth.models import Permission, Group, User
# # from product.models import Category, Product
# # from vendor.models import VendorOverview
# # from customer.models import CustomerOverview
# # from purchase_order.models import Bills, BillPayments
# # from sales_order.models import Invoice, InvoicePayments, SalesOrder, InvoiceSO, SalesOrderProducts
# # from django.db.models import Avg, Max, Min, Sum, Q
# # from purchase_order.models import PurchaseOrder, PurchaseOrderProducts
#
# register = template.Library()
#
#
# @register.simple_tag
# def footer():
#     return "Developed by Soft Tech Innovation Ltd."
#
#
# @register.simple_tag
# def check_group_permission(group_name, permission_code_name):
#     if Permission.objects.filter(codename__exact=permission_code_name, group__name=group_name).exists():
#         return "checked"
#     else:
#         return ""
#
#
# @register.simple_tag
# def get_user_group(request):
#     try:
#         return Group.objects.get(user=request.user).name
#     except Exception as e:
#         system_manager.views.log(request.path, e)
#         return "N/A"
#
#
# @register.simple_tag
# def get_user_group(request):
#     try:
#         return Group.objects.get(user=request.user).name
#     except Exception as e:
#         system_manager.views.log(request.path, e)
#         return "N/A"
#
#
# @register.simple_tag
# def get_user_group_name(request, user):
#     try:
#         return Group.objects.get(user=user).name
#     except Exception as e:
#         system_manager.views.log(request.path, e)
#         return "N/A"
#
#
# @register.simple_tag
# def generate_group_name_id(request, group_name):
#     try:
#         if group_name == "N/A":
#             return "none"
#         return str(group_name).lower().replace(' ', '')
#     except Exception as e:
#         system_manager.views.log(request.path, e)
#         return "N/A"
#
#
# @register.simple_tag
# def get_group_user_count(request, group_name):
#     try:
#         return User.objects.filter(groups__name=group_name).count()
#     except Exception as e:
#         system_manager.views.log(request.path, e)
#         return 0
#
#
# @register.simple_tag
# def getSubcategories(category_id):
#     subcategories = []
#     try:
#         subcategories = Category.objects.filter(parent=category_id).values('id', 'name')
#     except Exception:
#         pass
#     return subcategories
#
#
# @register.simple_tag
# def getVendorPayable(vendor_id):
#     return VendorOverview.objects.get(vendor_id=vendor_id).outstanding_payable
#
#
# @register.simple_tag
# def getCustomerReceivable(customer_id):
#     return CustomerOverview.objects.get(customer_id=customer_id).outstanding_receivables
#
#
# @register.simple_tag
# def checkExpiryDate(expiry_date):
#     if expiry_date is None:
#         return ""
#     remaining_days = (expiry_date - datetime.now().date()).days
#     return remaining_days
#
#
# @register.simple_tag
# def checkExpiredDate(expiry_date):
#     if expiry_date is None:
#         return ""
#     remaining_days = (datetime.now().date() - expiry_date).days
#     return remaining_days
#
#
# @register.simple_tag
# def getOrderStatus():
#     # STATUS = ['DRAFT', 'ISSUED', 'RECEIVED', 'BILLED', 'COMPLETE']
#     STATUS = ['DRAFT', 'ISSUED']
#     return STATUS
#
#
# @register.simple_tag
# def getSalesOrderStatus():
#     # STATUS = ['DRAFT', 'ISSUED', 'RECEIVED', 'BILLED', 'COMPLETE']
#     STATUS = ['DRAFT', 'CONFIRMED']
#     return STATUS
#
#
# @register.simple_tag
# def vendorBalanceOverview(vendor_id):
#     try:
#         payable_amount = Bills.objects.filter(vendor_id=vendor_id, status="DUE")
#         paid_amount = Bills.objects.filter(vendor_id=vendor_id, status="PAID")
#
#         payable_amount_instance = Bills.objects.filter(vendor_id=vendor_id)
#         if payable_amount_instance.count() > 0:
#             last_billed = payable_amount_instance.last().created_at
#         else:
#             last_billed = 'N/A'
#
#         paid_amount_instance = BillPayments.objects.filter(vendor_id=vendor_id, bill__status="PAID")
#         if paid_amount_instance.count() > 0:
#             last_paid = paid_amount_instance.last().created_at
#         else:
#             last_paid = 'N/A'
#
#         payable_amount = payable_amount.aggregate(Sum('amount'))
#         paid_amount = paid_amount.aggregate(Sum('amount'))
#
#         if payable_amount['amount__sum'] is None:
#             payable_amount = 0
#         else:
#             payable_amount = payable_amount['amount__sum']
#
#         if paid_amount['amount__sum'] is None:
#             paid_amount = 0
#         else:
#             paid_amount = paid_amount['amount__sum']
#         return {
#             'paid_amount': paid_amount,
#             'last_paid': last_paid,
#             'payable_amount': payable_amount,
#             'last_billed': last_billed
#         }
#     except Exception as e:
#         system_manager.views.log('templatetags.py', e)
#         return {
#             'paid_amount': 0,
#             'last_paid': 'N/A',
#             'payable_amount': 0,
#             'last_billed': 'N/A'
#         }
#
#
# @register.simple_tag
# def customerBalanceOverview(customer_id):
#     try:
#         receivable_amount = Invoice.objects.filter(customer_id=customer_id, status="DUE")
#         paid_amount = Invoice.objects.filter(customer_id=customer_id, status="PAID")
#
#         receivable_amount = receivable_amount.aggregate(Sum('amount'))
#         paid_amount = paid_amount.aggregate(Sum('amount'))
#
#         if receivable_amount['amount__sum'] is None:
#             receivable_amount = 0
#         else:
#             receivable_amount = receivable_amount['amount__sum']
#
#         if paid_amount['amount__sum'] is None:
#             paid_amount = 0
#         else:
#             paid_amount = paid_amount['amount__sum']
#         return {
#             'paid_amount': paid_amount,
#             'receivable_amount': receivable_amount
#         }
#     except Exception as e:
#         system_manager.views.log('templatetags.py', e)
#         return {
#             'paid_amount': 0,
#             'receivable_amount': 0,
#         }
#
#
# @register.simple_tag
# def getDashboardSummary():
#     try:
#         to_be_shipped = SalesOrder.objects.filter(
#             (~Q(status='DRAFT') & ~Q(status='CANCELLED')) & Q(shipped=False) & Q(complete=False)).count()
#         to_be_packed = SalesOrder.objects.filter(
#             (~Q(status='DRAFT') & ~Q(status='CANCELLED')) & Q(packed=False) & Q(complete=False)).count()
#         to_be_invoiced = SalesOrder.objects.filter(
#             (~Q(status='DRAFT') & ~Q(status='CANCELLED')) & Q(invoiced=False) & Q(complete=False)).count()
#         to_be_delivered = SalesOrder.objects.filter(
#             (~Q(status='DRAFT') & ~Q(status='CANCELLED')) & Q(complete=False)).count()
#         return {
#             'to_be_shipped': to_be_shipped,
#             'to_be_packed': to_be_packed,
#             'to_be_invoiced': to_be_invoiced,
#             'to_be_delivered': to_be_delivered
#         }
#     except Exception:
#         return {
#             'to_be_shipped': 0,
#             'to_be_packed': 0,
#             'to_be_invoiced': 0,
#             'to_be_delivered': 0
#         }
#
#
# @register.simple_tag
# def getStockSummary():
#     try:
#         qty_in_hand = Product.objects.all().aggregate(Sum('ps_on_hand'))
#         qty_to_receive = PurchaseOrderProducts.objects.filter(po__received=False).aggregate(Sum('quantity'))
#         return {
#             'qty_in_hand': qty_in_hand['ps_on_hand__sum'],
#             'qty_to_receive': qty_to_receive['quantity__sum']
#         }
#     except Exception:
#         return {
#             'qty_in_hand': 0,
#             'qty_to_receive': 0
#         }
#
#
# @register.simple_tag
# def showBackorderMenu(cart):
#     try:
#         for item in cart:
#             if item.product.ps_on_hand <= item.product.ps_committed:
#                 return True
#         return False
#     except Exception as e:
#         system_manager.views.log('templatetags.py', e)
#         return False
#
#
# @register.simple_tag
# def calculateDifference(a, b):
#     return round(float(a) - float(b), 2)
#
#
# @register.simple_tag
# def productsStat(product_id):
#     try:
#         so_product_data = SalesOrder.objects.filter(so_instance__product_id=product_id)
#         po_product_data = PurchaseOrder.objects.filter(po_instance__product_id=product_id)
#         return {
#             'tobe_shipped': so_product_data.filter(shipped=False).count(),
#             'tobe_received': po_product_data.filter(received=False).count(),
#             'tobe_invoiced': so_product_data.filter(invoiced=False).count(),
#             'tobe_billed': po_product_data.filter(billed=False).count()
#         }
#     except Exception as e:
#         return {
#             'tobe_shipped': 0,
#             'tobe_received': 0,
#             'tobe_invoiced': 0,
#             'tobe_billed': 0
#         }
#
#
# @register.simple_tag
# def checkSOPaymentStatus(so_id):
#     try:
#         invoice_status = InvoiceSO.objects.get(so__so_id=so_id).invoice.status
#     except Exception:
#         invoice_status = "DUE"
#     return invoice_status == "DUE"
#
#
# @register.simple_tag
# def getSOInvoiceData(so_id):
#     try:
#         invoice = InvoiceSO.objects.get(so__so_id=so_id).invoice
#         return {
#             'invoice_id': invoice.invoice_id,
#             'amount': round(invoice.amount, 2)
#         }
#     except Exception:
#         return {
#             'invoice_id': '',
#             'amount': 0.00
#         }
#
#
# @register.simple_tag
# def getSOQuantity(so_id, product_id):
#     try:
#         so_instance = SalesOrder.objects.get(id=so_id)
#         so_products = so_instance.so_instance.filter(product_id=product_id).aggregate(Sum('quantity'))
#         return so_products['quantity__sum']
#     except Exception:
#         return 0
#
#
# @register.simple_tag
# def getPOQuantity(po_id, product_id):
#     try:
#         po_instance = PurchaseOrder.objects.get(id=po_id)
#         po_products = po_instance.po_instance.filter(product_id=product_id).aggregate(Sum('quantity'))
#         return po_products['quantity__sum']
#     except Exception:
#         return 0
#
#
# @register.simple_tag
# def getBillInstance(po_id):
#     try:
#         po = PurchaseOrder.objects.get(po_id=po_id)
#         return po.bill_po.all().last().bill
#     except Exception:
#         return ''
#
#
# @register.simple_tag
# def get_user_ip(request):
#     try:
#         x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#         if x_forwarded_for:
#             ip = x_forwarded_for.split(',')[0]
#         else:
#             ip = request.META.get('REMOTE_ADDR')
#         return ip
#     except Exception as e:
#         return "127.0.0.1"
