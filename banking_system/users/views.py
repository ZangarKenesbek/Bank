from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F
from .models import Transaction, UserAccount
from django.contrib.auth import login, logout, authenticate
from .forms import UserRegistrationForm, UserLoginForm, TransferForm
from decimal import Decimal

@login_required
def transfer_balance_deposit(request):
    if request.method == "POST":
        user = request.user
        amount = request.POST.get("amount")
        direction = request.POST.get("direction")

        if not amount or not amount.isdigit():
            messages.error(request, "Введите корректную сумму.")
            return redirect("profile")

        amount = Decimal(amount)

        if direction == "to_deposit":
            if user.transfer_to_deposit(amount):
                messages.success(request, f"{amount} ₽ переведено на депозит.")
            else:
                messages.error(request, "Недостаточно средств на балансе.")

        elif direction == "from_deposit":
            if user.transfer_from_deposit(amount):
                messages.success(request, f"{amount} ₽ переведено на баланс.")
            else:
                messages.error(request, "Недостаточно средств на депозите.")

    return redirect("profile")

@login_required
def transfer_deposit(request):
    if request.method == "POST":
        user = request.user
        direction = request.POST.get("direction")
        amount = request.POST.get("amount")

        if not amount or not amount.isdigit():
            messages.error(request, "Введите корректную сумму.")
            return redirect("profile")

        amount = int(amount)

        if direction == "to_deposit":
            if user.balance >= amount:
                user.balance -= amount
                user.deposit += amount
                user.save()
                messages.success(request, f"{amount} ₸ переведено на депозит.")
            else:
                messages.error(request, "Недостаточно средств на балансе.")

        elif direction == "from_deposit":
            if user.deposit >= amount:
                user.deposit -= amount
                user.balance += amount
                user.save()
                messages.success(request, f"{amount} ₸ переведено на баланс.")
            else:
                messages.error(request, "Недостаточно средств на депозите.")

    return redirect("profile")
@login_required
def transfer_money(request):
    if request.method == "POST":
        form = TransferForm(request.POST, current_user=request.user)
        if form.is_valid():
            sender = request.user
            receiver = form.cleaned_data['receiver']
            amount = form.cleaned_data['amount']

            if sender.balance >= amount:
                transaction = Transaction.objects.create(
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    status="pending"
                )
                transaction.complete_transaction()
                messages.success(request, "Перевод успешно выполнен!")
                return redirect('profile')
            else:
                form.add_error(None, "Недостаточно средств")
    else:
        form = TransferForm(current_user=request.user)

    return render(request, 'users/transfer.html', {'form': form})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def transaction_history(request):
    user = request.user
    sent_transactions = user.sent_transactions.all().order_by('-timestamp')
    received_transactions = user.received_transactions.all().order_by('-timestamp')

    return render(request, 'users/transaction_history.html', {
        'sent_transactions': sent_transactions,
        'received_transactions': received_transactions
    })

@login_required
def update_balance(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, "Доступ запрещён!")
        return redirect("home")

    user = get_object_or_404(UserAccount, id=user_id)

    if request.method == "POST":
        new_balance = request.POST.get("balance")
        try:
            user.balance = float(new_balance)
            user.save()
            messages.success(request, f"Баланс {user.username} успешно обновлён!")
        except ValueError:
            messages.error(request, "Некорректное значение!")

    return redirect("home")

@login_required
def delete_transaction(request, transaction_id):
    if not request.user.is_superuser:
        messages.error(request, "Доступ запрещён!")
        return redirect("home")

    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.delete()
    messages.success(request, "Транзакция успешно удалена!")
    return redirect("transaction_history")

@login_required
def user_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Доступ запрещён!")
        return redirect("home")

    users = UserAccount.objects.all().only('id', 'username', 'email')  # НЕ передаем баланс
    return render(request, 'users/user_list.html', {'users': users})

@login_required
def profile(request):
    user = request.user
    sent_transactions = user.sent_transactions.all().order_by('-timestamp')
    received_transactions = user.received_transactions.all().order_by('-timestamp')

    return render(request, 'users/profile.html', {
        'user': user,
        'sent_transactions': sent_transactions,
        'received_transactions': received_transactions
    })

def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect("profile")
    else:
        form = UserRegistrationForm()
    return render(request, "registration/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Вы вошли в систему!")
            return redirect("profile")
    else:
        form = UserLoginForm()
    return render(request, "registration/login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.success(request, "Вы вышли из системы!")
    return redirect("login")

@login_required
def user_account_view(request):
    return render(request, 'users/user_account.html', {'user': request.user})
def home(request):
    return render(request, 'users/base.html')
