from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import ExpenseInfo
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum, Q
import matplotlib.pyplot as plt
from django.utils.decorators import sync_and_async_middleware


import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to prevent NSWindow error

# Define a function to generate the plot
def generate_plot(request):
    try:
        budget_total = ExpenseInfo.objects.filter(user_expense=request.user).aggregate(budget=Sum('cost', filter=Q(cost__gt=0)))
        expense_total = ExpenseInfo.objects.filter(user_expense=request.user).aggregate(expenses=Sum('cost', filter=Q(cost__lt=0)))
        fig, ax = plt.subplots()
        ax.bar(['Expenses', 'Budget'], [abs(expense_total['expenses']), budget_total['budget']], color=['red', 'green'])
        ax.set_title('Your total expenses vs total budget')
        plt.savefig('budget_app/static/budget_app/expense.jpg')
    except TypeError:
        print('No data.')
    except Exception as e:
        print(f"An error occurred: {e}")

# View for index page
def index(request):
    expense_items = ExpenseInfo.objects.filter(user_expense=request.user).order_by('-date_added')
    generate_plot(request)
    context = {'expense_items': expense_items}
    return render(request, 'budget_app/index.html', context=context)


# Define a function to generate the plot
# def generate_plot(request):
#     try:
#         budget_total = ExpenseInfo.objects.filter(user_expense=request.user).aggregate(budget=Sum('cost', filter=Q(cost__gt=0)))
#         expense_total = ExpenseInfo.objects.filter(user_expense=request.user).aggregate(expenses=Sum('cost', filter=Q(cost__lt=0)))
#         fig, ax = plt.subplots()
#         ax.bar(['Expenses', 'Budget'], [abs(expense_total['expenses']), budget_total['budget']], color=['red', 'green'])
#         ax.set_title('Your total expenses vs total budget')
#         plt.savefig('budget_app/static/budget_app/expense.jpg')
#     except TypeError:
#         print('No data.')

# View for index page
# def index(request):
#     expense_items = ExpenseInfo.objects.filter(user_expense=request.user).order_by('-date_added')
#     generate_plot(request)
#     context = {'expense_items': expense_items}
#     return render(request, 'budget_app/index.html', context=context)

# View for adding an item
def add_item(request):
    name = request.POST['expense_name']
    expense_cost = request.POST['cost']
    expense_date = request.POST['expense_date']
    ExpenseInfo.objects.create(expense_name=name, cost=expense_cost, date_added=expense_date, user_expense=request.user)
    generate_plot(request)
    return HttpResponseRedirect('app')

# View for user sign up
def sign_up(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect('app')
        else:
            for msg in form.error_messages:
                print(form.error_messages[msg])
    else:
        form = UserCreationForm()
    
    return render(request, 'budget_app/sign_up.html', {'form': form})

# View for user logout
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

# Apply sync_and_async_middleware decorator to ensure views run on the main thread
index = sync_and_async_middleware(index)
add_item = sync_and_async_middleware(add_item)
sign_up = sync_and_async_middleware(sign_up)
logout_view = sync_and_async_middleware(logout_view)

