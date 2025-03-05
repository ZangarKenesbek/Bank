from django.urls import path
from . import views
from .views import register_view, login_view, logout_view, user_account_view, transfer_balance_deposit
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("transfer_balance_deposit/", transfer_balance_deposit, name="transfer_balance_deposit"),
    path('', views.home, name='home'),
    path("transfer_deposit/", views.transfer_deposit, name="transfer_deposit"),
    path('transfer/', views.transfer_money, name='transfer'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('users/', views.user_list, name='user_list'),
    path('update_balance/<int:user_id>/', views.update_balance, name='update_balance'),
    path('delete_transaction/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path("profile/", views.profile, name="profile"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('account/', user_account_view, name='user_account'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),  # Новый путь

]
