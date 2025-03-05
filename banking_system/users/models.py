from decimal import Decimal
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import F

class UserAccount(AbstractUser):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    is_admin = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)

    def transfer_to_deposit(self, amount):
        amount = Decimal(amount)
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            self.deposit += amount
            self.save()
            return True
        return False

    def transfer_from_deposit(self, amount):
        amount = Decimal(amount)
        if amount > 0 and self.deposit >= amount:
            self.deposit -= amount
            self.balance += amount
            self.save()
            return True
        return False
    def __str__(self):
        return self.username

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    sender = models.ForeignKey('UserAccount', on_delete=models.CASCADE, related_name="sent_transactions")
    receiver = models.ForeignKey('UserAccount', on_delete=models.CASCADE, related_name="received_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.sender} -> {self.receiver} : {self.amount}"

    def complete_transaction(self):
        if self.status != 'pending':
            return

        if self.sender.balance < self.amount:
            self.status = 'failed'
            self.save(update_fields=['status'])
            raise ValidationError("Недостаточно средств для перевода!")

        with transaction.atomic():
            sender = UserAccount.objects.select_for_update().get(id=self.sender.id)
            receiver = UserAccount.objects.select_for_update().get(id=self.receiver.id)

            if sender.balance < self.amount:
                self.status = 'failed'
                self.save(update_fields=['status'])
                raise ValidationError("Недостаточно средств!")


            sender.balance = F('balance') - self.amount
            receiver.balance = F('balance') + self.amount
            sender.save(update_fields=['balance'])
            receiver.save(update_fields=['balance'])

            self.status = 'completed'
            self.save(update_fields=['status'])
