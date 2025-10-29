from django.urls import path
from . import views

app_name = "banksystem"

urlpatterns = [
    # Accounts
    path("accounts/", views.account_list, name="account_list"),
    path("accounts/create/", views.account_create, name="account_create"),
    path("accounts/<int:pk>/edit/", views.account_update, name="account_update"),
    path("accounts/<int:pk>/delete/", views.account_delete, name="account_delete"),

    # Transactions
    path("transactions/", views.transaction_list, name="transaction_list"),
    path("transactions/create/", views.transaction_create, name="transaction_create"),
    path("transactions/<int:pk>/edit/", views.transaction_update, name="transaction_update"),
    path("transactions/<int:pk>/delete/", views.transaction_delete, name="transaction_delete"),
]
